from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Skill, SkillPrerequisite
from schemas import SkillTreeResponse, TreeNode, TreeEdge
from services.skill_engine import SkillEngine
from services.level_engine import LevelEngine

router = APIRouter(prefix="/api/skill-tree", tags=["Skill Tree"])

@router.get("", response_model=SkillTreeResponse)
def get_skill_tree(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    skill_map = {s.id: s for s in skills}
    prereqs = db.query(SkillPrerequisite).all()

    nodes = []
    status_counts = {"MASTERED": 0, "IN_PROGRESS": 0, "LOCKED": 0, "AVAILABLE": 0}

    for s in skills:
        status = SkillEngine.get_skill_status(s, skill_map)
        status_counts[status] = status_counts.get(status, 0) + 1
        _, cur_xp, next_xp, pct = LevelEngine.calculate_skill_level_from_xp(s.xp, s.target_level)
        prereqs_met = SkillEngine.check_prerequisites_met(s, skill_map)

        prereq_names = []
        for p in s.prerequisites:
            parent = skill_map.get(p.prerequisite_id)
            if parent:
                prereq_names.append(parent.name)

        nodes.append(TreeNode(
            id=str(s.id),
            name=s.name,
            slug=s.slug,
            category=s.category,
            level=s.level,
            target_level=s.target_level,
            xp=s.xp,
            current_level_xp=cur_xp,
            next_level_xp=next_xp,
            progress_pct=pct,
            status=status,
            icon=s.icon,
            color=s.color,
            x=s.position_x,
            y=s.position_y,
            prerequisites_met=prereqs_met,
            prerequisite_names=prereq_names
        ))

    edges = []
    for pr in prereqs:
        parent = skill_map.get(pr.prerequisite_id)
        child = skill_map.get(pr.skill_id)
        if parent and child:
            is_active = parent.level >= pr.required_level
            edges.append(TreeEdge(
                id=f"e-{pr.prerequisite_id}-{pr.skill_id}",
                source=str(pr.prerequisite_id),
                target=str(pr.skill_id),
                required_level=pr.required_level,
                is_active=is_active
            ))

    return SkillTreeResponse(
        nodes=nodes,
        edges=edges,
        stats={
            "total": len(skills),
            "mastered": status_counts["MASTERED"],
            "in_progress": status_counts["IN_PROGRESS"],
            "locked": status_counts["LOCKED"],
            "available": status_counts["AVAILABLE"]
        }
    )
