from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), default="developer", unique=True)
    level = Column(Integer, default=1)
    total_xp = Column(Integer, default=0)
    current_level_xp = Column(Integer, default=0)
    next_level_xp = Column(Integer, default=100)
    streak_days = Column(Integer, default=1)
    last_active_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), default="Programming", index=True)
    description = Column(Text, default="")
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    target_level = Column(Integer, default=10)
    icon = Column(String(50), default="Code")
    color = Column(String(30), default="#06b6d4")
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prerequisites = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.skill_id",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    downstream = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.prerequisite_id",
        back_populates="prerequisite",
        cascade="all, delete-orphan"
    )
    learning_sessions = relationship(
        "LearningSession",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
    goals = relationship(
        "Goal",
        back_populates="skill",
        cascade="all, delete-orphan"
    )

class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    prerequisite_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    required_level = Column(Integer, default=1)

    skill = relationship("Skill", foreign_keys=[skill_id], back_populates="prerequisites")
    prerequisite = relationship("Skill", foreign_keys=[prerequisite_id], back_populates="downstream")

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    activity = Column(String(200), nullable=False)
    difficulty = Column(String(20), default="Medium")  # Easy, Medium, Hard
    notes = Column(Text, default="")
    is_deep_work = Column(Boolean, default=False)
    xp_earned = Column(Integer, default=0)
    xp_breakdown = Column(Text, default="[]")  # JSON string of breakdown items
    created_at = Column(DateTime, default=datetime.utcnow)

    skill = relationship("Skill", back_populates="learning_sessions")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    target_level = Column(Integer, default=5)
    deadline_days = Column(Integer, default=30)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    skill = relationship("Skill", back_populates="goals")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    icon = Column(String(50), default="Award")
    category = Column(String(50), default="Progression")
    target_value = Column(Integer, default=1)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)
    current_value = Column(Integer, default=0)

    achievement = relationship("Achievement")

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    xp_per_30min = Column(Integer, default=10)
    xp_per_60min = Column(Integer, default=25)
    deep_work_bonus_pct = Column(Integer, default=10)
    consistency_bonus_pct = Column(Integer, default=5)
    is_demo_mode = Column(Boolean, default=True)

class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    date_str = Column(String(10), unique=True, index=True, nullable=False)  # YYYY-MM-DD
    xp_gained = Column(Integer, default=0)
    minutes_spent = Column(Integer, default=0)
    sessions_count = Column(Integer, default=0)
