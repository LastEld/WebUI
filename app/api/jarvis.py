#app/api/jarvis.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.jarvis import ChatMessageCreate, ChatMessageRead, ChatMessageUpdate, ChatMessageShort
from app.crud.jarvis import (
    save_message,
    get_history,
    delete_history_for_project
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/jarvis", tags=["Jarvis"])

@router.post("/message", response_model=ChatMessageRead)
def post_message(
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    try:
        msg = save_message(
            db=db,
            project_id=data.project_id,
            role=data.role,
            content=data.content,
            timestamp=data.timestamp,
            metadata=data.metadata,
        )
        return msg
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history/{project_id}", response_model=List[ChatMessageRead])
def chat_history(
    project_id: int,
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    history = get_history(db, project_id, limit=limit, offset=offset)
    return history

@router.delete("/history/{project_id}", response_model=SuccessResponse)
def delete_chat_history(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    deleted = delete_history_for_project(db, project_id)
    return SuccessResponse(result=deleted, detail="Chat history deleted")

# (Опционально) endpoint для получения последних N сообщений (например, для prompt генерации AI)
@router.get("/history/{project_id}/last", response_model=List[ChatMessageShort])
def last_messages(
    project_id: int,
    n: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    history = get_history(db, project_id, limit=n)
    # Можно вернуть короткую схему (ChatMessageShort)
    return [ChatMessageShort.from_orm(msg) for msg in history[-n:]]
