#app/models/template.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from app.models.base import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(32), nullable=True, default="1.0.0")
    author = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    tags = Column(JSON, default=list, nullable=False)  # list of strings, e.g. ["freelance", "startup"]
    structure = Column(JSON, nullable=False)  # основной объект — JSON со структурой проекта (плагины, задачи, настройки)
    ai_notes = Column(Text, nullable=True)
    subscription_level = Column(String(32), nullable=True)  # например: Free, Pro, VIP
    is_private = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', version='{self.version}', active={self.is_active})>"
