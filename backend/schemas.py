from pydantic import BaseModel, Field
from typing import Optional, List
import datetime as dt


class PrereqIn(BaseModel):
    prerequisite_id: int
    required_level: int = 3


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    category: str = "Custom"
    description: str = ""
    current_level: int = Field(1, ge=1, le=100)
    target_level: int = Field(10, ge=1, le=100)
    prerequisites: List[PrereqIn] = []
    pos_x: float = 0
    pos_y: float = 0


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    target_level: Optional[int] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None


class PrereqOut(BaseModel):
    id: int
    name: str
    required_level: int
    met: bool

    class Config:
        from_attributes = True


class SkillOut(BaseModel):
    id: int
    name: str
    category: str
    description: str
    level: int
    xp: float
    xp_for_next: float
    xp_into_level: float
    progress_pct: float
    target_level: int
    status: str  # locked, available, in_progress, mastered
    pos_x: float
    pos_y: float
    prerequisites: List[PrereqOut] = []

    class Config:
        from_attributes = True


class LearningSessionCreate(BaseModel):
    skill_id: int
    duration_minutes: int = Field(..., gt=0, le=600)
    activity: str = ""
    difficulty: str = "Medium"
    notes: str = ""
    deep_work: bool = False


class LearningSessionOut(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    duration_minutes: int
    activity: str
    difficulty: str
    notes: str
    xp_awarded: float
    xp_breakdown: list
    deep_work: bool
    session_date: str

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str
    skill_id: Optional[int] = None
    target_level: int = 10
    deadline_days: int = 90


class GoalOut(BaseModel):
    id: int
    title: str
    skill_id: Optional[int]
    skill_name: Optional[str] = None
    target_level: int
    deadline_days: int
    current_level: int = 0
    progress_pct: float = 0
    completed: bool
    created_at: dt.datetime

    class Config:
        from_attributes = True


class AchievementOut(BaseModel):
    code: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: Optional[dt.datetime] = None

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    level: int
    xp: float
    xp_for_next: float
    xp_into_level: float
    total_skills: int
    mastered: int
    in_progress: int
    locked: int
    available: int
    current_streak: int
    longest_streak: int
    xp_this_week: float
    weekly_hours: float
    recently_improved: list
    recommended: list
    active_goals: list
