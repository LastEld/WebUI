#app/crud/team.py
from sqlalchemy.orm import Session
from app.models.team import Team
from sqlalchemy.exc import IntegrityError

class TeamError(Exception):
    pass

def create_team(db: Session, data: dict) -> Team:
    name = data["name"].strip()
    if db.query(Team).filter_by(name=name).first():
        raise TeamError(f"Team with name '{name}' already exists.")
    team = Team(
        name=name,
        description=data.get("description", "").strip()
    )
    db.add(team)
    try:
        db.commit()
        db.refresh(team)
        return team
    except IntegrityError as e:
        db.rollback()
        raise TeamError(f"Error creating team: {e}")

def get_team(db: Session, team_id: int) -> Team:
    team = db.query(Team).get(team_id)
    if not team:
        raise TeamError(f"Team with id={team_id} not found.")
    return team

def get_all_teams(db: Session):
    return db.query(Team).filter(Team.is_deleted == False).all()  # якщо є is_deleted

def update_team(db: Session, team_id: int, data: dict) -> Team:
    team = get_team(db, team_id)
    if "name" in data:
        new_name = data["name"].strip()
        existing = db.query(Team).filter(Team.name == new_name, Team.id != team_id).first()
        if existing:
            raise TeamError(f"Team with name '{new_name}' already exists.")
        team.name = new_name
    if "description" in data:
        team.description = data["description"].strip()
    db.commit()
    db.refresh(team)
    return team

def delete_team(db: Session, team_id: int) -> bool:
    team = get_team(db, team_id)
    # team.is_deleted = True  # soft-delete
    # db.commit()
    db.delete(team)  # hard delete
    db.commit()
    return True
