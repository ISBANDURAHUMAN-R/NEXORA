from typing import List, Optional
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Skill, SkillPrerequisite, LearningSession
from schemas import (
    SkillSimple, SkillResponse, SkillCreate, SkillUpdate,
    PrerequisiteInfo
)
from services.level_engine import LevelEngine
from services.skill_engine import SkillEngine

router = APIRouter(prefix="/api/skills", tags=["Skills"])

def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-")

@router.get("", response_model=List[SkillSimple])
def get_skills(
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Skill)
    if category and category != "All":
        query = query.filter(Skill.category == category)
    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))

    skills = query.all()
    all_skills = db.query(Skill).all()
    skill_map = {s.id: s for s in all_skills}

    result = []
    for s in skills:
        st = SkillEngine.get_skill_status(s, skill_map)
        if status and status != "ALL" and st != status:
            continue
        _, _, _, pct = LevelEngine.calculate_skill_level_from_xp(s.xp, s.target_level)
        result.append(SkillSimple(
            id=s.id,
            name=s.name,
            slug=s.slug,
            category=s.category,
            level=s.level,
            xp=s.xp,
            target_level=s.target_level,
            icon=s.icon,
            color=s.color,
            status=st,
            progress_pct=pct
        ))

    return result

@router.post("", response_model=SkillResponse)
def create_skill(skill_in: SkillCreate, db: Session = Depends(get_db)):
    base_slug = slugify(skill_in.name)
    slug = base_slug
    idx = 1
    while db.query(Skill).filter(Skill.slug == slug).first():
        slug = f"{base_slug}-{idx}"
        idx += 1

    # Calculate initial XP based on initial_level
    initial_xp = LevelEngine.skill_level_threshold(skill_in.initial_level)

    # Determine auto position if not set (0,0)
    pos_x = skill_in.position_x
    pos_y = skill_in.position_y
    if pos_x == 0 and pos_y == 0:
        count = db.query(Skill).count()
        pos_x = 100 + (count % 5) * 200
        pos_y = 100 + (count // 5) * 160

    new_skill = Skill(
        name=skill_in.name,
        slug=slug,
        category=skill_in.category,
        description=skill_in.description,
        level=skill_in.initial_level,
        xp=initial_xp,
        target_level=skill_in.target_level,
        icon=skill_in.icon or "Code",
        color=skill_in.color or "#06b6d4",
        position_x=pos_x,
        position_y=pos_y
    )
    db.add(new_skill)
    db.flush()

    # Add prerequisites
    for pid in skill_in.prerequisite_ids:
        if pid == new_skill.id:
            continue
        parent = db.query(Skill).filter(Skill.id == pid).first()
        if parent:
            pr = SkillPrerequisite(
                skill_id=new_skill.id,
                prerequisite_id=parent.id,
                required_level=1
            )
            db.add(pr)

    db.commit()
    db.refresh(new_skill)

    # Return full response
    return get_skill_detail(new_skill.id, db)

@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill_detail(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    all_skills = db.query(Skill).all()
    skill_map = {s.id: s for s in all_skills}

    status = SkillEngine.get_skill_status(skill, skill_map)
    _, cur_xp, next_xp, pct = LevelEngine.calculate_skill_level_from_xp(skill.xp, skill.target_level)

    # Prerequisites
    prereq_details = []
    for pr in skill.prerequisites:
        parent = skill_map.get(pr.prerequisite_id)
        if parent:
            prereq_details.append(PrerequisiteInfo(
                id=pr.id,
                skill_id=skill.id,
                prerequisite_id=parent.id,
                prerequisite_name=parent.name,
                required_level=pr.required_level,
                current_level=parent.level,
                is_satisfied=parent.level >= pr.required_level
            ))

    # Downstream skills that require this skill
    downstream = []
    for dn in skill.downstream:
        child = skill_map.get(dn.skill_id)
        if child:
            downstream.append(child.name)

    return SkillResponse(
        id=skill.id,
        name=skill.name,
        slug=skill.slug,
        category=skill.category,
        description=skill.description or "",
        level=skill.level,
        xp=skill.xp,
        target_level=skill.target_level,
        icon=skill.icon,
        color=skill.color,
        position_x=skill.position_x,
        position_y=skill.position_y,
        status=status,
        progress_pct=pct,
        current_level_xp=cur_xp,
        next_level_xp=next_xp,
        prerequisites=prereq_details,
        downstream_skills=downstream
    )

@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(skill_id: int, update_in: SkillUpdate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if update_in.name is not None:
        skill.name = update_in.name
    if update_in.category is not None:
        skill.category = update_in.category
    if update_in.description is not None:
        skill.description = update_in.description
    if update_in.target_level is not None:
        skill.target_level = update_in.target_level
    if update_in.icon is not None:
        skill.icon = update_in.icon
    if update_in.color is not None:
        skill.color = update_in.color
    if update_in.position_x is not None:
        skill.position_x = update_in.position_x
    if update_in.position_y is not None:
        skill.position_y = update_in.position_y

    if update_in.level is not None:
        skill.level = update_in.level
        # align xp if not provided
        if update_in.xp is None:
            skill.xp = LevelEngine.skill_level_threshold(skill.level)
    elif update_in.xp is not None:
        skill.xp = update_in.xp
        lvl, _, _, _ = LevelEngine.calculate_skill_level_from_xp(skill.xp, skill.target_level)
        skill.level = lvl

    # Prerequisites update if provided
    if update_in.prerequisite_ids is not None:
        # Check for cycles
        for pid in update_in.prerequisite_ids:
            if SkillEngine.detect_cycle(db, skill.id, pid):
                raise HTTPException(status_code=400, detail=f"Adding prerequisite ID {pid} creates a circular dependency")

        # Delete existing and re-add
        db.query(SkillPrerequisite).filter(SkillPrerequisite.skill_id == skill.id).delete()
        for pid in update_in.prerequisite_ids:
            if pid != skill.id:
                db.add(SkillPrerequisite(skill_id=skill.id, prerequisite_id=pid, required_level=1))

    db.commit()
    db.refresh(skill)
    return get_skill_detail(skill.id, db)

@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted successfully", "skill_id": skill_id}
