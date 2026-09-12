from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Achievement, UserAchievement, User
from schemas import AchievementResponse
from services.achievement_engine import AchievementEngine

router = APIRouter(prefix="/api/achievements", tags=["Achievements"])

@router.get("", response_model=List[AchievementResponse])
def get_achievements(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if user:
        AchievementEngine.evaluate_achievements(db, user)

    records = db.query(UserAchievement).join(Achievement).all()
    results = []

    for ua in records:
        ach = ua.achievement
        target = max(ach.target_value, 1)
        curr = ua.current_value
        pct = 100.0 if ua.unlocked else min(99.0, round((curr / target) * 100.0, 1))

        results.append(AchievementResponse(
            id=ach.id,
            code=ach.code,
            title=ach.title,
            description=ach.description,
            icon=ach.icon,
            category=ach.category,
            target_value=target,
            current_value=curr,
            progress_pct=pct,
            unlocked=ua.unlocked,
            unlocked_at=ua.unlocked_at
        ))

    # Sort unlocked first, then by progress percentage descending
    results.sort(key=lambda x: (not x.unlocked, -x.progress_pct))
    return results
