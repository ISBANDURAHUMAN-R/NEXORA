from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Skill, LearningSession, DailyStats
from schemas import (
    AnalyticsResponse, XpHistoryPoint, LearningHoursPoint,
    CategoryDistribution, PracticedSkillItem
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

CATEGORY_COLORS = {
    "Programming": "#06b6d4",
    "AI/ML": "#a855f7",
    "Data Science": "#3b82f6",
    "Computer Science": "#ec4899",
    "Mathematics": "#8b5cf6",
    "DevOps": "#f97316",
    "Design": "#10b981",
    "Cybersecurity": "#ef4444",
    "Communication": "#14b8a6",
    "Business": "#eab308",
    "Custom": "#64748b"
}

@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    timeframe: str = Query("30d", pattern="^(7d|30d|90d|all)$"),
    db: Session = Depends(get_db)
):
    user = db.query(User).first()
    streak = user.streak_days if user else 1

    # Date filter calculation
    days_map = {"7d": 7, "30d": 30, "90d": 90, "all": 365}
    num_days = days_map.get(timeframe, 30)
    cutoff_date = datetime.utcnow() - timedelta(days=num_days)

    sessions = db.query(LearningSession).filter(LearningSession.created_at >= cutoff_date).all()
    all_skills = db.query(Skill).all()
    skill_map = {s.id: s for s in all_skills}

    # Total stats in timeframe
    total_xp = sum(s.xp_earned for s in sessions)
    total_minutes = sum(s.duration_minutes for s in sessions)
    total_hours = round(total_minutes / 60.0, 1)
    total_sessions = len(sessions)

    # Daily aggregated points
    today = date.today()
    # Generate continuous date map for smooth charting
    chart_days = min(num_days, 60) if timeframe != "7d" else 7
    date_buckets: Dict[str, Dict[str, Any]] = {}
    for i in range(chart_days):
        d = today - timedelta(days=(chart_days - 1 - i))
        date_str = d.strftime("%Y-%m-%d")
        date_buckets[date_str] = {"xp": 0, "minutes": 0, "sessions": 0}

    for s in sessions:
        ds = s.created_at.strftime("%Y-%m-%d")
        if ds in date_buckets:
            date_buckets[ds]["xp"] += s.xp_earned
            date_buckets[ds]["minutes"] += s.duration_minutes
            date_buckets[ds]["sessions"] += 1

    # Format XP over time (with cumulative running total)
    xp_over_time: List[XpHistoryPoint] = []
    running_cumulative = 0
    for ds, data in date_buckets.items():
        running_cumulative += data["xp"]
        # Format date for display like "Sep 10"
        try:
            parsed = datetime.strptime(ds, "%Y-%m-%d")
            display_date = parsed.strftime("%b %d")
        except Exception:
            display_date = ds
        xp_over_time.append(XpHistoryPoint(
            date=display_date,
            xp=data["xp"],
            cumulative_xp=running_cumulative
        ))

    # Learning hours chart
    learning_hours_chart: List[LearningHoursPoint] = []
    for ds, data in date_buckets.items():
        try:
            parsed = datetime.strptime(ds, "%Y-%m-%d")
            display_date = parsed.strftime("%b %d")
        except Exception:
            display_date = ds
        learning_hours_chart.append(LearningHoursPoint(
            date=display_date,
            hours=round(data["minutes"] / 60.0, 1),
            sessions=data["sessions"]
        ))

    # Category distribution
    cat_stats: Dict[str, Dict[str, Any]] = {}
    for s in all_skills:
        cat = s.category or "Custom"
        if cat not in cat_stats:
            cat_stats[cat] = {"count": 0, "xp": 0, "minutes": 0}
        cat_stats[cat]["count"] += 1
        cat_stats[cat]["xp"] += s.xp

    for sess in sessions:
        sk = skill_map.get(sess.skill_id)
        if sk:
            cat = sk.category or "Custom"
            if cat in cat_stats:
                cat_stats[cat]["minutes"] += sess.duration_minutes

    category_distribution = []
    for cat, data in sorted(cat_stats.items(), key=lambda x: x[1]["xp"], reverse=True):
        category_distribution.append(CategoryDistribution(
            category=cat,
            skills_count=data["count"],
            total_xp=data["xp"],
            hours_spent=round(data["minutes"] / 60.0, 1),
            color=CATEGORY_COLORS.get(cat, "#64748b")
        ))

    # Most practiced skills
    skill_practice: Dict[int, Dict[str, Any]] = {}
    for sess in sessions:
        sid = sess.skill_id
        if sid not in skill_practice:
            skill_practice[sid] = {"minutes": 0, "xp": 0, "count": 0}
        skill_practice[sid]["minutes"] += sess.duration_minutes
        skill_practice[sid]["xp"] += sess.xp_earned
        skill_practice[sid]["count"] += 1

    most_practiced = []
    for sid, pdata in sorted(skill_practice.items(), key=lambda x: x[1]["minutes"], reverse=True)[:6]:
        sk = skill_map.get(sid)
        if sk:
            most_practiced.append(PracticedSkillItem(
                skill_id=sk.id,
                name=sk.name,
                category=sk.category,
                level=sk.level,
                total_minutes=pdata["minutes"],
                hours=round(pdata["minutes"] / 60.0, 1),
                xp_gained=pdata["xp"],
                sessions_count=pdata["count"]
            ))

    # Weekly consistency (Day of week breakdown: Mon-Sun)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dow_stats = {d: {"hours": 0.0, "sessions": 0, "xp": 0} for d in day_names}
    for sess in sessions:
        d_name = day_names[sess.created_at.weekday()]
        dow_stats[d_name]["hours"] += sess.duration_minutes / 60.0
        dow_stats[d_name]["sessions"] += 1
        dow_stats[d_name]["xp"] += sess.xp_earned

    weekly_consistency = [
        {"day": d, "hours": round(dow_stats[d]["hours"], 1), "sessions": dow_stats[d]["sessions"], "xp": dow_stats[d]["xp"]}
        for d in day_names
    ]

    return AnalyticsResponse(
        timeframe=timeframe,
        total_xp=total_xp,
        total_hours=total_hours,
        total_sessions=total_sessions,
        streak_days=streak,
        xp_over_time=xp_over_time,
        learning_hours_chart=learning_hours_chart,
        category_distribution=category_distribution,
        most_practiced_skills=most_practiced,
        weekly_consistency=weekly_consistency
    )
