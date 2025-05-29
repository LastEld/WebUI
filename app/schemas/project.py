#app/schemas/project.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from app.schemas.participant import Participant
from app.schemas.attachment import Attachment

class ProjectBase(BaseModel):
    name: str = Field(..., example="My Project")
    description: Optional[str] = Field("", example="Project description")
    status: Optional[str] = Field("active", example="active")  # active, archived, done
    deadline: Optional[date] = Field(None, example="2024-12-31")
    priority: Optional[int] = Field(3, ge=1, le=5, example=3)
    tags: List[str] = Field(default_factory=list, example=["python", "startup"])
    linked_repo: Optional[str] = Field(None, example="https://github.com/username/repo")
    color: Optional[str] = Field(None, example="#FFAA00")
    participants: List[Participant] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    parent_project_id: Optional[int] = Field(None, example=123)
    attachments: List[Attachment] = Field(default_factory=list)
    is_favorite: Optional[bool] = Field(False, description="Is project in favorites?")
    ai_notes: Optional[str] = Field(None, example="AI project summary or prompt")
    external_id: Optional[str] = Field(None, example="PRJ-4567")
    subscription_level: Optional[str] = Field(None, example="Pro")  # Free, Pro, VIP

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]
    deadline: Optional[date]
    priority: Optional[int]
    tags: Optional[List[str]]
    linked_repo: Optional[str]
    color: Optional[str]
    participants: Optional[List[Participant]]
    custom_fields: Optional[Dict[str, Any]]
    parent_project_id: Optional[int]
    attachments: Optional[List[Attachment]]
    is_favorite: Optional[bool]
    ai_notes: Optional[str]
    external_id: Optional[str]
    subscription_level: Optional[str]

class ProjectShort(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True
