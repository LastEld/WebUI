#app/models/jarvis.py
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, func, Boolean
from app.models.base import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # Время создания сообщения (для совместимости с SQLite/Postgres)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.datetime.utcnow, nullable=False)

    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)

    # Универсальные метаданные: action, source, reference, статус AI и т.д.
    metadata_ = Column("metadata", JSON, nullable=True)  # Не конфликтует с SQLAlchemy

    # --- Дополнительно ---
    author = Column(String(64), nullable=True)                 # Автор сообщения (user/email/id)
    is_deleted = Column(Boolean, default=False, nullable=False) # Soft-delete (например, для модерации)
    ai_notes = Column(Text, nullable=True)                     # AI summary/explanation
    attachments = Column(JSON, default=list)                   # [{ "url": "...", "type": "...", "name": "..." }]

    def __repr__(self):
        return (
            f"<ChatMessage(id={self.id}, project_id={self.project_id}, role='{self.role}', timestamp='{self.timestamp}')>"
        )

    def to_dict(self):
        """Конвертирует объект в словарь для чата (можно расширить под свои нужды)."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata_,
            "author": self.author,
            "ai_notes": self.ai_notes,
            "attachments": self.attachments,
            "is_deleted": self.is_deleted,
        }
