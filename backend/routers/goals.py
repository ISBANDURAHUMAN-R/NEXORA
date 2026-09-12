from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Goal, Skill
from schemas import GoalCreate, GoalResponse

router = APIRouter(prefix="/api/goals", tags=["Goals"])

@router.get("", response_model=List[GoalResponse])
def get_goals(db: Session = Depends(get_db)):
    goals = db.query(Goal).order_by(Goal.completed.asc(), Goal.created_at.desc()).all()
    skills = db.query(Skill).all()
    skill_map = {s.id: s for s in skills}

    results = []
    for g in goals:
        sk = skill_map.get(g.skill_id)
        if sk:
            days_passed = (datetime.utcnow() - g.created_at).days
            days_rem = max(0, g.deadline_days - days_passed)
            prog = min(100.0, round((sk.level / g.target_level) * 100.0, 1))

            # Auto mark complete if target level reached
            is_completed = g.completed or (sk.level >= g.target_level)

            results.append(GoalResponse(
                id=g.id,
                title=g.title,
                skill_id=sk.id,
                skill_name=sk.name,
                skill_category=sk.category,
                current_level=sk.level,
                target_level=g.target_level,
                progress_pct=prog,
                deadline_days=g.deadline_days,
                days_remaining=days_rem,
                completed=is_completed,
                created_at=g.created_at
            ))

    return results

@router.post("", response_model=GoalResponse)
def create_goal(goal_in: GoalCreate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == goal_in.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    goal = Goal(
        title=goal_in.title,
        skill_id=goal_in.skill_id,
        target_level=goal_in.target_level,
        deadline_days=goal_in.deadline_days,
        completed=False,
        created_at=datetime.utcnow()
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    prog = min(100.0, round((skill.level / goal.target_level) * 100.0, 1))
    return GoalResponse(
        id=goal.id,
        title=goal.title,
        skill_id=skill.id,
        skill_name=skill.name,
        skill_category=skill.category,
        current_level=skill.level,
        target_level=goal.target_level,
        progress_pct=prog,
        deadline_days=goal.deadline_days,
        days_remaining=goal.deadline_days,
        completed=False,
        created_at=goal.created_at
    )

@router.put("/{goal_id}/toggle", response_model=GoalResponse)
def toggle_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.completed = not goal.completed
    db.commit()
    db.refresh(goal)

    skill = db.query(Skill).filter(Skill.id == goal.skill_id).first()
    days_passed = (datetime.utcnow() - goal.created_at).days
    days_rem = max(0, goal.deadline_days - days_passed)
    prog = min(100.0, round((skill.level / goal.target_level) * 100.0, 1)) if skill else 0.0

    return GoalResponse(
        id=goal.id,
        title=goal.title,
        skill_id=goal.skill_id,
        skill_name=skill.name if skill else "Skill",
        skill_category=skill.category if skill else "General",
        current_level=skill.level if skill else 1,
        target_level=goal.target_level,
        progress_pct=prog,
        deadline_days=goal.deadline_days,
        days_remaining=days_rem,
        completed=goal.completed,
        created_at=goal.created_at
    )

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully", "id": goal_id}
