import os
import json
import datetime as dt
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from dotenv import load_dotenv

from database import Base, engine, get_db
import models
import schemas
from services.xp_engine import calculate_xp, level_progress, xp_required_cumulative
from services.skill_engine import serialize_skill, skill_status, sync_skill_level, prereqs_met
from services.recommendation import recommend_skills
from services.achievement_engine import ACHIEVEMENT_DEFS, ensure_achievement_rows, check_achievements
from seed import seed_demo_data

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillTree API", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_or_create_user(db: Session) -> models.User:
    user = db.query(models.User).first()
    if not user:
        user = seed_demo_data(db)
    return user


@app.on_event("startup")
def startup():
    db = next(get_db())
    ensure_achievement_rows(db)
    get_or_create_user(db)


# ---------------------------------------------------------------- dashboard
@app.get("/api/dashboard", response_model=schemas.DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    skills = db.query(models.Skill).filter(models.Skill.user_id == user.id).all()

    statuses = [skill_status(db, s) for s in skills]
    mastered = statuses.count("mastered")
    in_progress = statuses.count("in_progress")
    locked = statuses.count("locked")
    available = statuses.count("available")

    week_ago = (dt.date.today() - dt.timedelta(days=7)).isoformat()
    xp_this_week = (
        db.query(func.coalesce(func.sum(models.DailyStats.xp_gained), 0.0))
        .filter(models.DailyStats.user_id == user.id, models.DailyStats.date >= week_ago)
        .scalar()
    )
    minutes_this_week = (
        db.query(func.coalesce(func.sum(models.DailyStats.minutes_learned), 0))
        .filter(models.DailyStats.user_id == user.id, models.DailyStats.date >= week_ago)
        .scalar()
    )

    recent_sessions = (
        db.query(models.LearningSession)
        .filter(models.LearningSession.user_id == user.id)
        .order_by(models.LearningSession.created_at.desc())
        .limit(5)
        .all()
    )
    recently_improved = [
        {"skill_id": s.skill_id, "skill_name": s.skill.name if s.skill else "Unknown",
         "xp_awarded": s.xp_awarded, "date": s.session_date}
        for s in recent_sessions
    ]

    recommended = recommend_skills(db, user.id, limit=3)

    goals = db.query(models.Goal).filter(models.Goal.user_id == user.id, models.Goal.completed == False).limit(3).all()
    active_goals = []
    for g in goals:
        current_level = g.skill.level if g.skill else 0
        pct = round(min(100, (current_level / g.target_level) * 100), 1) if g.target_level else 0
        active_goals.append({
            "id": g.id, "title": g.title, "target_level": g.target_level,
            "current_level": current_level, "progress_pct": pct, "deadline_days": g.deadline_days,
        })

    prog = level_progress(user.total_xp)

    return schemas.DashboardOut(
        level=user.level or prog["level"],
        xp=user.total_xp,
        xp_for_next=prog["xp_for_next"],
        xp_into_level=prog["xp_into_level"],
        total_skills=len(skills),
        mastered=mastered,
        in_progress=in_progress,
        locked=locked,
        available=available,
        current_streak=user.current_streak,
        longest_streak=user.longest_streak,
        xp_this_week=round(xp_this_week or 0, 1),
        weekly_hours=round((minutes_this_week or 0) / 60, 1),
        recently_improved=recently_improved,
        recommended=recommended,
        active_goals=active_goals,
    )


# ------------------------------------------------------------------ skills
@app.get("/api/skills", response_model=List[schemas.SkillOut])
def list_skills(db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    skills = db.query(models.Skill).filter(models.Skill.user_id == user.id).all()
    return [serialize_skill(db, s) for s in skills]


@app.get("/api/skills/{skill_id}", response_model=schemas.SkillOut)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return serialize_skill(db, skill)


@app.post("/api/skills", response_model=schemas.SkillOut)
def create_skill(payload: schemas.SkillCreate, db: Session = Depends(get_db)):
    user = get_or_create_user(db)

    if payload.target_level < payload.current_level:
        raise HTTPException(status_code=400, detail="Target level must be >= current level")

    existing = db.query(models.Skill).filter(
        models.Skill.user_id == user.id, func.lower(models.Skill.name) == payload.name.lower()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A skill with this name already exists")

    xp = xp_required_cumulative(payload.current_level)
    skill = models.Skill(
        user_id=user.id, name=payload.name, category=payload.category,
        description=payload.description, level=payload.current_level, xp=xp,
        target_level=payload.target_level, pos_x=payload.pos_x, pos_y=payload.pos_y,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)

    for p in payload.prerequisites:
        prereq_skill = db.query(models.Skill).filter(models.Skill.id == p.prerequisite_id).first()
        if not prereq_skill:
            continue
        db.add(models.SkillPrerequisite(
            skill_id=skill.id, prerequisite_id=p.prerequisite_id, required_level=p.required_level
        ))
    db.commit()
    db.refresh(skill)
    return serialize_skill(db, skill)


@app.put("/api/skills/{skill_id}", response_model=schemas.SkillOut)
def update_skill(skill_id: int, payload: schemas.SkillUpdate, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(skill, field, value)
    db.commit()
    db.refresh(skill)
    return serialize_skill(db, skill)


@app.delete("/api/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.query(models.SkillPrerequisite).filter(
        (models.SkillPrerequisite.skill_id == skill_id) | (models.SkillPrerequisite.prerequisite_id == skill_id)
    ).delete()
    db.delete(skill)
    db.commit()
    return {"success": True}


@app.get("/api/skill-tree")
def get_skill_tree(db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    skills = db.query(models.Skill).filter(models.Skill.user_id == user.id).all()
    nodes = [serialize_skill(db, s) for s in skills]
    edges = []
    for s in skills:
        for p in s.prereqs:
            edges.append({"from": p.prerequisite_id, "to": s.id, "met": p.prerequisite.level >= p.required_level if p.prerequisite else False})
    return {"nodes": nodes, "edges": edges}


# --------------------------------------------------------------- learning
def _is_consistent_day(db: Session, user: models.User) -> bool:
    yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    return db.query(models.LearningSession).filter(
        models.LearningSession.user_id == user.id, models.LearningSession.session_date == yesterday
    ).first() is not None


def _update_streak(db: Session, user: models.User):
    today = dt.date.today().isoformat()
    yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    if user.last_active_date == today:
        return
    if user.last_active_date == yesterday:
        user.current_streak += 1
    else:
        user.current_streak = 1
    user.longest_streak = max(user.longest_streak, user.current_streak)
    user.last_active_date = today


@app.get("/api/learning", response_model=List[schemas.LearningSessionOut])
def list_learning_sessions(skill_id: Optional[int] = None, limit: int = 50, db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    q = db.query(models.LearningSession).filter(models.LearningSession.user_id == user.id)
    if skill_id:
        q = q.filter(models.LearningSession.skill_id == skill_id)
    sessions = q.order_by(models.LearningSession.created_at.desc()).limit(limit).all()
    out = []
    for s in sessions:
        try:
            breakdown = json.loads(s.xp_breakdown)
        except Exception:
            breakdown = []
        out.append(schemas.LearningSessionOut(
            id=s.id, skill_id=s.skill_id, skill_name=s.skill.name if s.skill else "Unknown",
            duration_minutes=s.duration_minutes, activity=s.activity, difficulty=s.difficulty,
            notes=s.notes, xp_awarded=s.xp_awarded, xp_breakdown=breakdown, deep_work=s.deep_work,
            session_date=s.session_date,
        ))
    return out


@app.post("/api/learning", response_model=schemas.LearningSessionOut)
def create_learning_session(payload: schemas.LearningSessionCreate, db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    skill = db.query(models.Skill).filter(models.Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if payload.difficulty not in ("Easy", "Medium", "Hard"):
        raise HTTPException(status_code=400, detail="Difficulty must be Easy, Medium, or Hard")

    # 1. calculate XP server-side (never trust the frontend)
    consistent = _is_consistent_day(db, user)
    xp, breakdown = calculate_xp(payload.duration_minutes, payload.difficulty, payload.deep_work, consistent)

    prev_level = skill.level

    # 2. save activity
    sess = models.LearningSession(
        user_id=user.id, skill_id=skill.id, duration_minutes=payload.duration_minutes,
        activity=payload.activity, difficulty=payload.difficulty, notes=payload.notes,
        xp_awarded=xp, xp_breakdown=json.dumps(breakdown), deep_work=payload.deep_work,
        session_date=dt.date.today().isoformat(),
    )
    db.add(sess)

    # 3. update skill progress + 4. update skill level
    skill.xp += xp
    sync_skill_level(skill)

    # account-level xp + level
    prev_account_level = level_progress(user.total_xp)["level"]
    user.total_xp += xp
    new_account_level = level_progress(user.total_xp)["level"]
    user.level = new_account_level
    leveled_up = new_account_level > prev_account_level

    # 5. streak
    _update_streak(db, user)

    # 6. daily stats
    today = dt.date.today().isoformat()
    stat = db.query(models.DailyStats).filter(models.DailyStats.user_id == user.id, models.DailyStats.date == today).first()
    if not stat:
        stat = models.DailyStats(user_id=user.id, date=today, xp_gained=0, minutes_learned=0, sessions_count=0)
        db.add(stat)
    stat.xp_gained += xp
    stat.minutes_learned += payload.duration_minutes
    stat.sessions_count += 1

    db.commit()
    db.refresh(sess)

    # 7. check achievements
    check_achievements(db, user, leveled_up=leveled_up)

    return schemas.LearningSessionOut(
        id=sess.id, skill_id=skill.id, skill_name=skill.name, duration_minutes=sess.duration_minutes,
        activity=sess.activity, difficulty=sess.difficulty, notes=sess.notes, xp_awarded=sess.xp_awarded,
        xp_breakdown=breakdown, deep_work=sess.deep_work, session_date=sess.session_date,
    )


@app.delete("/api/learning/{session_id}")
def delete_learning_session(session_id: int, db: Session = Depends(get_db)):
    sess = db.query(models.LearningSession).filter(models.LearningSession.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(sess)
    db.commit()
    return {"success": True}


# -------------------------------------------------------------- analytics
@app.get("/api/analytics")
def get_analytics(range: str = "30d", db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    days_map = {"7d": 7, "30d": 30, "90d": 90, "all": 3650}
    days = days_map.get(range, 30)
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()

    stats = (
        db.query(models.DailyStats)
        .filter(models.DailyStats.user_id == user.id, models.DailyStats.date >= since)
        .order_by(models.DailyStats.date.asc())
        .all()
    )
    xp_over_time = [{"date": s.date, "xp": s.xp_gained} for s in stats]
    learning_hours = [{"date": s.date, "hours": round(s.minutes_learned / 60, 2)} for s in stats]

    sessions = (
        db.query(models.LearningSession)
        .filter(models.LearningSession.user_id == user.id, models.LearningSession.session_date >= since)
        .all()
    )

    category_totals = {}
    skill_totals = {}
    for s in sessions:
        if s.skill:
            category_totals[s.skill.category] = category_totals.get(s.skill.category, 0) + s.duration_minutes
            skill_totals[s.skill.name] = skill_totals.get(s.skill.name, 0) + s.duration_minutes

    category_distribution = [{"category": k, "minutes": v} for k, v in category_totals.items()]
    most_practiced = sorted(
        [{"skill": k, "minutes": v} for k, v in skill_totals.items()], key=lambda x: x["minutes"], reverse=True
    )[:8]

    skills = db.query(models.Skill).filter(models.Skill.user_id == user.id).all()
    skill_growth = [{"skill": s.name, "level": s.level, "category": s.category} for s in skills]

    # weekly consistency: sessions per weekday
    weekday_counts = [0] * 7
    for s in sessions:
        d = dt.date.fromisoformat(s.session_date)
        weekday_counts[d.weekday()] += 1
    weekly_consistency = [
        {"day": day, "sessions": count}
        for day, count in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], weekday_counts)
    ]

    return {
        "xp_over_time": xp_over_time,
        "learning_hours": learning_hours,
        "category_distribution": category_distribution,
        "most_practiced": most_practiced,
        "skill_growth": skill_growth,
        "weekly_consistency": weekly_consistency,
    }


# ------------------------------------------------------------------ goals
@app.get("/api/goals", response_model=List[schemas.GoalOut])
def list_goals(db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    goals = db.query(models.Goal).filter(models.Goal.user_id == user.id).all()
    out = []
    for g in goals:
        current_level = g.skill.level if g.skill else 0
        pct = round(min(100, (current_level / g.target_level) * 100), 1) if g.target_level else 0
        out.append(schemas.GoalOut(
            id=g.id, title=g.title, skill_id=g.skill_id, skill_name=g.skill.name if g.skill else None,
            target_level=g.target_level, deadline_days=g.deadline_days, current_level=current_level,
            progress_pct=pct, completed=g.completed, created_at=g.created_at,
        ))
    return out


@app.post("/api/goals", response_model=schemas.GoalOut)
def create_goal(payload: schemas.GoalCreate, db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    if payload.skill_id:
        skill = db.query(models.Skill).filter(models.Skill.id == payload.skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
    goal = models.Goal(
        user_id=user.id, skill_id=payload.skill_id, title=payload.title,
        target_level=payload.target_level, deadline_days=payload.deadline_days,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    current_level = goal.skill.level if goal.skill else 0
    pct = round(min(100, (current_level / goal.target_level) * 100), 1) if goal.target_level else 0
    return schemas.GoalOut(
        id=goal.id, title=goal.title, skill_id=goal.skill_id, skill_name=goal.skill.name if goal.skill else None,
        target_level=goal.target_level, deadline_days=goal.deadline_days, current_level=current_level,
        progress_pct=pct, completed=goal.completed, created_at=goal.created_at,
    )


@app.delete("/api/goals/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"success": True}


# ------------------------------------------------------------ achievements
@app.get("/api/achievements", response_model=List[schemas.AchievementOut])
def list_achievements(db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    ensure_achievement_rows(db)
    achievements = db.query(models.Achievement).all()
    unlocked = {
        ua.achievement_id: ua.unlocked_at
        for ua in db.query(models.UserAchievement).filter(models.UserAchievement.user_id == user.id).all()
    }
    out = []
    for a in achievements:
        out.append(schemas.AchievementOut(
            code=a.code, name=a.name, description=a.description, icon=a.icon,
            unlocked=a.id in unlocked, unlocked_at=unlocked.get(a.id),
        ))
    return out


# -------------------------------------------------------------------- demo
@app.post("/api/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    user = seed_demo_data(db)
    return {"success": True, "message": "Demo data has been reset."}


@app.get("/api/health")
def health():
    return {"status": "ok"}
