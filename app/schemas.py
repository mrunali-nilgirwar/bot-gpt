from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- MESSAGE SCHEMAS ---
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- CONVERSATION SCHEMAS ---
class ConversationCreate(BaseModel):
    user_id: int
    first_message: str
    title: Optional[str] = "New Conversation"

class MessageCreate(BaseModel):
    user_message: str

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True

# --- RAG SCHEMAS ---
class RAGMessageCreate(BaseModel):
    user_message: str
    use_rag: bool = True