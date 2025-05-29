#app/crud/settings.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.settings import Setting
from app.core.exceptions import ProjectValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime

def create_setting(db: Session, data: dict) -> Setting:
    if db.query(Setting).filter(Setting.key == data["key"], Setting.user_id == data.get("user_id")).first():
        raise ProjectValidationError("Setting with this key already exists for this user.")
    setting = Setting(
        key=data["key"],
        value=data["value"],
        description=data.get("description"),
        user_id=data.get("user_id"),
        is_active=data.get("is_active", True)
    )
    db.add(setting)
    try:
        db.commit()
        db.refresh(setting)
        return setting
    except IntegrityError:
        db.rollback()
        raise ProjectValidationError("Setting already exists.")
    except Exception:
        db.rollback()
        raise

def get_setting(db: Session, key: str, user_id: Optional[int] = None) -> Optional[Setting]:
    query = db.query(Setting).filter(Setting.key == key)
    if user_id is not None:
        query = query.filter(Setting.user_id == user_id)
    else:
        query = query.filter(Setting.user_id == None)
    return query.first()

def update_setting(db: Session, setting_id: int, data: dict) -> Setting:
    setting = db.query(Setting).filter(Setting.id == setting_id).first()
    if not setting:
        raise ProjectValidationError("Setting not found.")
    for field in ["value", "description", "is_active"]:
        if field in data:
            setattr(setting, field, data[field])
    setting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(setting)
    return setting

def delete_setting(db: Session, setting_id: int) -> bool:
    setting = db.query(Setting).filter(Setting.id == setting_id).first()
    if not setting:
        raise ProjectValidationError("Setting not found.")
    db.delete(setting)
    db.commit()
    return True

def get_all_settings(db: Session, user_id: Optional[int] = None) -> List[Setting]:
    query = db.query(Setting)
    if user_id is not None:
        query = query.filter(Setting.user_id == user_id)
    return query.order_by(Setting.key).all()
