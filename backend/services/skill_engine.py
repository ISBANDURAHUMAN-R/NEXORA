from typing import Dict, List, Set, Any
from sqlalchemy.orm import Session
from models import Skill, SkillPrerequisite

class SkillEngine:
    @staticmethod
    def get_skill_status(skill: Skill, skill_map: Dict[int, Skill]) -> str:
        """
        Determines the state of a skill:
        - MASTERED: Current level >= target_level (e.g. 10)
        - LOCKED: Any prerequisite is not met (prereq level < required_level)
        - IN_PROGRESS: Prerequisites met AND (level > 1 or xp > 0)
        - AVAILABLE: Prerequisites met AND level == 1 AND xp == 0
        """
        if skill.level >= skill.target_level:
            return "MASTERED"

        # Check prerequisites
        for prereq_rel in skill.prerequisites:
            parent = skill_map.get(prereq_rel.prerequisite_id)
            if not parent:
                continue
            if parent.level < prereq_rel.required_level:
                return "LOCKED"

        if skill.level > 1 or skill.xp > 0:
            return "IN_PROGRESS"

        return "AVAILABLE"

    @staticmethod
    def check_prerequisites_met(skill: Skill, skill_map: Dict[int, Skill]) -> bool:
        for prereq_rel in skill.prerequisites:
            parent = skill_map.get(prereq_rel.prerequisite_id)
            if not parent or parent.level < prereq_rel.required_level:
                return False
        return True

    @staticmethod
    def get_prerequisite_details(skill: Skill, skill_map: Dict[int, Skill]) -> List[Dict[str, Any]]:
        details = []
        for prereq_rel in skill.prerequisites:
            parent = skill_map.get(prereq_rel.prerequisite_id)
            if parent:
                details.append({
                    "id": prereq_rel.id,
                    "skill_id": skill.id,
                    "prerequisite_id": parent.id,
                    "prerequisite_name": parent.name,
                    "required_level": prereq_rel.required_level,
                    "current_level": parent.level,
                    "is_satisfied": parent.level >= prereq_rel.required_level
                })
        return details

    @staticmethod
    def detect_cycle(db: Session, skill_id: int, new_prerequisite_id: int) -> bool:
        """
        Returns True if adding (skill_id requires new_prerequisite_id) would create a cycle.
        A cycle occurs if new_prerequisite_id already depends (directly or transitively) on skill_id.
        """
        if skill_id == new_prerequisite_id:
            return True

        visited: Set[int] = set()
        queue = [new_prerequisite_id]

        while queue:
            curr = queue.pop(0)
            if curr == skill_id:
                return True
            if curr in visited:
                continue
            visited.add(curr)

            # Get parents of curr
            parents = db.query(SkillPrerequisite).filter(SkillPrerequisite.skill_id == curr).all()
            for p in parents:
                if p.prerequisite_id not in visited:
                    queue.append(p.prerequisite_id)

        return False
