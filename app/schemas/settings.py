#app/schemas/settings.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class SettingBase(BaseModel):
    key: str = Field(..., example="theme")
    value: Any = Field(..., example="dark")
    description: Optional[str] = Field(None, example="UI theme for the app")
    is_active: Optional[bool] = True

class SettingCreate(SettingBase):
    user_id: Optional[int] = None

class SettingUpdate(BaseModel):
    value: Optional[Any]
    description: Optional[str]
    is_active: Optional[bool]

class SettingRead(SettingBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
