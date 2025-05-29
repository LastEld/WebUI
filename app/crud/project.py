# app/crud/project.py
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.models.project import Project
from app.core.exceptions import (
    ProjectNotFound,
    DuplicateProjectName,
    ProjectValidationError,
)
from app.core.custom_fields import CUSTOM_FIELDS_SCHEMA
import logging
from typing import Optional, List, Dict

logger = logging.getLogger("DevOS.Projects")

def validate_custom_fields_payload(custom_fields: dict):
    for key, value in custom_fields.items():
        schema = CUSTOM_FIELDS_SCHEMA.get(key)
        if not schema:
            raise ProjectValidationError(f"Unknown custom field: {key}")
        if not schema["validator"](value):
            raise ProjectValidationError(f"Invalid value for '{key}': {value} (expected {schema['type']})")

def create_project(db: Session, data: dict) -> Project:
    # Проверка обязательных полей
    if not data.get("name") or not data["name"].strip():
        raise ProjectValidationError("Project name is required.")

    if db.query(Project).filter_by(name=data["name"]).first():
        raise DuplicateProjectName(f"Project with name '{data['name']}' already exists.")

    if data.get("deadline") and data["deadline"] < date.today():
        raise ProjectValidationError("Deadline cannot be in the past.")

    custom_fields = data.get("custom_fields", {})
    if custom_fields:
        validate_custom_fields_payload(custom_fields)

    # Обработка новых возможных полей
    attachments = data.get("attachments", [])
    is_favorite = data.get("is_favorite", False)
    ai_notes = data.get("ai_notes")
    external_id = data.get("external_id")
    subscription_level = data.get("subscription_level")
    color = data.get("color")
    parent_project_id = data.get("parent_project_id")

    project = Project(
        name=data["name"].strip(),
        description=data.get("description", ""),
        status=data.get("status", "active"),
        deadline=data.get("deadline"),
        priority=data.get("priority", 3),
        tags=data.get("tags", []),
        linked_repo=data.get("linked_repo"),
        color=color,
        participants=data.get("participants", []),
        custom_fields=custom_fields,
        is_deleted=False,
        attachments=attachments,
        is_favorite=is_favorite,
        ai_notes=ai_notes,
        external_id=external_id,
        subscription_level=subscription_level,
        parent_project_id=parent_project_id,
        created_at=data.get("created_at") or datetime.utcnow(),
        updated_at=data.get("updated_at") or datetime.utcnow(),
    )

    db.add(project)
    try:
        db.commit()
        db.refresh(project)
        return project
    except Exception as e:
        db.rollback()
        logger.error(f"Exception during save: {e}")
        raise ProjectValidationError("Database error while creating project.")

def get_all_projects(db: Session, filters: dict = None, sort_by: str = "created_at") -> List[Project]:
    query = db.query(Project)
    filters = filters or {}

    if not filters.get("show_archived", False):
        query = query.filter(Project.is_deleted == False)

    if "status" in filters:
        query = query.filter(Project.status == filters["status"])

    if "search" in filters:
        search = f"%{filters['search']}%"
        query = query.filter(
            (Project.name.ilike(search)) | (Project.description.ilike(search))
        )

    if "tag" in filters:
        tag = filters["tag"]
        query = query.filter(Project.tags.contains([tag]))

    if "deadline" in filters:
        query = query.filter(Project.deadline == filters["deadline"])
    if "deadline_from" in filters:
        query = query.filter(Project.deadline >= filters["deadline_from"])
    if "deadline_to" in filters:
        query = query.filter(Project.deadline <= filters["deadline_to"])

    if "priority" in filters:
        query = query.filter(Project.priority == filters["priority"])

    if "custom_fields" in filters:
        for key, value in filters["custom_fields"].items():
            query = query.filter(Project.custom_fields[key].astext == str(value))

    # Доп. фильтры по новым полям
    if "is_favorite" in filters:
        query = query.filter(Project.is_favorite == filters["is_favorite"])
    if "subscription_level" in filters:
        query = query.filter(Project.subscription_level == filters["subscription_level"])
    if "external_id" in filters:
        query = query.filter(Project.external_id == filters["external_id"])

    # Сортировка по любому полю, включая новые (безопасно)
    if hasattr(Project, sort_by):
        if sort_by == "priority":
            query = query.order_by(getattr(Project, sort_by).asc())
        else:
            query = query.order_by(getattr(Project, sort_by).desc())
    else:
        query = query.order_by(Project.created_at.desc())
    return query.all()

def get_project(db: Session, project_id: int) -> Project:
    project = db.query(Project).get(project_id)
    if not project:
        raise ProjectNotFound(f"Project with id={project_id} not found.")
    return project

def update_project(db: Session, project_id: int, data: dict) -> Project:
    project = get_project(db, project_id)
    pre_update_snapshot = {
        k: v for k, v in project.__dict__.items()
        if not k.startswith('_sa_')
    }

    # Обновление базовых и расширенных полей
    for field in [
        "name", "description", "status", "deadline", "priority",
        "tags", "linked_repo", "color", "participants", "parent_project_id",
        "attachments", "is_favorite", "ai_notes", "external_id", "subscription_level"
    ]:
        if field in data:
            setattr(project, field, data[field])

    if "custom_fields" in data:
        cf = data["custom_fields"]
        validate_custom_fields_payload(cf)
        if project.custom_fields is None:
            project.custom_fields = cf
        else:
            project.custom_fields.update(cf)

    # Валидация ключевых полей
    if not project.name:
        raise ProjectValidationError("Project name is required.")
    if project.deadline and project.deadline < date.today():
        raise ProjectValidationError("Deadline cannot be in the past.")

    # Обновляем updated_at
    project.updated_at = datetime.utcnow()

    try:
        db.commit()
        post_update_snapshot = {
            k: v for k, v in project.__dict__.items()
            if not k.startswith('_sa_')
        }
        changes = {
            k: (pre_update_snapshot[k], post_update_snapshot[k])
            for k in post_update_snapshot
            if pre_update_snapshot.get(k) != post_update_snapshot[k]
        }
        if changes:
            logger.info(f"Updated project {project.id} fields: {changes}")
        else:
            logger.info(f"Update called but no changes for project {project.id}")
        return project
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update project: {e}")
        raise ProjectValidationError("Database error while updating project.")

def soft_delete_project(db: Session, project_id: int) -> bool:
    project = get_project(db, project_id)
    if project.is_deleted:
        raise ProjectValidationError("Project already archived.")
    project.is_deleted = True
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to archive project: {e}")
        raise ProjectValidationError("Database error while archiving project.")

def restore_project(db: Session, project_id: int) -> bool:
    project = get_project(db, project_id)
    if not project.is_deleted:
        raise ProjectValidationError("Project is not archived.")
    project.is_deleted = False
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to restore project: {e}")
        raise ProjectValidationError("Database error while restoring project.")

def get_ai_context(db: Session, project_id: int) -> Dict:
    project = get_project(db, project_id)
    is_overdue = bool(project.deadline and project.deadline < date.today())
    ctx = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "deadline": str(project.deadline) if project.deadline else None,
        "priority": project.priority,
        "participants": project.participants or [],
        "tags": project.tags or [],
        "linked_repo": project.linked_repo,
        "parent_project_id": project.parent_project_id,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "custom_fields": project.custom_fields or {},
        "is_overdue": is_overdue,
        "is_deleted": project.is_deleted,
        "attachments": project.attachments or [],
        "is_favorite": project.is_favorite,
        "ai_notes": project.ai_notes,
        "external_id": project.external_id,
        "subscription_level": project.subscription_level,
    }
    logger.info(f"Generated AI context for project: {project.id}")
    return ctx

def summarize_project(db: Session, project_id: int, style: str = "default") -> str:
    ctx = get_ai_context(db, project_id)
    parent_str = f"Parent project ID: {ctx.get('parent_project_id')}\n" if ctx.get('parent_project_id') else ""
    overdue_str = "⚠️ OVERDUE!\n" if ctx.get("is_overdue") else ""
    summary = (
        f"{overdue_str}"
        f"Project '{ctx.get('name')}' — {ctx.get('description')}\n"
        f"Status: {ctx.get('status')}, Priority: {ctx.get('priority')}, Deadline: {ctx.get('deadline')}\n"
        f"Tags: {', '.join(ctx.get('tags', []))}\n"
        f"Participants: {', '.join([p['name'] for p in ctx.get('participants', []) if 'name' in p])}\n"
        f"{parent_str}"
        f"Linked repo: {ctx.get('linked_repo')}\n"
        f"Created at: {ctx.get('created_at')}\n"
        f"AI Notes: {ctx.get('ai_notes') or '-'}\n"
        f"Subscription Level: {ctx.get('subscription_level') or 'Free'}\n"
        f"Attachments: {len(ctx.get('attachments', []))}\n"
    )
    return summary if summary is not None else ""
