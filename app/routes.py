from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.rag import retrieve_relevant_context
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# How many messages to keep in context window
CONTEXT_WINDOW_SIZE = 10


# -----------------------------------------------
# HELPER - Call the AI brain (Groq/LLM)
# -----------------------------------------------
def get_ai_reply(messages):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service is temporarily unavailable. Please try again. Error: {str(e)}"
        )


# -----------------------------------------------
# HELPER - Build sliding window of messages
# Only keeps last CONTEXT_WINDOW_SIZE messages
# -----------------------------------------------
def build_context_window(history):
    # Take only the last N messages
    recent_messages = history[-CONTEXT_WINDOW_SIZE:]
    return [{"role": m.role, "content": m.content} for m in recent_messages]


# -----------------------------------------------
# CREATE USER
# POST /users
# -----------------------------------------------
@router.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(models.User).filter(
            models.User.email == user.email
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        new_user = models.User(name=user.name, email=user.email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )


# -----------------------------------------------
# START NEW CONVERSATION
# POST /conversations
# -----------------------------------------------
@router.post("/conversations", response_model=schemas.ConversationResponse)
def create_conversation(data: schemas.ConversationCreate, db: Session = Depends(get_db)):
    try:
        # Check user exists
        user = db.query(models.User).filter(
            models.User.id == data.user_id
        ).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Create conversation
        conversation = models.Conversation(
            user_id=data.user_id,
            title=data.title or data.first_message[:50]
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Save user message
        user_message = models.Message(
            conversation_id=conversation.id,
            role="user",
            content=data.first_message
        )
        db.add(user_message)
        db.commit()

        # Call AI
        ai_reply = get_ai_reply([
            {"role": "user", "content": data.first_message}
        ])

        # Save AI reply
        assistant_message = models.Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_reply
        )
        db.add(assistant_message)
        db.commit()

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create conversation: {str(e)}"
        )


# -----------------------------------------------
# LIST ALL CONVERSATIONS FOR A USER
# GET /conversations?user_id=1
# -----------------------------------------------
@router.get("/conversations", response_model=list[schemas.ConversationResponse])
def list_conversations(user_id: int, db: Session = Depends(get_db)):
    try:
        conversations = db.query(models.Conversation).filter(
            models.Conversation.user_id == user_id
        ).all()
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversations: {str(e)}"
        )


# -----------------------------------------------
# GET FULL CONVERSATION WITH MESSAGES
# GET /conversations/{id}
# -----------------------------------------------
@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationDetailResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    try:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation: {str(e)}"
        )


# -----------------------------------------------
# ADD NEW MESSAGE TO EXISTING CONVERSATION
# POST /conversations/{id}/messages
# -----------------------------------------------
@router.post("/conversations/{conversation_id}/messages", response_model=schemas.MessageResponse)
def add_message(conversation_id: int, data: schemas.MessageCreate, db: Session = Depends(get_db)):
    try:
        # Check conversation exists
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        # Get conversation history
        history = db.query(models.Message).filter(
            models.Message.conversation_id == conversation_id
        ).all()

        # Apply sliding window - only last 10 messages
        messages = build_context_window(history)
        messages.append({"role": "user", "content": data.user_message})

        # Save user message
        user_message = models.Message(
            conversation_id=conversation_id,
            role="user",
            content=data.user_message
        )
        db.add(user_message)
        db.commit()

        # Call AI with windowed history
        ai_reply = get_ai_reply(messages)

        # Save AI reply
        assistant_message = models.Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_reply
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        return assistant_message

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


# -----------------------------------------------
# DELETE CONVERSATION
# DELETE /conversations/{id}
# -----------------------------------------------
@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    try:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        # Delete all messages first
        db.query(models.Message).filter(
            models.Message.conversation_id == conversation_id
        ).delete()

        # Delete conversation
        db.delete(conversation)
        db.commit()

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete conversation: {str(e)}"
        )


# -----------------------------------------------
# RAG CHAT - Chat grounded in documents
# POST /conversations/{id}/rag-messages
# -----------------------------------------------
@router.post("/conversations/{conversation_id}/rag-messages", response_model=schemas.MessageResponse)
def add_rag_message(conversation_id: int, data: schemas.RAGMessageCreate, db: Session = Depends(get_db)):
    try:
        # Check conversation exists
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        # Get relevant context from fake knowledge base
        context = retrieve_relevant_context(data.user_message)

        # Build system prompt with context
        if context and data.use_rag:
            system_prompt = f"""You are a helpful assistant.
Use the following context to answer the user's question.
Only use the context provided. If the answer is not in the context, say you don't know.

Context:
{context}"""
        else:
            system_prompt = "You are a helpful assistant."

        # Get conversation history with sliding window
        history = db.query(models.Message).filter(
            models.Message.conversation_id == conversation_id
        ).all()

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages += build_context_window(history)
        messages.append({"role": "user", "content": data.user_message})

        # Save user message
        user_message = models.Message(
            conversation_id=conversation_id,
            role="user",
            content=data.user_message
        )
        db.add(user_message)
        db.commit()

        # Call AI
        ai_reply = get_ai_reply(messages)

        # Save AI reply
        assistant_message = models.Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_reply
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        return assistant_message

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process RAG message: {str(e)}"
        )
