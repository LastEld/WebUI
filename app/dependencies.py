# app/dependencies.py

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, oauth2_scheme
from app.core.settings import settings
from app.crud.user import get_user_by_email
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.db.session import SessionLocal

# --- Database Dependency ---
def get_db() -> Generator:
    # Replace with your actual database session logic
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# --- User Authentication Dependency ---
async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenPayload(sub=email)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email=token_data.sub) # Changed
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active: # is_active needs to be a field in User model
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
