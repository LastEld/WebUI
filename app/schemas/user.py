#app/schemas/user.py
from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., example="john_doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    full_name: Optional[str] = Field(None, example="John Doe")
    is_active: bool = Field(True, description="User is active")
    is_superuser: bool = Field(False, description="Admin privileges")
    roles: List[str] = Field(default_factory=list, example=["developer", "manager"])

class UserCreate(UserBase):
    password: constr(min_length=8) = Field(..., example="StrongPassw0rd!")

class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    full_name: Optional[str]
    is_active: Optional[bool]
    roles: Optional[List[str]]

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
