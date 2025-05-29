#app/api/token_refresh.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.token_refresh import TokenRefreshRequest, TokenRefreshResponse
from app.crud.token_refresh import (
    get_token_by_refresh,
    get_tokens_by_user,
    deactivate_token,
    deactivate_tokens_by_user,
    cleanup_expired_tokens,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/token-refresh", tags=["TokenRefresh"])

@router.get("/", response_model=List[dict])
def list_active_tokens(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить список refresh-токенов пользователя (или всех, если admin).
    """
    uid = user_id or user.id
    return [t.__dict__ for t in get_tokens_by_user(db, uid)]

@router.post("/deactivate", response_model=SuccessResponse)
def deactivate_refresh_token(
    data: TokenRefreshRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Деактивировать конкретный refresh-токен (logout сессии).
    """
    try:
        deactivate_token(db, data.refresh_token)
        return SuccessResponse(result=data.refresh_token, detail="Token deactivated")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/deactivate-all", response_model=SuccessResponse)
def deactivate_all_tokens(
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Деактивировать все refresh-токены пользователя (logout со всех устройств).
    """
    count = deactivate_tokens_by_user(db, user.id)
    return SuccessResponse(result=count, detail="All tokens deactivated")

@router.post("/cleanup", response_model=SuccessResponse)
def cleanup_expired(
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Очистить все просроченные refresh-токены (admin/system).
    """
    count = cleanup_expired_tokens(db)
    return SuccessResponse(result=count, detail="Expired tokens cleaned up")
