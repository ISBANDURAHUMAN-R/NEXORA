"""
Rule-based (non-AI) recommendation engine.

Scoring heuristic per candidate skill:
  + 40 pts  if all prerequisites are met (i.e. it's "available")
  + up to 30 pts based on how close prerequisites are to being met (avg readiness)
  + 15 pts  if it directly unlocks a skill tied to an active goal
  + up to 15 pts for recent momentum: bonus if a prerequisite skill was
    practiced in the last 7 days (keeps recommendations relevant to recent activity)
  - skills already mastered or already deep in progress score lower priority
    (we want to surface the *next* logical step, not what's already moving)

The top-ranked skills are returned with a plain-English reason.
"""
from sqlalchemy.orm import Session
from models import Skill, LearningSession, Goal
from services.skill_engine import skill_status, prereqs_met
import datetime as dt


def _readiness(db: Session, skill: Skill) -> float:
    """0-1 score of how close prerequisites are to being satisfied."""
    if not skill.prereqs:
        return 1.0
    total = 0.0
    for p in skill.prereqs:
        prereq = p.prerequisite
        if not prereq:
            continue
        total += min(1.0, prereq.level / max(1, p.required_level))
    return total / len(skill.prereqs)


def _recent_momentum(db: Session, skill: Skill) -> bool:
    cutoff = (dt.date.today() - dt.timedelta(days=7)).isoformat()
    prereq_ids = [p.prerequisite_id for p in skill.prereqs]
    if not prereq_ids:
        return False
    count = (
        db.query(LearningSession)
        .filter(LearningSession.skill_id.in_(prereq_ids))
        .filter(LearningSession.session_date >= cutoff)
        .count()
    )
    return count > 0


def recommend_skills(db: Session, user_id: int, limit: int = 4):
    skills = db.query(Skill).filter(Skill.user_id == user_id).all()
    goal_skill_ids = {
        g.skill_id for g in db.query(Goal).filter(Goal.user_id == user_id, Goal.completed == False).all()
        if g.skill_id
    }

    scored = []
    for s in skills:
        status = skill_status(db, s)
        if status == "mastered":
            continue

        score = 0.0
        reasons = []

        if status == "available":
            score += 40
            reasons.append("all prerequisites are met")
        else:
            readiness = _readiness(db, s)
            score += 30 * readiness
            if readiness > 0:
                reasons.append(f"prerequisites are {round(readiness * 100)}% ready")

        if s.id in goal_skill_ids:
            score += 15
            reasons.append("tied to one of your active goals")

        if _recent_momentum(db, s):
            score += 15
            reasons.append("builds on skills you've practiced recently")

        # Slight penalty for skills already well in progress (surface *next* steps)
        if status == "in_progress" and s.level >= 5:
            score -= 10

        scored.append((score, s, reasons, status))

    scored.sort(key=lambda t: t[0], reverse=True)

    out = []
    for score, s, reasons, status in scored[:limit]:
        reason_text = "Recommended because " + " and ".join(reasons) if reasons else \
            "A solid next step based on your current progress"
        out.append({
            "skill_id": s.id,
            "name": s.name,
            "category": s.category,
            "level": s.level,
            "status": status,
            "score": round(score, 1),
            "reason": reason_text,
        })
    return out
