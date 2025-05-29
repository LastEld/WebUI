#app/schemas/task.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from app.schemas.assignee import Assignee
from app.schemas.attachment import Attachment

class TaskBase(BaseModel):
    title: str = Field(..., example="Implement login page")
    description: Optional[str] = Field("", example="Detailed description")
    status: Optional[str] = Field("todo", example="todo")  # todo, in progress, done, blocked, cancelled
    priority: Optional[int] = Field(3, ge=1, le=5, example=3)
    deadline: Optional[date] = Field(None, example="2024-12-31")
    assignees: List[Assignee] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    project_id: int = Field(..., example=1)
    parent_task_id: Optional[int] = Field(None, example=2)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    attachments: List[Attachment] = Field(default_factory=list)
    is_favorite: Optional[bool] = Field(False, description="Is task a favorite for user?")
    ai_notes: Optional[str] = Field(None, example="AI suggestions for this task.")
    external_id: Optional[str] = Field(None, example="TASK-1001")
    reviewed: Optional[bool] = Field(False, description="Has the task been reviewed by QA/manager?")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    priority: Optional[int]
    deadline: Optional[date]
    assignees: Optional[List[Assignee]]
    tags: Optional[List[str]]
    project_id: Optional[int]
    parent_task_id: Optional[int]
    custom_fields: Optional[Dict[str, Any]]
    attachments: Optional[List[Attachment]]
    is_favorite: Optional[bool]
    ai_notes: Optional[str]
    external_id: Optional[str]
    reviewed: Optional[bool]

class TaskShort(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True

class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True
