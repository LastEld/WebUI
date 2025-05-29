#app/api/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.crud.user import (
    create_user,
    get_user,
    get_user_by_username,
    get_user_by_email,
    update_user,
    get_users,
    soft_delete_user,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
def register_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)  # Можно ограничить только для админов
):
    """
    Зарегистрировать нового пользователя.
    """
    try:
        user_obj = create_user(db, data.dict())
        return user_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserRead)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить профиль пользователя по ID.
    """
    user_obj = get_user(db, user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

@router.get("/", response_model=List[UserRead])
def list_users(
    is_active: Optional[bool] = Query(None),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить список пользователей (фильтрация по активности, роли, поиску).
    """
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if role:
        filters["role"] = role
    if search:
        filters["search"] = search
    return get_users(db, filters=filters)

@router.patch("/{user_id}", response_model=UserRead)
def patch_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Обновить данные пользователя.
    """
    try:
        user_obj = update_user(db, user_id, data.dict(exclude_unset=True))
        return user_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", response_model=SuccessResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Деактивировать (soft-delete) пользователя.
    """
    soft_delete_user(db, user_id)
    return SuccessResponse(result=user_id, detail="User deactivated")

@router.get("/by-username/{username}", response_model=UserRead)
def get_by_username(
    username: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить пользователя по username.
    """
    user_obj = get_user_by_username(db, username)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

@router.get("/by-email/{email}", response_model=UserRead)
def get_by_email(
    email: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить пользователя по email.
    """
    user_obj = get_user_by_email(db, email)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj
