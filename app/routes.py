from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------------------------
# HELPER FUNCTION - Call the AI brain (Groq/LLM)
# -----------------------------------------------
def get_ai_reply(messages):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content


# -----------------------------------------------
# CREATE USER
# POST /users
# -----------------------------------------------
@router.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -----------------------------------------------
# START NEW CONVERSATION
# POST /conversations
# -----------------------------------------------
@router.post("/conversations", response_model=schemas.ConversationResponse)
def create_conversation(data: schemas.ConversationCreate, db: Session = Depends(get_db)):
    # Check user exists
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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

    # Call AI and get reply
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


# -----------------------------------------------
# LIST ALL CONVERSATIONS FOR A USER
# GET /conversations?user_id=1
# -----------------------------------------------
@router.get("/conversations", response_model=list[schemas.ConversationResponse])
def list_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id
    ).all()
    return conversations


# -----------------------------------------------
# GET FULL CONVERSATION WITH MESSAGES
# GET /conversations/{id}
# -----------------------------------------------
@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationDetailResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


# -----------------------------------------------
# ADD NEW MESSAGE TO EXISTING CONVERSATION
# POST /conversations/{id}/messages
# -----------------------------------------------
@router.post("/conversations/{conversation_id}/messages", response_model=schemas.MessageResponse)
def add_message(conversation_id: int, data: schemas.MessageCreate, db: Session = Depends(get_db)):
    # Check conversation exists
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get full conversation history
    history = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).all()

    # Build message history to send to AI
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": data.user_message})

    # Save user message
    user_message = models.Message(
        conversation_id=conversation_id,
        role="user",
        content=data.user_message
    )
    db.add(user_message)
    db.commit()

    # Call AI with full history
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


# -----------------------------------------------
# DELETE CONVERSATION
# DELETE /conversations/{id}
# -----------------------------------------------
@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete all messages first
    db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).delete()

    # Delete conversation
    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted successfully"}
