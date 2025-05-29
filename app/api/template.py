#app/api/template.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.template import (
    TemplateCreate, TemplateRead, TemplateUpdate, TemplateShort
)
from app.crud.template import (
    create_template,
    get_template,
    get_all_templates,
    update_template,
    delete_template,
    clone_template_to_project,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.post("/", response_model=TemplateRead)
def create_new_template(
    data: TemplateCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Создать новый шаблон.
    """
    try:
        template = create_template(db, data.dict())
        return template
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{template_id}", response_model=TemplateRead)
def get_one_template(
    template_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить шаблон по ID.
    """
    template = get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/", response_model=List[TemplateShort])
def list_templates(
    is_active: Optional[bool] = Query(None),
    subscription_level: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить список шаблонов (фильтрация по активности, подписке, тегу).
    """
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if subscription_level:
        filters["subscription_level"] = subscription_level
    if tag:
        filters["tags"] = [tag]
    return get_all_templates(db, filters=filters)

@router.patch("/{template_id}", response_model=TemplateRead)
def update_one_template(
    template_id: int,
    data: TemplateUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Обновить шаблон.
    """
    try:
        template = update_template(db, template_id, data.dict(exclude_unset=True))
        return template
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{template_id}", response_model=SuccessResponse)
def delete_one_template(
    template_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Удалить шаблон.
    """
    delete_template(db, template_id)
    return SuccessResponse(result=template_id, detail="Template deleted")

@router.post("/{template_id}/clone", response_model=SuccessResponse)
def clone_template(
    template_id: int,
    target_project_data: Dict[str, Any],  # Обычно ProjectCreate или dict с настройками
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Клонировать шаблон в новый проект (универсальный endpoint для AI и UI).
    """
    try:
        new_project = clone_template_to_project(db, template_id, target_project_data)
        return SuccessResponse(result=new_project.id, detail="Project created from template")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
