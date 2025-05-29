#app/models/ai_context.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from app.models.base import Base

class AIContext(Base):
    __tablename__ = "ai_contexts"

    id = Column(Integer, primary_key=True, index=True)
    object_type = Column(String(32), nullable=False)  # "project", "task", "devlog", "user", "plugin" і т.д.
    object_id = Column(Integer, nullable=False)       # id зв'язаної сутності
    context_data = Column(JSON, nullable=False)       # готовий контекст (структура залежить від object_type)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(128), nullable=True)   # хто згенерував (user, system, AI)
    request_id = Column(String(64), nullable=True)    # для трекінгу запитів
    notes = Column(String(512), nullable=True)        # коментарі
    is_deleted = Column(Boolean, default=False, nullable=False)  # soft-delete

    def __repr__(self):
        return f"<AIContext(id={self.id}, object_type='{self.object_type}', object_id={self.object_id})>"
