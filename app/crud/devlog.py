#app/crud/devlog.py
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.devlog import DevLogEntry
from app.core.exceptions import DevLogNotFound, DevLogValidationError
from app.core.custom_fields import CUSTOM_FIELDS_SCHEMA
import logging

logger = logging.getLogger("DevOS.DevLog")

def validate_custom_fields_payload(custom_fields)
    for key, value in custom_fields.items():
        schema = CUSTOM_FIELDS_SCHEMA.get(key)
        if not schema:
            raise DevLogValidationError(f"Unknown custom field: {key}")
        if not schema["validator"](value):
            raise DevLogValidationError(f"Invalid value for '{key}': {value} (expected {schema['type']})")

def create_entry(db: Session, data: dict) -> DevLogEntry:
    if not data.get("content") or not data.get("content").strip():
        raise DevLogValidationError("DevLog entry content cannot be empty.")
    if not data.get("author") or not data.get("author").strip():
        raise DevLogValidationError("Author is required.")

    custom_fields = data.get("custom_fields", {})
    if custom_fields:
        validate_custom_fields_payload(custom_fields)

    entry = DevLogEntry(
        project_id=data.get("project_id"),
        task_id=data.get("task_id"),
        entry_type=data.get("entry_type", "note"),
        content=data.get("content").strip(),
        author=data.get("author").strip(),
        tags=data.get("tags") or [],
        created_at=data.get("created_at") or datetime.utcnow(),
        updated_at=data.get("updated_at") or datetime.utcnow(),
        custom_fields=custom_fields,
        is_deleted=False,
        # Новые поля:
        edited_by=data.get("edited_by"),
        edit_reason=data.get("edit_reason"),
        attachments=data.get("attachments", []),
        ai_notes=data.get("ai_notes"),
    )
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        logger.info(f"Created DevLog entry {entry.id} (project_id={entry.project_id}, author={entry.author})")
        return entry
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create DevLog entry: {e}")
        raise DevLogValidationError(f"DB error: {e}")

def get_entry(db: Session, entry_id: int) -> DevLogEntry:
    entry = db.query(DevLogEntry).get(entry_id)
    if not entry or getattr(entry, "is_deleted", False):
        raise DevLogNotFound(f"DevLogEntry {entry_id} not found")
    return entry

def update_entry(db: Session, entry_id: int, data: dict) -> DevLogEntry:
    entry = get_entry(db, entry_id)
    updated = False
    # Обновляем базовые поля
    for field in ["content", "entry_type", "author", "tags", "edited_by", "edit_reason", "attachments", "ai_notes"]:
        if field in data and getattr(entry, field) != data[field]:
            setattr(entry, field, data[field])
            updated = True
    if "project_id" in data:
        entry.project_id = data["project_id"]
        updated = True
    if "task_id" in data:
        entry.task_id = data["task_id"]
        updated = True
    if "custom_fields" in data:
        cf = data["custom_fields"]
        validate_custom_fields_payload(cf)
        if entry.custom_fields is None:
            entry.custom_fields = cf
        else:
            entry.custom_fields.update(cf)
        updated = True
    if updated:
        entry.updated_at = datetime.utcnow()
        try:
            db.commit()
            db.refresh(entry)
            logger.info(f"Updated DevLog entry {entry.id}")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to update DevLog entry: {e}")
            raise DevLogValidationError(f"DB error: {e}")
    return entry

def soft_delete_entry(db: Session, entry_id: int) -> bool:
    entry = get_entry(db, entry_id)
    if getattr(entry, "is_deleted", False):
        raise DevLogValidationError("DevLog entry already archived.")
    entry.is_deleted = True
    try:
        db.commit()
        logger.info(f"Archived DevLog entry {entry_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to archive DevLog entry: {e}")
        raise DevLogValidationError(f"DB error: {e}")

def restore_entry(db: Session, entry_id: int) -> bool:
    entry = db.query(DevLogEntry).get(entry_id)
    if not entry or not getattr(entry, "is_deleted", False):
        raise DevLogNotFound("DevLog entry not found or not archived.")
    entry.is_deleted = False
    try:
        db.commit()
        logger.info(f"Restored DevLog entry {entry_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to restore DevLog entry: {e}")
        raise DevLogValidationError(f"DB error: {e}")

def get_entries(db: Session, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
    query = db.query(DevLogEntry)
    filters = filters or {}

    show_archived = filters.get("show_archived", False)
    if not show_archived:
        query = query.filter(DevLogEntry.is_deleted == False)

    if "project_id" in filters:
        query = query.filter(DevLogEntry.project_id == filters["project_id"])
    if "task_id" in filters:
        query = query.filter(DevLogEntry.task_id == filters["task_id"])
    if "entry_type" in filters and filters["entry_type"] != "all":
        query = query.filter(DevLogEntry.entry_type == filters["entry_type"])
    if "author" in filters and filters["author"]:
        query = query.filter(DevLogEntry.author.ilike(f"%{filters['author']}%"))
    if "tag" in filters and filters["tag"]:
        query = query.filter(DevLogEntry.tags.contains([filters["tag"]]))

    if "date_from" in filters and filters["date_from"]:
        try:
            date_from_obj = datetime.strptime(str(filters["date_from"]), "%Y-%m-%d").date()
            query = query.filter(DevLogEntry.created_at >= date_from_obj)
        except ValueError:
            logger.warning(f"Invalid date_from format: {filters['date_from']}. Expected YYYY-MM-DD.")

    if "date_to" in filters and filters["date_to"]:
        try:
            date_to_obj = datetime.strptime(str(filters["date_to"]), "%Y-%m-%d").date()
            end_of_day_to = datetime.combine(date_to_obj, datetime.max.time())
            query = query.filter(DevLogEntry.created_at <= end_of_day_to)
        except ValueError:
            logger.warning(f"Invalid date_to format: {filters['date_to']}. Expected YYYY-MM-DD.")

    if "search" in filters and filters["search"]:
        search_term = f"%{filters['search']}%"
        query = query.filter(DevLogEntry.content.ilike(search_term))

    if "custom_fields" in filters:
        for key, value in filters["custom_fields"].items():
            if key and value:
                query = query.filter(DevLogEntry.custom_fields[key].astext.ilike(f"%{str(value)}%"))

    total_count = query.count()
    query = query.order_by(DevLogEntry.created_at.desc())

    if page < 1: page = 1
    if per_page < 1: per_page = 1
    offset = (page - 1) * per_page

    entries = query.limit(per_page).offset(offset).all()
    return {"entries": entries, "total_count": total_count}

def summarize_entry(db: Session, entry_id: int) -> str:
    entry = get_entry(db, entry_id)
    return (
        f"[{entry.created_at.strftime('%Y-%m-%d %H:%M')}] "
        f"{entry.author}: {entry.entry_type.upper()} - {entry.content[:180]}"
        + (f" (tags: {', '.join(entry.tags or [])})" if entry.tags else "")
    )

def get_ai_context(db: Session, entry_id: int) -> dict:
    entry = get_entry(db, entry_id)
    return {
        "id": entry.id,
        "project_id": entry.project_id,
        "task_id": entry.task_id,
        "entry_type": entry.entry_type,
        "content": entry.content,
        "author": entry.author,
        "tags": entry.tags or [],
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat() if hasattr(entry, "updated_at") and entry.updated_at else None,
        "custom_fields": entry.custom_fields or {},
        "is_deleted": entry.is_deleted,
        # Новое:
        "edited_by": entry.edited_by,
        "edit_reason": entry.edit_reason,
        "attachments": entry.attachments or [],
        "ai_notes": entry.ai_notes,
    }
