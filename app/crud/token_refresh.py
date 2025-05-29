#app/crud/token_refresh.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.token_refresh import TokenRefresh
from app.core.exceptions import ProjectValidationError
from typing import Optional, List
from datetime import datetime

import logging
logger = logging.getLogger("DevOS.TokenRefresh")

def create_token_refresh(
    db: Session,
    user_id: int,
    refresh_token: str,
    expires_at: Optional[datetime] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> TokenRefresh:
    token_obj = TokenRefresh(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(token_obj)
    try:
        db.commit()
        db.refresh(token_obj)
        logger.info(f"Created refresh token for user {user_id}")
        return token_obj
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating token: {e}")
        raise ProjectValidationError("Token already exists.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating token: {e}")
        raise ProjectValidationError("Database error while creating refresh token.")

def get_token_by_refresh(db: Session, refresh_token: str) -> Optional[TokenRefresh]:
    return db.query(TokenRefresh).filter(TokenRefresh.refresh_token == refresh_token, TokenRefresh.is_active == True).first()

def get_tokens_by_user(db: Session, user_id: int) -> List[TokenRefresh]:
    return db.query(TokenRefresh).filter(TokenRefresh.user_id == user_id).order_by(TokenRefresh.created_at.desc()).all()

def deactivate_token(db: Session, refresh_token: str) -> bool:
    token = db.query(TokenRefresh).filter(TokenRefresh.refresh_token == refresh_token, TokenRefresh.is_active == True).first()
    if not token:
        raise ProjectValidationError("Token not found or already deactivated.")
    token.is_active = False
    try:
        db.commit()
        logger.info(f"Deactivated token {refresh_token}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deactivate token: {e}")
        raise ProjectValidationError("Database error while deactivating token.")

def deactivate_tokens_by_user(db: Session, user_id: int) -> int:
    tokens = db.query(TokenRefresh).filter(TokenRefresh.user_id == user_id, TokenRefresh.is_active == True).all()
    count = 0
    for token in tokens:
        token.is_active = False
        count += 1
    try:
        db.commit()
        logger.info(f"Deactivated {count} tokens for user {user_id}")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deactivate tokens: {e}")
        raise ProjectValidationError("Database error while deactivating tokens.")

def cleanup_expired_tokens(db: Session) -> int:
    """Deactivate all tokens that expired before now."""
    now = datetime.utcnow()
    tokens = db.query(TokenRefresh).filter(TokenRefresh.is_active == True, TokenRefresh.expires_at != None, TokenRefresh.expires_at < now).all()
    count = 0
    for token in tokens:
        token.is_active = False
        count += 1
    try:
        db.commit()
        logger.info(f"Cleaned up {count} expired tokens")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clean up expired tokens: {e}")
        raise ProjectValidationError("Database error while cleaning up expired tokens.")
