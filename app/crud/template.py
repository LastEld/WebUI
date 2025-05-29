#app/crud/template.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.template import Template
from app.core.exceptions import (
    DuplicateProjectName,
    ProjectValidationError,
    # Можно создать TemplateNotFoundError
)
import logging
from typing import List, Optional, Dict

logger = logging.getLogger("DevOS.Templates")

def create_template(db: Session, data: dict) -> Template:
    name = data.get("name")
    if not name or not name.strip():
        raise ProjectValidationError("Template name is required.")

    if db.query(Template).filter(Template.name == name).first():
        raise DuplicateProjectName(f"Template with name '{name}' already exists.")

    structure = data.get("structure")
    if not structure:
        raise ProjectValidationError("Template structure is required.")

    template = Template(
        name=name.strip(),
        description=data.get("description"),
        version=data.get("version", "1.0.0"),
        author=data.get("author"),
        is_active=data.get("is_active", True),
        tags=data.get("tags", []),
        structure=structure,
        ai_notes=data.get("ai_notes"),
        subscription_level=data.get("subscription_level"),
        is_private=data.get("is_private", False),
    )
    db.add(template)
    try:
        db.commit()
        db.refresh(template)
        logger.info(f"Created template {template.id} - '{template.name}'")
        return template
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating template: {e}")
        raise ProjectValidationError(f"Template with name '{name}' already exists.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating template: {e}")
        raise ProjectValidationError("Database error while creating template.")

def get_template(db: Session, template_id: int) -> Template:
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise ProjectValidationError(f"Template with id={template_id} not found.")
    return template

def get_all_templates(db: Session, filters: Optional[Dict] = None) -> List[Template]:
    filters = filters or {}
    query = db.query(Template)

    if "is_active" in filters:
        query = query.filter(Template.is_active == filters["is_active"])

    if "name" in filters:
        query = query.filter(Template.name.ilike(f"%{filters['name']}%"))

    if "tag" in filters:
        query = query.filter(Template.tags.contains([filters["tag"]]))

    if "subscription_level" in filters:
        query = query.filter(Template.subscription_level == filters["subscription_level"])

    return query.order_by(Template.created_at.desc()).all()

def update_template(db: Session, template_id: int, data: dict) -> Template:
    template = get_template(db, template_id)

    for field in [
        "name", "description", "version", "author",
        "is_active", "tags", "structure", "ai_notes",
        "subscription_level", "is_private"
    ]:
        if field in data:
            setattr(template, field, data[field])

    if not template.name:
        raise ProjectValidationError("Template name is required.")

    if not template.structure:
        raise ProjectValidationError("Template structure is required.")

    try:
        db.commit()
        db.refresh(template)
        logger.info(f"Updated template {template.id} - '{template.name}'")
        return template
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating template {template.id}: {e}")
        raise ProjectValidationError("Database error while updating template.")

def soft_delete_template(db: Session, template_id: int) -> bool:
    template = get_template(db, template_id)
    if not template.is_active:
        raise ProjectValidationError("Template already inactive.")
    template.is_active = False
    try:
        db.commit()
        logger.info(f"Soft-deleted template {template_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to soft-delete template {template_id}: {e}")
        raise ProjectValidationError("Database error while deleting template.")

def restore_template(db: Session, template_id: int) -> bool:
    template = get_template(db, template_id)
    if template.is_active:
        raise ProjectValidationError("Template is already active.")
    template.is_active = True
    try:
        db.commit()
        logger.info(f"Restored template {template_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to restore template {template_id}: {e}")
        raise ProjectValidationError("Database error while restoring template.")
