#app/schemas/attachment.py
from pydantic import BaseModel, Field
from typing import Optional

class Attachment(BaseModel):
    url: str = Field(..., example="https://cdn.example.com/files/doc1.pdf")
    type: Optional[str] = Field(None, example="pdf")  # pdf, image/png, screenshot, txt и т.д.
    name: Optional[str] = Field(None, example="Project Spec")
    size: Optional[int] = Field(None, example=102400, description="Размер файла в байтах")
    uploaded_by: Optional[str] = Field(None, example="john@company.com")
    uploaded_at: Optional[str] = Field(None, example="2024-05-29T15:20:00Z")
    description: Optional[str] = Field(None, example="Документация к проекту")
    preview_url: Optional[str] = Field(None, example="https://cdn.example.com/previews/doc1.png")
    # Можешь добавить thumbnail_url, external_id и т.д. при необходимости

    class Config:
        orm_mode = True
