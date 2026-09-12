from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from models import User, Skill, LearningSession, Achievement, UserAchievement

DEFAULT_ACHIEVEMENTS = [
    {
        "code": "FIRST_STEP",
        "title": "First Step",
        "description": "Complete your first learning session",
        "icon": "Footprints",
        "category": "Getting Started",
        "target_value": 1
    },
    {
        "code": "CONSISTENT",
        "title": "Consistent",
        "description": "Maintain a 7-day learning streak",
        "icon": "Flame",
        "category": "Discipline",
        "target_value": 7
    },
    {
        "code": "DEEP_WORKER",
        "title": "Deep Worker",
        "description": "Complete 10 deep work sessions",
        "icon": "Brain",
        "category": "Focus",
        "target_value": 10
    },
    {
        "code": "LEVEL_UP",
        "title": "Level Up",
        "description": "Reach overall level 5 or higher",
        "icon": "TrendingUp",
        "category": "Progression",
        "target_value": 5
    },
    {
        "code": "MASTER",
        "title": "Master",
        "description": "Master your first skill to its target level",
        "icon": "Award",
        "category": "Mastery",
        "target_value": 1
    },
    {
        "code": "MULTI_TALENT",
        "title": "Multi-Talent",
        "description": "Reach Level 5 in 5 different skills",
        "icon": "Sparkles",
        "category": "Versatility",
        "target_value": 5
    },
    {
        "code": "CENTURION",
        "title": "XP Centurion",
        "description": "Accumulate 1,000 total progression XP",
        "icon": "ShieldAlert",
        "category": "Progression",
        "target_value": 1000
    },
    {
        "code": "STUDIOUS",
        "title": "Dedicated Scholar",
        "description": "Log 25 total learning sessions",
        "icon": "BookOpen",
        "category": "Discipline",
        "target_value": 25
    }
]

class AchievementEngine:
    @staticmethod
    def ensure_achievements_exist(db: Session):
        """Seed achievement definitions if they don't exist."""
        for item in DEFAULT_ACHIEVEMENTS:
            existing = db.query(Achievement).filter(Achievement.code == item["code"]).first()
            if not existing:
                ach = Achievement(**item)
                db.add(ach)
                db.flush()
                # Create user_achievement tracking record
                db.add(UserAchievement(achievement_id=ach.id, unlocked=False, current_value=0))
        db.commit()

    @staticmethod
    def evaluate_achievements(db: Session, user: User) -> List[str]:
        """
        Evaluates criteria for all achievements.
        Returns list of newly unlocked achievement titles.
        """
        AchievementEngine.ensure_achievements_exist(db)

        # Gather stats
        total_sessions = db.query(LearningSession).count()
        deep_sessions = db.query(LearningSession).filter(LearningSession.is_deep_work == True).count()
        skills = db.query(Skill).all()
        mastered_count = sum(1 for s in skills if s.level >= s.target_level)
        level_5_count = sum(1 for s in skills if s.level >= 5)

        criteria = {
            "FIRST_STEP": total_sessions,
            "CONSISTENT": user.streak_days,
            "DEEP_WORKER": deep_sessions,
            "LEVEL_UP": user.level,
            "MASTER": mastered_count,
            "MULTI_TALENT": level_5_count,
            "CENTURION": user.total_xp,
            "STUDIOUS": total_sessions
        }

        user_achievements = db.query(UserAchievement).join(Achievement).all()
        newly_unlocked = []

        for ua in user_achievements:
            code = ua.achievement.code
            target = ua.achievement.target_value
            current_val = criteria.get(code, 0)
            ua.current_value = current_val

            if not ua.unlocked and current_val >= target:
                ua.unlocked = True
                ua.unlocked_at = datetime.utcnow()
                newly_unlocked.append(ua.achievement.title)

        db.commit()
        return newly_unlocked
