#app/api/settings.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from app.schemas.settings import (
    SettingCreate, SettingUpdate, SettingRead
)
from app.crud.settings import (
    create_setting,
    get_setting,
    update_setting,
    delete_setting,
    get_all_settings
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.post("/", response_model=SettingRead)
def create_new_setting(
    data: SettingCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Создать новую настройку (глобальную или пользовательскую).
    """
    try:
        setting = create_setting(db, data.dict())
        return setting
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[SettingRead])
def list_settings(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить список всех настроек (глобальных или пользователя).
    """
    return get_all_settings(db, user_id=user_id)

@router.get("/{key}", response_model=SettingRead)
def get_one_setting(
    key: str,
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить настройку по ключу (и user_id, если нужно).
    """
    setting = get_setting(db, key, user_id=user_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.patch("/{setting_id}", response_model=SettingRead)
def update_one_setting(
    setting_id: int,
    data: SettingUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Обновить настройку по ID.
    """
    try:
        setting = update_setting(db, setting_id, data.dict(exclude_unset=True))
        return setting
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{setting_id}", response_model=SuccessResponse)
def delete_one_setting(
    setting_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Удалить настройку по ID.
    """
    delete_setting(db, setting_id)
    return SuccessResponse(result=setting_id, detail="Setting deleted")
