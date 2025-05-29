#app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse
from app.schemas.user import UserRead
from app.crud.user import authenticate_user, get_user_by_username, set_last_login
from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from app.dependencies import get_db
from datetime import timedelta
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "roles": user.roles},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    set_last_login(db, user.id)
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token( #TODO: remove db: Session = Depends(get_db) if not used
    data: TokenRefreshRequest,
    db: Session = Depends(get_db), # Required for get_user_by_username
):
    payload = verify_refresh_token(data.refresh_token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")
    user = get_user_by_username(db, payload["sub"]) # db is used here
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    new_access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "roles": user.roles},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenRefreshResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
def logout(
    data: TokenRefreshRequest,
    # db: Session = Depends(get_db) # db is no longer used
):
    # Деактивируем refresh токен (logout only current session)
    # deactivate_token(db, data.refresh_token) # Removed as per requirements
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserRead)
def get_me(
    current_user=Depends(get_user_by_username),  # Обычно get_current_active_user
    db: Session = Depends(get_db)
):
    user = get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
