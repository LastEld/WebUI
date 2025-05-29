#app/api/task.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.task import (
    TaskCreate, TaskRead, TaskUpdate, TaskShort
)
from app.crud.task import (
    create_task,
    get_task,
    get_all_tasks,
    update_task,
    soft_delete_task,
    restore_task,
    get_ai_context,
    summarize_task,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskRead)
def create_new_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Создать новую задачу.
    """
    try:
        task = create_task(db, data.dict())
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{task_id}", response_model=TaskRead)
def get_one_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить задачу по ID.
    """
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=List[TaskShort])
def list_tasks(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    deadline_before: Optional[str] = Query(None),
    deadline_after: Optional[str] = Query(None),
    parent_task_id: Optional[int] = Query(None),
    priority: Optional[int] = Query(None, ge=1, le=5),
    tag: Optional[str] = Query(None),
    custom_fields: Optional[Dict[str, Any]] = None,
    assignee_id: Optional[int] = Query(None),
    show_archived: bool = Query(False),
    sort_by: Optional[str] = Query("deadline"),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить список задач с фильтрацией и поиском.
    """
    filters = {
        "project_id": project_id,
        "status": status,
        "search": search,
        "deadline_before": deadline_before,
        "deadline_after": deadline_after,
        "parent_task_id": parent_task_id,
        "priority": priority,
        "tag": tag,
        "custom_fields": custom_fields,
        "assignee_id": assignee_id,
        "show_archived": show_archived,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    return get_all_tasks(db, filters=filters, sort_by=sort_by)

@router.patch("/{task_id}", response_model=TaskRead)
def update_one_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Обновить задачу.
    """
    try:
        task = update_task(db, task_id, data.dict(exclude_unset=True))
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{task_id}", response_model=SuccessResponse)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Архивировать задачу (soft-delete).
    """
    soft_delete_task(db, task_id)
    return SuccessResponse(result=task_id, detail="Task archived")

@router.post("/{task_id}/restore", response_model=SuccessResponse)
def restore_deleted_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Восстановить архивированную задачу.
    """
    restore_task(db, task_id)
    return SuccessResponse(result=task_id, detail="Task restored")

@router.get("/{task_id}/ai_context", response_model=Dict[str, Any])
def get_task_ai_context(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Получить AI-контекст по задаче.
    """
    return get_ai_context(db, task_id)

@router.get("/{task_id}/summary", response_model=str)
def task_summary(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Краткое описание задачи для AI/сводки.
    """
    return summarize_task(db, task_id)
