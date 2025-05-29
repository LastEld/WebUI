from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.plugin import PluginShort

class TemplateBase(BaseModel):
    name: str = Field(..., example="Freelancer Project Template")
    description: Optional[str] = Field(None, example="A template suited for freelance projects")
    version: Optional[str] = Field("1.0.0", example="1.0.0")
    author: Optional[str] = Field(None, example="lasteld@devos.io")
    created_at: Optional[datetime] = Field(None, example="2024-05-29T12:00:00Z")
    updated_at: Optional[datetime] = Field(None, example="2024-05-29T12:00:00Z")
    is_active: Optional[bool] = Field(True, description="Is this template active and available for use")
    tags: List[str] = Field(default_factory=list, example=["freelance", "simple", "startup"])

    # Основной объект шаблона — структура проекта с плагинами и настройками
    structure: Dict[str, Any] = Field(..., example={
        "plugins": [
            {"name": "kanban", "config": {"columns": ["To Do", "In Progress", "Done"]}},
            {"name": "timer", "config": {"default_duration": 25}}
        ],
        "default_tasks": [
            {"title": "Initial meeting", "status": "todo", "priority": 3}
        ],
        "settings": {
            "default_priority": 3,
            "allow_subtasks": True
        }
    })

    # Опциональные доп. поля для AI/Marketplace/Расширений
    ai_notes: Optional[str] = Field(None, example="This template works best for small teams.")
    subscription_level: Optional[str] = Field(None, example="Pro")
    is_private: Optional[bool] = Field(False, description="Is template private (only for the author)?")

    @validator('version')
    def version_must_be_semver(cls, v):
        if v is None:
            return v
        import re
        semver_regex = r'^\d+\.\d+\.\d+$'
        if not re.match(semver_regex, v):
            raise ValueError('Version must follow semantic versioning (e.g., 1.0.0)')
        return v

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    version: Optional[str]
    is_active: Optional[bool]
    tags: Optional[List[str]]
    structure: Optional[Dict[str, Any]]
    ai_notes: Optional[str]
    subscription_level: Optional[str]
    is_private: Optional[bool]

class TemplateShort(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        orm_mode = True

class TemplateRead(TemplateBase):
    id: int

    class Config:
        orm_mode = True
