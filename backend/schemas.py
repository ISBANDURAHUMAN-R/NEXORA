from datetime import datetime, date
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# Prerequisite schemas
class PrerequisiteInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    skill_id: int
    prerequisite_id: int
    prerequisite_name: str
    required_level: int
    current_level: int
    is_satisfied: bool

class PrerequisiteCreate(BaseModel):
    prerequisite_id: int
    required_level: int = 1

# Skill schemas
class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field("Programming", max_length=50)
    description: str = ""
    target_level: int = Field(10, ge=1, le=100)
    icon: str = "Code"
    color: str = "#06b6d4"
    position_x: float = 0.0
    position_y: float = 0.0

class SkillCreate(SkillBase):
    initial_level: int = Field(1, ge=1, le=100)
    prerequisite_ids: List[int] = []

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    xp: Optional[int] = None
    target_level: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    prerequisite_ids: Optional[List[int]] = None

class SkillSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    category: str
    level: int
    xp: int
    target_level: int
    icon: str
    color: str
    status: str  # LOCKED, AVAILABLE, IN_PROGRESS, MASTERED
    progress_pct: float

class SkillResponse(SkillSimple):
    model_config = ConfigDict(from_attributes=True)
    description: str
    position_x: float
    position_y: float
    current_level_xp: int
    next_level_xp: int
    prerequisites: List[PrerequisiteInfo] = []
    downstream_skills: List[str] = []

# Tree visualization schemas
class TreeNode(BaseModel):
    id: str
    name: str
    slug: str
    category: str
    level: int
    target_level: int
    xp: int
    current_level_xp: int
    next_level_xp: int
    progress_pct: float
    status: str  # LOCKED, AVAILABLE, IN_PROGRESS, MASTERED
    icon: str
    color: str
    x: float
    y: float
    prerequisites_met: bool
    prerequisite_names: List[str] = []

class TreeEdge(BaseModel):
    id: str
    source: str
    target: str
    required_level: int
    is_active: bool

class SkillTreeResponse(BaseModel):
    nodes: List[TreeNode]
    edges: List[TreeEdge]
    stats: Dict[str, int]

# Learning Session schemas
class XpBreakdownItem(BaseModel):
    label: str
    xp: int
    icon: Optional[str] = None

class LearningSessionCreate(BaseModel):
    skill_id: int
    duration_minutes: int = Field(..., ge=5, le=1440)
    activity: str = Field(..., min_length=2, max_length=200)
    difficulty: str = Field("Medium", pattern="^(Easy|Medium|Hard)$")
    notes: Optional[str] = ""
    is_deep_work: bool = False

class LearningSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    skill_id: int
    skill_name: str
    skill_category: str
    duration_minutes: int
    activity: str
    difficulty: str
    notes: str
    is_deep_work: bool
    xp_earned: int
    xp_breakdown: List[XpBreakdownItem]
    created_at: datetime

class SessionResultResponse(BaseModel):
    session: LearningSessionResponse
    xp_earned: int
    xp_breakdown: List[XpBreakdownItem]
    skill_level_before: int
    skill_level_after: int
    skill_leveled_up: bool
    user_level_before: int
    user_level_after: int
    user_leveled_up: bool
    new_achievements: List[str] = []

# Goal schemas
class GoalCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    skill_id: int
    target_level: int = Field(..., ge=1, le=100)
    deadline_days: int = Field(30, ge=1, le=365)

class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    skill_id: int
    skill_name: str
    skill_category: str
    current_level: int
    target_level: int
    progress_pct: float
    deadline_days: int
    days_remaining: int
    completed: bool
    created_at: datetime

# Achievement schemas
class AchievementResponse(BaseModel):
    id: int
    code: str
    title: str
    description: str
    icon: str
    category: str
    target_value: int
    current_value: int
    progress_pct: float
    unlocked: bool
    unlocked_at: Optional[datetime] = None

# Recommendation schema
class SkillRecommendation(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    current_level: int
    target_level: int
    progress_pct: float
    status: str
    score: float
    reason: str
    key_factors: List[str]

# Settings schemas
class SettingsResponse(BaseModel):
    xp_per_30min: int
    xp_per_60min: int
    deep_work_bonus_pct: int
    consistency_bonus_pct: int
    is_demo_mode: bool

class SettingsUpdate(BaseModel):
    xp_per_30min: Optional[int] = Field(None, ge=1, le=500)
    xp_per_60min: Optional[int] = Field(None, ge=1, le=1000)
    deep_work_bonus_pct: Optional[int] = Field(None, ge=0, le=100)
    consistency_bonus_pct: Optional[int] = Field(None, ge=0, le=100)

# Analytics schemas
class XpHistoryPoint(BaseModel):
    date: str
    xp: int
    cumulative_xp: int

class LearningHoursPoint(BaseModel):
    date: str
    hours: float
    sessions: int

class CategoryDistribution(BaseModel):
    category: str
    skills_count: int
    total_xp: int
    hours_spent: float
    color: str

class PracticedSkillItem(BaseModel):
    skill_id: int
    name: str
    category: str
    level: int
    total_minutes: int
    hours: float
    xp_gained: int
    sessions_count: int

class AnalyticsResponse(BaseModel):
    timeframe: str
    total_xp: int
    total_hours: float
    total_sessions: int
    streak_days: int
    xp_over_time: List[XpHistoryPoint]
    learning_hours_chart: List[LearningHoursPoint]
    category_distribution: List[CategoryDistribution]
    most_practiced_skills: List[PracticedSkillItem]
    weekly_consistency: List[Dict[str, Any]]

# Dashboard schema
class DashboardResponse(BaseModel):
    user_level: int
    total_xp: int
    current_level_xp: int
    next_level_xp: int
    level_progress_pct: float
    total_skills: int
    mastered_skills: int
    in_progress_skills: int
    locked_skills: int
    available_skills: int
    streak_days: int
    xp_this_week: int
    weekly_learning_hours: float
    recently_improved: List[SkillSimple]
    recommendations: List[SkillRecommendation]
    current_goals: List[GoalResponse]
    recent_sessions: List[LearningSessionResponse]
    is_demo_mode: bool
