from sqlalchemy.orm import Session
from models import User, Skill, LearningSession, Achievement, UserAchievement

ACHIEVEMENT_DEFS = [
    {"code": "first_step", "name": "First Step", "description": "Complete your first learning session.", "icon": "footprints"},
    {"code": "consistent", "name": "Consistent", "description": "Maintain a 7-day learning streak.", "icon": "flame"},
    {"code": "deep_worker", "name": "Deep Worker", "description": "Complete 10 deep-work sessions.", "icon": "brain"},
    {"code": "level_up", "name": "Level Up", "description": "Reach a new overall level.", "icon": "arrow-up-circle"},
    {"code": "master", "name": "Master", "description": "Master your first skill.", "icon": "award"},
    {"code": "multi_talent", "name": "Multi-Talent", "description": "Reach Level 5 in five different skills.", "icon": "layers"},
]


def ensure_achievement_rows(db: Session):
    existing = {a.code for a in db.query(Achievement).all()}
    for d in ACHIEVEMENT_DEFS:
        if d["code"] not in existing:
            db.add(Achievement(**d))
    db.commit()


def _unlock(db: Session, user_id: int, code: str, newly_unlocked: list):
    achievement = db.query(Achievement).filter(Achievement.code == code).first()
    if not achievement:
        return
    already = (
        db.query(UserAchievement)
        .filter(UserAchievement.user_id == user_id, UserAchievement.achievement_id == achievement.id)
        .first()
    )
    if not already:
        db.add(UserAchievement(user_id=user_id, achievement_id=achievement.id))
        newly_unlocked.append(achievement.name)


def check_achievements(db: Session, user: User, leveled_up: bool = False) -> list:
    """Run after a learning session or level change. Returns list of newly unlocked names."""
    newly_unlocked = []
    ensure_achievement_rows(db)

    session_count = db.query(LearningSession).filter(LearningSession.user_id == user.id).count()
    if session_count >= 1:
        _unlock(db, user.id, "first_step", newly_unlocked)

    if user.current_streak >= 7:
        _unlock(db, user.id, "consistent", newly_unlocked)

    deep_count = (
        db.query(LearningSession)
        .filter(LearningSession.user_id == user.id, LearningSession.deep_work == True)
        .count()
    )
    if deep_count >= 10:
        _unlock(db, user.id, "deep_worker", newly_unlocked)

    if leveled_up:
        _unlock(db, user.id, "level_up", newly_unlocked)

    mastered_count = db.query(Skill).filter(Skill.user_id == user.id, Skill.level >= 10).count()
    if mastered_count >= 1:
        _unlock(db, user.id, "master", newly_unlocked)

    high_level_skills = db.query(Skill).filter(Skill.user_id == user.id, Skill.level >= 5).count()
    if high_level_skills >= 5:
        _unlock(db, user.id, "multi_talent", newly_unlocked)

    db.commit()
    return newly_unlocked
