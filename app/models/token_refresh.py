#app/models/token_refresh.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.models.base import Base

class TokenRefresh(Base):
    __tablename__ = "token_refresh"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    refresh_token = Column(String(256), unique=True, nullable=False, index=True)
    user_agent = Column(String(256), nullable=True)    # Для аудита: из какого браузера/устройства
    ip_address = Column(String(64), nullable=True)     # Для аудита: откуда был выдан токен
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)       # Можно реализовать автоудаление по сроку

    def __repr__(self):
        return f"<TokenRefresh(id={self.id}, user_id={self.user_id}, is_active={self.is_active}, expires_at={self.expires_at})>"
