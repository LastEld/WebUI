#app/schemas/plugin.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class PluginBase(BaseModel):
    name: str = Field(..., example="kanban")
    description: Optional[str] = Field(None, example="Task Kanban board")
    config_json: Dict[str, Any] = Field(default_factory=dict, example={"columns": ["To Do", "In Progress", "Done"]})
    is_active: Optional[bool] = Field(True, description="Is plugin enabled?")
    version: Optional[str] = Field(None, example="1.0.0")
    author: Optional[str] = Field(None, example="lasteld@devos.io")
    subscription_level: Optional[str] = Field(None, example="Pro")  # Free, Pro, VIP
    is_private: Optional[bool] = Field(False, description="Is plugin private?")
    ui_component: Optional[str] = Field(None, example="KanbanBoard")
    tags: List[str] = Field(default_factory=list, example=["kanban", "board"])

class PluginCreate(PluginBase):
    pass

class PluginUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    config_json: Optional[Dict[str, Any]]
    is_active: Optional[bool]
    version: Optional[str]
    author: Optional[str]
    subscription_level: Optional[str]
    is_private: Optional[bool]
    ui_component: Optional[str]
    tags: Optional[List[str]]

class PluginShort(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        orm_mode = True

class PluginRead(PluginBase):
    id: int

    class Config:
        orm_mode = True
