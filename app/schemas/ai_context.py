#app/schemas/ai_context.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class ProjectAIContext(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[str] = None      # ISO-строка
    priority: Optional[int] = None
    participants: List[Dict[str, Any]] = []
    tags: List[str] = []
    linked_repo: Optional[str] = None
    parent_project_id: Optional[int] = None
    custom_fields: Dict[str, Any] = {}
    is_overdue: Optional[bool] = None
    is_deleted: Optional[bool] = None
    ai_notes: Optional[str] = None
    external_id: Optional[str] = None
    subscription_level: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TaskAIContext(BaseModel):
    id: int
    project_id: int
    parent_task_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    deadline: Optional[str] = None
    assignees: List[Dict[str, Any]] = []
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_overdue: Optional[bool] = None
    is_deleted: Optional[bool] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    is_favorite: Optional[bool] = None
    ai_notes: Optional[str] = None
    external_id: Optional[str] = None
    reviewed: Optional[bool] = None

class DevLogAIContext(BaseModel):
    id: int
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    entry_type: str
    content: str
    author: str
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    is_deleted: Optional[bool] = None
    edited_by: Optional[str] = None
    edit_reason: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    ai_notes: Optional[str] = None

class UserAIContext(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    roles: List[str] = []
    is_superuser: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[str] = None
    avatar_url: Optional[str] = None

class PluginAIContext(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    config_json: Dict[str, Any] = {}
    is_active: Optional[bool] = None
    version: Optional[str] = None
    author: Optional[str] = None
    subscription_level: Optional[str] = None
    is_private: Optional[bool] = None
    ui_component: Optional[str] = None
    tags: List[str] = []
