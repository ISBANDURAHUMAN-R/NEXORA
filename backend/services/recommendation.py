from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Skill, SkillPrerequisite, Goal, LearningSession
from services.skill_engine import SkillEngine
from services.level_engine import LevelEngine

class RecommendationEngine:
    @staticmethod
    def recommend_skills(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        all_skills = db.query(Skill).all()
        skill_map = {s.id: s for s in all_skills}

        # Active goals mapping
        active_goals = db.query(Goal).filter(Goal.completed == False).all()
        goal_skill_ids = {g.skill_id: g for g in active_goals}

        # Recent sessions (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = db.query(LearningSession).filter(
            LearningSession.created_at >= seven_days_ago
        ).all()
        recent_skill_ids = {s.skill_id for s in recent_sessions}

        # Calculate downstream unlock potential for each skill
        prereq_counts: Dict[int, int] = {}
        for p in db.query(SkillPrerequisite).all():
            prereq_counts[p.prerequisite_id] = prereq_counts.get(p.prerequisite_id, 0) + 1

        scored_candidates = []

        for skill in all_skills:
            status = SkillEngine.get_skill_status(skill, skill_map)

            # Mastered skills don't need recommendation
            if status == "MASTERED":
                continue

            # Locked skills can only be recommended if very close or unlockable
            if status == "LOCKED":
                continue

            _, _, _, pct = LevelEngine.calculate_skill_level_from_xp(skill.xp, skill.target_level)

            score = 0.0
            reasons = []
            factors = []

            # 1. Goal alignment (Highest weight)
            if skill.id in goal_skill_ids:
                goal = goal_skill_ids[skill.id]
                score += 50.0
                reasons.append(f"Directly advances your goal '{goal.title}'")
                factors.append("Goal Target")

            # 2. Downstream unlocking value (Gateway skills)
            downstream_count = prereq_counts.get(skill.id, 0)
            if downstream_count > 0:
                score += min(downstream_count * 15.0, 45.0)
                reasons.append(f"Key gateway skill: unlocks {downstream_count} advanced node{'s' if downstream_count > 1 else ''}")
                factors.append(f"Unlocks {downstream_count} skills")

            # 3. In-Progress Momentum
            if status == "IN_PROGRESS":
                score += 25.0
                factors.append("Active Progression")
                if skill.id in recent_skill_ids:
                    score += 15.0
                    reasons.append("Maintains your active learning momentum from this week")
                    factors.append("Recent Momentum")
                else:
                    reasons.append("Already in progress with solid foundation")

            # 4. Freshly Available Skill
            elif status == "AVAILABLE":
                score += 30.0
                reasons.append("All prerequisites satisfied and ready to begin")
                factors.append("Prerequisites Met")

            # 5. Proximity to Level-Up sweet spot (e.g. 50% - 90% through current level)
            if 40.0 <= pct <= 95.0:
                score += 10.0
                factors.append(f"{int(pct)}% to next milestone")

            # Default fallback reason if list empty
            primary_reason = reasons[0] if reasons else f"Recommended next step in your {skill.category} roadmap"

            scored_candidates.append({
                "skill_id": skill.id,
                "skill_name": skill.name,
                "category": skill.category,
                "current_level": skill.level,
                "target_level": skill.target_level,
                "progress_pct": pct,
                "status": status,
                "score": round(score, 1),
                "reason": primary_reason,
                "key_factors": factors[:3]
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:limit]
