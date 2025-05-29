#app/schemas/response.py
from pydantic import BaseModel, Field
from typing import Any, Optional

class ErrorDetail(BaseModel):
    code: str = Field(..., example="validation_error")
    message: str = Field(..., example="Field X is required.")
    details: Optional[Any] = Field(None, example={"field": "username"})

class ErrorResponse(BaseModel):
    error: ErrorDetail

class SuccessResponse(BaseModel):
    result: Any
    detail: Optional[str] = Field(None, example="Operation successful")

class ListResponse(BaseModel):
    results: Any  # Обычно List[SomeSchema], но можно оставить Any для универсальности
    total_count: Optional[int] = None
    detail: Optional[str] = None

class SimpleMessage(BaseModel):
    message: str = Field(..., example="Action completed successfully")
