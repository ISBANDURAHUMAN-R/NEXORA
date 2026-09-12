from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Skill, LearningSession, Goal, Settings, DailyStats
from schemas import DashboardResponse, SkillSimple, GoalResponse, LearningSessionResponse, XpBreakdownItem
from services.level_engine import LevelEngine
from services.skill_engine import SkillEngine
from services.recommendation import RecommendationEngine
import json

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        # Fallback create user
        user = User(username="developer", level=1, total_xp=0)
        db.add(user)
        db.commit()
        db.refresh(user)

    settings = db.query(Settings).first()
    is_demo_mode = settings.is_demo_mode if settings else True

    # Recalculate level details
    lvl, cur_xp, next_xp, pct = LevelEngine.calculate_user_level(user.total_xp)

    # Skill counts
    all_skills = db.query(Skill).all()
    skill_map = {s.id: s for s in all_skills}

    status_counts = {"MASTERED": 0, "IN_PROGRESS": 0, "LOCKED": 0, "AVAILABLE": 0}
    for s in all_skills:
        status = SkillEngine.get_skill_status(s, skill_map)
        status_counts[status] = status_counts.get(status, 0) + 1

    # Weekly stats (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_sessions = db.query(LearningSession).filter(
        LearningSession.created_at >= seven_days_ago
    ).all()

    xp_this_week = sum(s.xp_earned for s in recent_sessions)
    weekly_learning_hours = round(sum(s.duration_minutes for s in recent_sessions) / 60.0, 1)

    # Recently improved skills (distinct skills from recent sessions or updated recently)
    recent_skill_ids = []
    for s in db.query(LearningSession).order_by(LearningSession.created_at.desc()).limit(10).all():
        if s.skill_id not in recent_skill_ids:
            recent_skill_ids.append(s.skill_id)

    recently_improved = []
    for sid in recent_skill_ids[:4]:
        sk = skill_map.get(sid)
        if sk:
            st = SkillEngine.get_skill_status(sk, skill_map)
            _, _, _, prog = LevelEngine.calculate_skill_level_from_xp(sk.xp, sk.target_level)
            recently_improved.append(SkillSimple(
                id=sk.id,
                name=sk.name,
                slug=sk.slug,
                category=sk.category,
                level=sk.level,
                xp=sk.xp,
                target_level=sk.target_level,
                icon=sk.icon,
                color=sk.color,
                status=st,
                progress_pct=prog
            ))

    # Recommendations
    recs = RecommendationEngine.recommend_skills(db, limit=4)

    # Current Goals
    active_goals = db.query(Goal).filter(Goal.completed == False).order_by(Goal.created_at.desc()).all()
    goals_resp = []
    for g in active_goals:
        sk = skill_map.get(g.skill_id)
        if sk:
            days_passed = (datetime.utcnow() - g.created_at).days
            days_rem = max(0, g.deadline_days - days_passed)
            prog = min(100.0, round((sk.level / g.target_level) * 100.0, 1))
            goals_resp.append(GoalResponse(
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
                completed=g.completed,
                created_at=g.created_at
            ))

    # Recent 5 sessions
    latest_sessions = db.query(LearningSession).order_by(LearningSession.created_at.desc()).limit(5).all()
    sessions_resp = []
    for s in latest_sessions:
        sk = skill_map.get(s.skill_id)
        bd = []
        try:
            bd_raw = json.loads(s.xp_breakdown) if s.xp_breakdown else []
            bd = [XpBreakdownItem(**item) for item in bd_raw]
        except Exception:
            bd = [XpBreakdownItem(label="XP Awarded", xp=s.xp_earned, icon="Zap")]

        sessions_resp.append(LearningSessionResponse(
            id=s.id,
            skill_id=s.skill_id,
            skill_name=sk.name if sk else "Unknown",
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

    return DashboardResponse(
        user_level=user.level,
        total_xp=user.total_xp,
        current_level_xp=cur_xp,
        next_level_xp=next_xp,
        level_progress_pct=pct,
        total_skills=len(all_skills),
        mastered_skills=status_counts["MASTERED"],
        in_progress_skills=status_counts["IN_PROGRESS"],
        locked_skills=status_counts["LOCKED"],
        available_skills=status_counts["AVAILABLE"],
        streak_days=user.streak_days,
        xp_this_week=xp_this_week,
        weekly_learning_hours=weekly_learning_hours,
        recently_improved=recently_improved,
        recommendations=recs,
        current_goals=goals_resp,
        recent_sessions=sessions_resp,
        is_demo_mode=is_demo_mode
    )
