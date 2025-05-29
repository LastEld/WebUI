#app/schemas/team.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TeamBase(BaseModel):
    name: str = Field(..., example="Dev Team")
    description: Optional[str] = Field("", example="Development department")

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

class TeamRead(TeamBase):
    id: int
    owner_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        orm_mode = True
