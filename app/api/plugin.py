#app/api/plugin.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.plugin import (
    PluginCreate, PluginRead, PluginUpdate, PluginShort
)
from app.crud.plugin import (
    create_plugin,
    get_plugin,
    get_all_plugins,
    update_plugin,
    delete_plugin,
    activate_plugin,
    deactivate_plugin,
    get_active_plugins_summary,
    run_plugin_action,
)
from app.dependencies import get_db, get_current_active_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/plugins", tags=["Plugins"])

@router.post("/", response_model=PluginRead)
def create_new_plugin(
    data: PluginCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    try:
        plugin = create_plugin(db, data.dict())
        return plugin
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{plugin_id}", response_model=PluginRead)
def get_one_plugin(
    plugin_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    plugin = get_plugin(db, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin

@router.get("/", response_model=List[PluginShort])
def list_plugins(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    return get_all_plugins(db, filters=filters)

@router.patch("/{plugin_id}", response_model=PluginRead)
def update_one_plugin(
    plugin_id: int,
    data: PluginUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    plugin = update_plugin(db, plugin_id, data.dict(exclude_unset=True))
    return plugin

@router.delete("/{plugin_id}", response_model=SuccessResponse)
def delete_one_plugin(
    plugin_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    delete_plugin(db, plugin_id)
    return SuccessResponse(result=plugin_id, detail="Plugin deleted")

@router.post("/{plugin_id}/activate", response_model=PluginRead)
def activate_plugin_endpoint(
    plugin_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    return activate_plugin(db, plugin_id)

@router.post("/{plugin_id}/deactivate", response_model=PluginRead)
def deactivate_plugin_endpoint(
    plugin_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    return deactivate_plugin(db, plugin_id)

@router.get("/active/summary", response_model=str)
def get_plugins_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    return get_active_plugins_summary(db)

@router.post("/run/{plugin_name}/{action_name}", response_model=str)
def run_plugin(
    plugin_name: str,
    action_name: str,
    project_context: dict,
    plugin_params: Optional[dict] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    """
    Запустить действие (action) плагина с передачей project_context и (опциональных) параметров.
    """
    return run_plugin_action(db, plugin_name, action_name, project_context, plugin_params or {})
