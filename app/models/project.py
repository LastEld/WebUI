#app/models/project.py
import datetime
from app.models.base import Base
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Text, JSON, ForeignKey, Boolean, Index
)

class Project(Base):
    __tablename__ = "projects"  # рекомендується множина!

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active", index=True)
    deadline = Column(Date, nullable=True, index=True)  # Індекс по дедлайну
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, onupdate=datetime.datetime.utcnow)

    participants = Column(JSON, nullable=True, default=list)    # [{name, email, role}]
    tags = Column(JSON, nullable=True, default=list)            # ["python", "startup"]
    custom_fields = Column(JSON, default=dict)                  # Додаткові поля

    priority = Column(Integer, default=3)
    linked_repo = Column(String(256), nullable=True)
    color = Column(String(7), nullable=True)

    # === Нові поля ===
    parent_project_id = Column(Integer, ForeignKey('projects.id', ondelete="CASCADE"), nullable=True)  # Каскадне видалення підпроєктів
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)     # Власник/автор проекту
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)       # Якщо є модель Team/teams

    is_deleted = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    ai_notes = Column(Text, nullable=True)
    attachments = Column(JSON, default=list)

    external_id = Column(String(64), nullable=True, index=True)   # Для інтеграцій (та індекс для швидкого пошуку)
    subscription_level = Column(String(32), nullable=True)

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}', priority={self.priority})>"

    # Додаткові індекси (deadline, external_id)
    __table_args__ = (
        Index("ix_projects_deadline", "deadline"),
        Index("ix_projects_external_id", "external_id"),
    )

def init_db(engine):
    Base.metadata.create_all(engine)
