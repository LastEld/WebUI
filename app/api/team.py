#app/api/team.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate
from app.crud.team import create_team, get_team, get_all_teams, update_team, delete_team, TeamError
from app.dependencies import get_db

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team_api(data: TeamCreate, db: Session = Depends(get_db)):
    """
    Створити нову команду.
    """
    try:
        return create_team(db, data.dict())
    except TeamError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{team_id}", response_model=TeamRead)
def read_team(team_id: int, db: Session = Depends(get_db)):
    """
    Отримати команду за ID.
    """
    try:
        return get_team(db, team_id)
    except TeamError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[TeamRead])
def read_teams(db: Session = Depends(get_db)):
    """
    Список всіх команд.
    """
    return get_all_teams(db)

@router.put("/{team_id}", response_model=TeamRead)
def update_team_api(team_id: int, data: TeamUpdate, db: Session = Depends(get_db)):
    """
    Оновити команду.
    """
    try:
        return update_team(db, team_id, data.dict(exclude_unset=True))
    except TeamError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team_api(team_id: int, db: Session = Depends(get_db)):
    """
    Видалити команду.
    """
    try:
        delete_team(db, team_id)
    except TeamError as e:
        raise HTTPException(status_code=404, detail=str(e))
