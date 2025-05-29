#app/schemas/token_refresh.py
from pydantic import BaseModel, Field

class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = Field("bearer", example="bearer")
    expires_in: int = Field(..., description="Seconds until token expiration")
