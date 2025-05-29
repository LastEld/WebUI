#app/models/task.py
import datetime
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, JSON, Boolean, Index
)
from sqlalchemy.orm import relationship
from app.models.base import Base

class Task(Base):
    __tablename__ = "tasks"  # множина, для consistency

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)

    title = Column(String(160), nullable=False)
    description = Column(String(2000), default="")

    status = Column(String(24), default="todo", index=True)  # індекс для швидкої фільтрації
    priority = Column(Integer, default=3, index=True)        # індекс для Kanban/AI/сортування
    deadline = Column(Date, nullable=True, index=True)       # індекс для пошуку по даті

    assignees = Column(JSON, nullable=True, default=list)    # [{user_id, name, role}]
    tags = Column(JSON, default=list)                        # ["bug", "feature"]

    custom_fields = Column(JSON, default=dict)                # Кастомные поля

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, onupdate=datetime.datetime.utcnow)

    is_deleted = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)

    ai_notes = Column(String(2000), nullable=True)
    attachments = Column(JSON, default=list)
    external_id = Column(String(64), nullable=True, index=True)  # для інтеграцій, індекс!
    reviewed = Column(Boolean, default=False, nullable=False)

    # Сабтаски (self-referencing)
    subtasks = relationship("Task", backref="parent", remote_side=[id], cascade="all, delete")

    __table_args__ = (
        Index("ix_tasks_deadline", "deadline"),
        Index("ix_tasks_external_id", "external_id"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_priority", "priority"),
    )

    def __repr__(self):
        return (
            f"<Task(id={self.id}, title='{self.title}', status={self.status}, "
            f"project_id={self.project_id}, priority={self.priority}, "
            f"deadline={self.deadline}, assignees={self.assignees})>"
        )
