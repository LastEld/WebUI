#app/schemas/jarvis.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.attachment import Attachment

class ChatMessageBase(BaseModel):
    project_id: int = Field(..., example=1)
    role: str = Field(..., example="user")   # "user", "assistant", "system"
    content: str = Field(..., example="Let's plan our next sprint!")
    timestamp: Optional[datetime] = Field(None, example="2024-06-01T15:00:00Z")
    metadata: Optional[Dict[str, Any]] = Field(None, example={"action": "ref", "source": "gpt"})
    author: Optional[str] = Field(None, example="john.doe")
    ai_notes: Optional[str] = Field(None, example="AI summary of the conversation.")
    attachments: List[Attachment] = Field(default_factory=list)
    is_deleted: Optional[bool] = Field(False, description="Soft-delete flag")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageUpdate(BaseModel):
    content: Optional[str]
    metadata: Optional[Dict[str, Any]]
    author: Optional[str]
    ai_notes: Optional[str]
    attachments: Optional[List[Attachment]]
    is_deleted: Optional[bool]

class ChatMessageRead(ChatMessageBase):
    id: int

    class Config:
        orm_mode = True

class ChatMessageShort(BaseModel):
    id: int
    role: str
    content: str
    timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True
