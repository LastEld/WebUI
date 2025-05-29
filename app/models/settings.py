#app/models/settings.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey
from app.models.base import Base

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), unique=True, nullable=False, index=True)    # Например, "theme", "ai.max_tokens"
    value = Column(JSON, nullable=False)                                  # Можно хранить любое значение
    description = Column(String(512), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)      # NULL = глобальная настройка
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Setting(key='{self.key}', value={self.value}, user_id={self.user_id})>"
