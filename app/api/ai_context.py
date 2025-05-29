#app/api/ai_context.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.ai_context import (
    ProjectAIContext, TaskAIContext, DevLogAIContext, UserAIContext, PluginAIContext
)
from app.crud.ai_context import (
    create_ai_context,
    get_ai_context,
    get_ai_contexts,
    update_ai_context,
    delete_ai_context,
    get_latest_ai_context,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/ai-context", tags=["AI Context"])

@router.post("/", response_model=SuccessResponse)
def create_ai_ctx(
    object_type: str,
    object_id: int,
    context_data: dict,
    created_by: Optional[str] = None,
    request_id: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Создать новый AI-контекст (для задачи, проекта, пользователя и т.д.)
    """
    try:
        ai_ctx = create_ai_context(
            db=db,
            object_type=object_type,
            object_id=object_id,
            context_data=context_data,
            created_by=created_by or user.username,
            request_id=request_id,
            notes=notes,
        )
        return SuccessResponse(result=ai_ctx.id, detail="AIContext created")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ai_context_id}")
def get_one_ai_ctx(
    ai_context_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    ai_ctx = get_ai_context(db, ai_context_id)
    if not ai_ctx:
        raise HTTPException(status_code=404, detail="AIContext not found")
    return ai_ctx

@router.get("/latest/")
def get_latest_ctx(
    object_type: str = Query(..., example="project"),
    object_id: int = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    ai_ctx = get_latest_ai_context(db, object_type, object_id)
    if not ai_ctx:
        raise HTTPException(status_code=404, detail="AIContext not found")
    return ai_ctx

@router.get("/", response_model=List[dict])
def list_ai_contexts(
    object_type: Optional[str] = None,
    object_id: Optional[int] = None,
    created_by: Optional[str] = None,
    request_id: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    filters = {}
    if object_type: filters["object_type"] = object_type
    if object_id: filters["object_id"] = object_id
    if created_by: filters["created_by"] = created_by
    if request_id: filters["request_id"] = request_id
    if created_after: filters["created_after"] = created_after
    if created_before: filters["created_before"] = created_before
    return get_ai_contexts(db, filters=filters, limit=limit, offset=offset)

@router.patch("/{ai_context_id}", response_model=SuccessResponse)
def patch_ai_context(
    ai_context_id: int,
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    ai_ctx = update_ai_context(db, ai_context_id, data)
    return SuccessResponse(result=ai_ctx.id, detail="AIContext updated")

@router.delete("/{ai_context_id}", response_model=SuccessResponse)
def delete_ai_ctx(
    ai_context_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    delete_ai_context(db, ai_context_id)
    return SuccessResponse(result=ai_context_id, detail="AIContext deleted")
