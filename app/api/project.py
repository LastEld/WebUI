#app/api/project.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.project import (
    ProjectCreate, ProjectRead, ProjectUpdate, ProjectShort
)
from app.crud.project import (
    create_project,
    get_project,
    get_all_projects,
    update_project,
    soft_delete_project,
    restore_project,
    get_ai_context,
    summarize_project,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectRead)
def create_new_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Создать новый проект.
    """
    try:
        project = create_project(db, data.dict())
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}", response_model=ProjectRead)
def get_one_project(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить проект по ID.
    """
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/", response_model=List[ProjectShort])
def list_projects(
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    deadline: Optional[str] = Query(None),
    deadline_from: Optional[str] = Query(None),
    deadline_to: Optional[str] = Query(None),
    priority: Optional[int] = Query(None, ge=1, le=5),
    custom_fields: Optional[Dict[str, Any]] = None,
    show_archived: bool = Query(False),
    sort_by: Optional[str] = Query("created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить список проектов с фильтрацией.
    """
    filters = {
        "status": status,
        "tag": tag,
        "search": search,
        "deadline": deadline,
        "deadline_from": deadline_from,
        "deadline_to": deadline_to,
        "priority": priority,
        "custom_fields": custom_fields,
        "show_archived": show_archived,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    return get_all_projects(db, filters=filters, sort_by=sort_by)

@router.patch("/{project_id}", response_model=ProjectRead)
def update_one_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Обновить проект.
    """
    try:
        project = update_project(db, project_id, data.dict(exclude_unset=True))
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{project_id}", response_model=SuccessResponse)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Архивировать проект (soft-delete).
    """
    soft_delete_project(db, project_id)
    return SuccessResponse(result=project_id, detail="Project archived")

@router.post("/{project_id}/restore", response_model=SuccessResponse)
def restore_deleted_project(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Восстановить архивированный проект.
    """
    restore_project(db, project_id)
    return SuccessResponse(result=project_id, detail="Project restored")

@router.get("/{project_id}/ai_context", response_model=Dict[str, Any])
def get_project_ai_context(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить AI-контекст по проекту.
    """
    return get_ai_context(db, project_id)

@router.get("/{project_id}/summary", response_model=str)
def project_summary(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Краткое описание проекта для AI/сводки.
    """
    return summarize_project(db, project_id)
