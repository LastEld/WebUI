from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.ai_context import AIContext
from app.core.exceptions import ProjectValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime

import logging
logger = logging.getLogger("DevOS.AIContext")

def create_ai_context(
    db: Session,
    object_type: str,
    object_id: int,
    context_data: Dict[str, Any],
    created_by: Optional[str] = None,
    request_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> AIContext:
    ai_ctx = AIContext(
        object_type=object_type,
        object_id=object_id,
        context_data=context_data,
        created_by=created_by,
        request_id=request_id,
        notes=notes,
        created_at=datetime.utcnow()
    )
    db.add(ai_ctx)
    try:
        db.commit()
        db.refresh(ai_ctx)
        logger.info(f"Created AIContext (object_type={object_type}, object_id={object_id})")
        return ai_ctx
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating AIContext: {e}")
        raise ProjectValidationError("AIContext for this object already exists.")
    except Exception as e:
        db.rollback()
        logger.error(f"DB error creating AIContext: {e}")
        raise ProjectValidationError("Database error while creating AIContext.")

def get_ai_context(db: Session, ai_context_id: int) -> Optional[AIContext]:
    return db.query(AIContext).filter(AIContext.id == ai_context_id).first()

def get_latest_ai_context(
    db: Session,
    object_type: str,
    object_id: int
) -> Optional[AIContext]:
    return (
        db.query(AIContext)
        .filter(AIContext.object_type == object_type, AIContext.object_id == object_id)
        .order_by(AIContext.created_at.desc())
        .first()
    )

def get_ai_contexts(
    db: Session,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 50,
    offset: int = 0
) -> List[AIContext]:
    filters = filters or {}
    query = db.query(AIContext)
    if "object_type" in filters:
        query = query.filter(AIContext.object_type == filters["object_type"])
    if "object_id" in filters:
        query = query.filter(AIContext.object_id == filters["object_id"])
    if "created_by" in filters:
        query = query.filter(AIContext.created_by == filters["created_by"])
    if "request_id" in filters:
        query = query.filter(AIContext.request_id == filters["request_id"])
    if "created_after" in filters:
        query = query.filter(AIContext.created_at >= filters["created_after"])
    if "created_before" in filters:
        query = query.filter(AIContext.created_at <= filters["created_before"])
    return query.order_by(AIContext.created_at.desc()).limit(limit).offset(offset).all()

def update_ai_context(
    db: Session,
    ai_context_id: int,
    data: Dict[str, Any]
) -> AIContext:
    ai_ctx = get_ai_context(db, ai_context_id)
    if not ai_ctx:
        raise ProjectValidationError("AIContext not found.")
    for field in ["context_data", "notes"]:
        if field in data:
            setattr(ai_ctx, field, data[field])
    try:
        db.commit()
        db.refresh(ai_ctx)
        logger.info(f"Updated AIContext {ai_ctx.id}")
        return ai_ctx
    except Exception as e:
        db.rollback()
        logger.error(f"DB error updating AIContext: {e}")
        raise ProjectValidationError("Database error while updating AIContext.")

def delete_ai_context(db: Session, ai_context_id: int) -> bool:
    ai_ctx = get_ai_context(db, ai_context_id)
    if not ai_ctx:
        raise ProjectValidationError("AIContext not found.")
    db.delete(ai_ctx)
    try:
        db.commit()
        logger.info(f"Deleted AIContext {ai_ctx.id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"DB error deleting AIContext: {e}")
        raise ProjectValidationError("Database error while deleting AIContext.")
