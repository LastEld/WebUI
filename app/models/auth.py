#app/models/auth.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.models.base import Base

class AccessToken(Base):
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    user_agent = Column(String(256), nullable=True)
    ip_address = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<AccessToken(id={self.id}, user_id={self.user_id}, is_active={self.is_active}, revoked={self.revoked})>"
