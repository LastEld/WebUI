#app/api/devlog.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.devlog import (
    DevLogCreate, DevLogRead, DevLogUpdate, DevLogShort
)
from app.crud.devlog import (
    create_entry,
    get_entry,
    update_entry,
    soft_delete_entry,
    restore_entry,
    get_entries,
    summarize_entry,
    get_ai_context,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/devlog", tags=["DevLog"])

@router.post("/", response_model=DevLogRead)
def create_devlog_entry(
    data: DevLogCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    try:
        entry = create_entry(db, data.dict())
        return entry
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{entry_id}", response_model=DevLogRead)
def read_devlog_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    entry = get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="DevLog entry not found")
    return entry

@router.patch("/{entry_id}", response_model=DevLogRead)
def update_devlog_entry(
    entry_id: int,
    data: DevLogUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    entry = update_entry(db, entry_id, data.dict(exclude_unset=True))
    return entry

@router.delete("/{entry_id}", response_model=SuccessResponse)
def delete_devlog_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    soft_delete_entry(db, entry_id)
    return SuccessResponse(result=entry_id, detail="DevLog entry archived")

@router.post("/{entry_id}/restore", response_model=SuccessResponse)
def restore_devlog_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    restore_entry(db, entry_id)
    return SuccessResponse(result=entry_id, detail="DevLog entry restored")

@router.get("/", response_model=List[DevLogShort])
def list_devlog_entries(
    project_id: Optional[int] = Query(None),
    task_id: Optional[int] = Query(None),
    entry_type: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    show_archived: Optional[bool] = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    filters = {
        "project_id": project_id,
        "task_id": task_id,
        "entry_type": entry_type,
        "author": author,
        "tag": tag,
        "date_from": date_from,
        "date_to": date_to,
        "search": search,
        "show_archived": show_archived
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    result = get_entries(db, filters, page, per_page)
    return result["entries"]

@router.get("/{entry_id}/ai_context", response_model=Dict[str, Any])
def get_entry_ai_context(
    entry_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    return get_ai_context(db, entry_id)

@router.get("/{entry_id}/summary", response_model=str)
def summarize_devlog_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    return summarize_entry(db, entry_id)
