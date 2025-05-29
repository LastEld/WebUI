#app/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=True)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    roles = Column(JSON, default=list, nullable=False)  # ["developer", "manager", ...]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    avatar_url = Column(String(255), nullable=True)

    # Дополнительные поля можно добавить по мере роста: настройки, Telegram, Stripe, и т.д.

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', roles={self.roles})>"
