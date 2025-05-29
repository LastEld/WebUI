#app/crud/auth.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.auth import AccessToken
from app.models.user import User
from app.core.exceptions import ProjectValidationError
from typing import Optional, List
from datetime import datetime

import logging
logger = logging.getLogger("DevOS.Auth")

def create_access_token(
    db: Session,
    user_id: int,
    token: str,
    expires_at: Optional[datetime] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AccessToken:
    access_token_obj = AccessToken(
        user_id=user_id,
        token=token,
        issued_at=datetime.utcnow(),
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
        is_active=True,
        revoked=False,
    )
    db.add(access_token_obj)
    try:
        db.commit()
        db.refresh(access_token_obj)
        logger.info(f"Issued access token for user {user_id}")
        return access_token_obj
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating access token: {e}")
        raise ProjectValidationError("Access token already exists.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating access token: {e}")
        raise ProjectValidationError("Database error while creating access token.")

def get_access_token(db: Session, token: str) -> Optional[AccessToken]:
    return db.query(AccessToken).filter(AccessToken.token == token, AccessToken.is_active == True, AccessToken.revoked == False).first()

def get_active_tokens_by_user(db: Session, user_id: int) -> List[AccessToken]:
    return db.query(AccessToken).filter(
        AccessToken.user_id == user_id,
        AccessToken.is_active == True,
        AccessToken.revoked == False
    ).order_by(AccessToken.issued_at.desc()).all()

def revoke_access_token(db: Session, token: str) -> bool:
    access_token = db.query(AccessToken).filter(AccessToken.token == token, AccessToken.is_active == True).first()
    if not access_token:
        raise ProjectValidationError("Access token not found or already revoked.")
    access_token.revoked = True
    access_token.is_active = False
    try:
        db.commit()
        logger.info(f"Revoked access token {token}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to revoke access token: {e}")
        raise ProjectValidationError("Database error while revoking access token.")

def revoke_all_tokens_for_user(db: Session, user_id: int) -> int:
    tokens = db.query(AccessToken).filter(
        AccessToken.user_id == user_id,
        AccessToken.is_active == True,
        AccessToken.revoked == False
    ).all()
    count = 0
    for token in tokens:
        token.revoked = True
        token.is_active = False
        count += 1
    try:
        db.commit()
        logger.info(f"Revoked {count} access tokens for user {user_id}")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to revoke tokens for user: {e}")
        raise ProjectValidationError("Database error while revoking tokens.")

def cleanup_expired_tokens(db: Session) -> int:
    """Deactivate all access tokens that expired before now."""
    now = datetime.utcnow()
    tokens = db.query(AccessToken).filter(
        AccessToken.is_active == True,
        AccessToken.revoked == False,
        AccessToken.expires_at != None,
        AccessToken.expires_at < now
    ).all()
    count = 0
    for token in tokens:
        token.is_active = False
        token.revoked = True
        count += 1
    try:
        db.commit()
        logger.info(f"Cleaned up {count} expired access tokens")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clean up expired tokens: {e}")
        raise ProjectValidationError("Database error while cleaning up expired tokens.")
