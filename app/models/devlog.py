#app/models/devlog.py


from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Index
)
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base

class DevLogEntry(Base):
    __tablename__ = "devlog_entries"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)

    entry_type = Column(String(24), nullable=False, default="note")  # "note", "action", "decision", "meeting"
    content = Column(String(5000), nullable=False)
    author = Column(String(64), nullable=False)
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)

    # Аудит
    edited_by = Column(String(64), nullable=True)
    edit_reason = Column(String(256), nullable=True)

    # Вложения (список файлов/ссылок)
    attachments = Column(JSON, default=list)

    # AI-примечания
    ai_notes = Column(String(2000), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, onupdate=datetime.datetime.utcnow)

    is_deleted = Column(Boolean, default=False, nullable=False)

    # ORM-связи
    project = relationship("Project", backref="devlog_entries")
    task = relationship("Task", backref="devlog_entries")

    # Доданий індекс по created_at:
    __table_args__ = (
        Index("ix_devlog_entries_created_at", "created_at"),
    )

    def __repr__(self):
        return (
            f"<DevLogEntry(id={self.id}, type={self.entry_type}, "
            f"project_id={self.project_id}, task_id={self.task_id}, "
            f"author='{self.author}')>"
        )
