from sqlalchemy.orm import Session
from models import Skill, SkillPrerequisite
from services.xp_engine import level_progress

MASTERY_LEVEL = 10


def prereqs_met(db: Session, skill: Skill) -> bool:
    for p in skill.prereqs:
        prereq_skill = p.prerequisite
        if not prereq_skill or prereq_skill.level < p.required_level:
            return False
    return True


def skill_status(db: Session, skill: Skill) -> str:
    if skill.level >= MASTERY_LEVEL:
        return "mastered"
    if skill.xp > 0 or skill.level > 1:
        return "in_progress"
    if prereqs_met(db, skill):
        return "available"
    return "locked"


def serialize_skill(db: Session, skill: Skill) -> dict:
    prog = level_progress(skill.xp)
    prereq_out = []
    for p in skill.prereqs:
        prereq_skill = p.prerequisite
        prereq_out.append({
            "id": prereq_skill.id if prereq_skill else p.prerequisite_id,
            "name": prereq_skill.name if prereq_skill else "Unknown",
            "required_level": p.required_level,
            "met": bool(prereq_skill and prereq_skill.level >= p.required_level),
        })
    return {
        "id": skill.id,
        "name": skill.name,
        "category": skill.category,
        "description": skill.description,
        "level": prog["level"],
        "xp": skill.xp,
        "xp_for_next": prog["xp_for_next"],
        "xp_into_level": prog["xp_into_level"],
        "progress_pct": prog["progress_pct"],
        "target_level": skill.target_level,
        "status": skill_status(db, skill),
        "pos_x": skill.pos_x,
        "pos_y": skill.pos_y,
        "prerequisites": prereq_out,
    }


def sync_skill_level(skill: Skill):
    """Keep skill.level consistent with skill.xp using the shared curve."""
    prog = level_progress(skill.xp)
    skill.level = prog["level"]
