#app/schemas/participant.py
from pydantic import BaseModel, Field
from typing import Optional

class Participant(BaseModel):
    name: str = Field(..., example="Jane Smith")
    email: Optional[str] = Field(None, example="jane@company.com")
    role: Optional[str] = Field(None, example="manager")  # manager, dev, reviewer и т.д.
    avatar_url: Optional[str] = Field(None, example="https://cdn.example.com/avatars/jane.jpg")
    is_team: Optional[bool] = Field(False, description="Участник — это команда?")
    is_active: Optional[bool] = Field(True, description="Активен ли участник")
    joined_at: Optional[str] = Field(None, example="2024-05-20T10:00:00Z")

    class Config:
        orm_mode = True

