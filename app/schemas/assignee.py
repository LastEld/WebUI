#app/schemas/assignee.py
from pydantic import BaseModel, Field
from typing import Optional

class Assignee(BaseModel):
    user_id: Optional[int] = Field(None, example=17)
    name: str = Field(..., example="John Doe")
    email: Optional[str] = Field(None, example="john@company.com")
    role: Optional[str] = Field(None, example="developer")  # developer, manager, reviewer и т.д.
    avatar_url: Optional[str] = Field(None, example="https://example.com/avatar.jpg")
    is_active: Optional[bool] = Field(True, description="Включён ли пользователь (для фильтрации, AI)")

    class Config:
        orm_mode = True
