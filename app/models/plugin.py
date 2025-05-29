#app/models/plugin.py
from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.models.base import Base

class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)

    config_json = Column(JSON, nullable=False, default=dict)   # Основная конфигурация (любая структура)
    is_active = Column(Boolean, default=True, nullable=False)

    # --- Дополнительно для масштабируемости/Pro ---
    version = Column(String(32), nullable=True)                # Версия плагина, например "1.0.3"
    author = Column(String(128), nullable=True)                # Имя или e-mail автора
    subscription_level = Column(String(32), nullable=True)     # "Free", "Pro", "VIP" (для платных фич)
    is_private = Column(Boolean, default=False, nullable=False) # Приватный/Публичный
    ui_component = Column(String(64), nullable=True)           # Имя компонента фронта (например, "KanbanBoard")

    # Можно добавить поле tags для быстрого поиска/фильтрации
    tags = Column(JSON, default=list)                          # ["calendar", "kanban"]

    def __repr__(self):
        return f"<Plugin(id={self.id}, name='{self.name}', version={self.version}, active={self.is_active})>"
