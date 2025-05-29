#app/schemas/auth.py
from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = Field("bearer", example="bearer")
    expires_in: Optional[int] = Field(None, description="Seconds until token expiration")

class TokenPayload(BaseModel):
    sub: Optional[str] = None  # subject: usually user id or username
    exp: Optional[int] = None  # expiration time as timestamp

class LoginRequest(BaseModel):
    username: str = Field(..., example="john_doe")
    password: str = Field(..., example="StrongPassw0rd!")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = Field("bearer", example="bearer")
    expires_in: int = Field(..., description="Seconds until token expiration")
    refresh_token: Optional[str] = None
