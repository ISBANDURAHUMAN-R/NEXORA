import json
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import (
    User, Skill, LearningSession, Settings, DailyStats
)
from schemas import (
    LearningSessionCreate, LearningSessionResponse, SessionResultResponse,
    XpBreakdownItem
)
from services.xp_engine import XpEngine
from services.level_engine import LevelEngine
from services.achievement_engine import AchievementEngine

router = APIRouter(prefix="/api/learning", tags=["Learning"])

@router.get("", response_model=List[LearningSessionResponse])
def get_learning_sessions(
    skill_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(LearningSession).order_by(LearningSession.created_at.desc())
    if skill_id:
        query = query.filter(LearningSession.skill_id == skill_id)

    sessions = query.offset(offset).limit(limit).all()
    skills = db.query(Skill).all()
    skill_map = {s.id: s for s in skills}

    results = []
    for s in sessions:
        sk = skill_map.get(s.skill_id)
        bd = []
        try:
            bd_raw = json.loads(s.xp_breakdown) if s.xp_breakdown else []
            bd = [XpBreakdownItem(**item) for item in bd_raw]
        except Exception:
            bd = [XpBreakdownItem(label="XP Awarded", xp=s.xp_earned, icon="Zap")]

        results.append(LearningSessionResponse(
            id=s.id,
            skill_id=s.skill_id,
            skill_name=sk.name if sk else "Unknown Skill",
            skill_category=sk.category if sk else "General",
            duration_minutes=s.duration_minutes,
            activity=s.activity,
            difficulty=s.difficulty,
            notes=s.notes or "",
            is_deep_work=s.is_deep_work,
            xp_earned=s.xp_earned,
            xp_breakdown=bd,
            created_at=s.created_at
        ))

    return results

@router.post("", response_model=SessionResultResponse)
def record_learning_session(
    session_in: LearningSessionCreate,
    db: Session = Depends(get_db)
):
    # 1. Fetch skill
    skill = db.query(Skill).filter(Skill.id == session_in.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # 2. Fetch user and settings
    user = db.query(User).first()
    if not user:
        user = User(username="developer", level=1, total_xp=0)
        db.add(user)
        db.flush()

    settings = db.query(Settings).first()
    xp_30 = settings.xp_per_30min if settings else 10
    xp_60 = settings.xp_per_60min if settings else 25
    deep_pct = settings.deep_work_bonus_pct if settings else 10
    cons_pct = settings.consistency_bonus_pct if settings else 5

    # 3. Calculate Deterministic XP
    calc = XpEngine.calculate_session_xp(
        duration_minutes=session_in.duration_minutes,
        difficulty=session_in.difficulty,
        is_deep_work=session_in.is_deep_work,
        streak_days=user.streak_days,
        xp_per_30min=xp_30,
        xp_per_60min=xp_60,
        deep_work_bonus_pct=deep_pct,
        consistency_bonus_pct=cons_pct
    )
    xp_earned = calc["total_xp"]
    breakdown = calc["breakdown"]

    # 4. Update Skill Progress
    skill_level_before = skill.level
    skill.xp += xp_earned
    new_skill_level, _, _, _ = LevelEngine.calculate_skill_level_from_xp(skill.xp, skill.target_level)
    skill.level = new_skill_level
    skill_leveled_up = new_skill_level > skill_level_before

    # 5. Update User Level & XP
    user_level_before = user.level
    user.total_xp += xp_earned
    new_user_level, cur_xp, next_xp, _ = LevelEngine.calculate_user_level(user.total_xp)
    user.level = new_user_level
    user.current_level_xp = cur_xp
    user.next_level_xp = next_xp
    user_leveled_up = new_user_level > user_level_before

    # 6. Update Streak
    today = date.today()
    if user.last_active_date:
        diff_days = (today - user.last_active_date).days
        if diff_days == 1:
            user.streak_days += 1
        elif diff_days > 1:
            user.streak_days = 1
        # if diff_days == 0 (same day), maintain streak
    else:
        user.streak_days = 1
    user.last_active_date = today

    # 7. Update DailyStats
    today_str = today.strftime("%Y-%m-%d")
    daily = db.query(DailyStats).filter(DailyStats.date_str == today_str).first()
    if not daily:
        daily = DailyStats(date_str=today_str, xp_gained=0, minutes_spent=0, sessions_count=0)
        db.add(daily)
        db.flush()
    daily.xp_gained += xp_earned
    daily.minutes_spent += session_in.duration_minutes
    daily.sessions_count += 1

    # 8. Save Session
    new_session = LearningSession(
        skill_id=skill.id,
        duration_minutes=session_in.duration_minutes,
        activity=session_in.activity,
        difficulty=session_in.difficulty,
        notes=session_in.notes or "",
        is_deep_work=session_in.is_deep_work,
        xp_earned=xp_earned,
        xp_breakdown=json.dumps(breakdown),
        created_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    db.refresh(user)
    db.refresh(skill)

    # 9. Evaluate Achievements
    new_achievements = AchievementEngine.evaluate_achievements(db, user)

    bd_items = [XpBreakdownItem(**item) for item in breakdown]

    session_resp = LearningSessionResponse(
        id=new_session.id,
        skill_id=skill.id,
        skill_name=skill.name,
        skill_category=skill.category,
        duration_minutes=new_session.duration_minutes,
        activity=new_session.activity,
        difficulty=new_session.difficulty,
        notes=new_session.notes,
        is_deep_work=new_session.is_deep_work,
        xp_earned=new_session.xp_earned,
        xp_breakdown=bd_items,
        created_at=new_session.created_at
    )

    return SessionResultResponse(
        session=session_resp,
        xp_earned=xp_earned,
        xp_breakdown=bd_items,
        skill_level_before=skill_level_before,
        skill_level_after=new_skill_level,
        skill_leveled_up=skill_leveled_up,
        user_level_before=user_level_before,
        user_level_after=new_user_level,
        user_leveled_up=user_leveled_up,
        new_achievements=new_achievements
    )

@router.delete("/{session_id}")
def delete_learning_session(session_id: int, db: Session = Depends(get_db)):
    sess = db.query(LearningSession).filter(LearningSession.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(sess)
    db.commit()
    return {"message": "Session deleted successfully", "id": session_id}
