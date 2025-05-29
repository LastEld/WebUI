#app/models/team.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Boolean
from app.models.base import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)

    # Optional: Who created/owns the team
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=False, onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"
