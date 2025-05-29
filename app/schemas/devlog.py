#app/schemas/devlog.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.attachment import Attachment

class DevLogBase(BaseModel):
    project_id: Optional[int] = Field(None, example=1)
    task_id: Optional[int] = Field(None, example=2)
    entry_type: str = Field("note", example="note")  # note, action, decision, meeting
    content: str = Field(..., example="Implemented project structure.")
    author: str = Field(..., example="John Doe")
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    attachments: List[Attachment] = Field(default_factory=list)
    edited_by: Optional[str] = Field(None, example="Jane Doe")
    edit_reason: Optional[str] = Field(None, example="Fixed typo")
    ai_notes: Optional[str] = Field(None, example="AI summary for this entry.")
    # Можно добавить поле status (например, approved/under_review), если нужно workflow

class DevLogCreate(DevLogBase):
    pass

class DevLogUpdate(BaseModel):
    project_id: Optional[int]
    task_id: Optional[int]
    entry_type: Optional[str]
    content: Optional[str]
    author: Optional[str]
    tags: Optional[List[str]]
    custom_fields: Optional[Dict[str, Any]]
    attachments: Optional[List[Attachment]]
    edited_by: Optional[str]
    edit_reason: Optional[str]
    ai_notes: Optional[str]

class DevLogShort(BaseModel):
    id: int
    entry_type: str
    content: str
    author: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class DevLogRead(DevLogBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

    class Config:
        orm_mode = True
