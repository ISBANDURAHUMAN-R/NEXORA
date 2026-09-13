import datetime as dt
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from database import Base


def now():
    return dt.datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="Demo User")
    is_demo = Column(Boolean, default=True)
    total_xp = Column(Float, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(String, nullable=True)  # ISO date string
    created_at = Column(DateTime, default=now)

    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    user_achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    daily_stats = relationship("DailyStats", back_populates="user", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    category = Column(String, default="Custom")
    description = Column(Text, default="")
    level = Column(Integer, default=1)
    xp = Column(Float, default=0)
    target_level = Column(Integer, default=10)
    pos_x = Column(Float, default=0)
    pos_y = Column(Float, default=0)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    user = relationship("User", back_populates="skills")
    prereqs = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.skill_id",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    sessions = relationship("LearningSession", back_populates="skill", cascade="all, delete-orphan")


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"
    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    prerequisite_id = Column(Integer, ForeignKey("skills.id"))
    required_level = Column(Integer, default=3)

    skill = relationship("Skill", foreign_keys=[skill_id], back_populates="prereqs")
    prerequisite = relationship("Skill", foreign_keys=[prerequisite_id])


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    duration_minutes = Column(Integer, nullable=False)
    activity = Column(String, default="")
    difficulty = Column(String, default="Medium")  # Easy, Medium, Hard
    notes = Column(Text, default="")
    xp_awarded = Column(Float, default=0)
    xp_breakdown = Column(Text, default="[]")  # JSON string list of {reason, amount}
    deep_work = Column(Boolean, default=False)
    session_date = Column(String, default=lambda: dt.date.today().isoformat())
    created_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="sessions")
    skill = relationship("Skill", back_populates="sessions")


class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    title = Column(String, nullable=False)
    target_level = Column(Integer, default=10)
    deadline_days = Column(Integer, default=90)
    created_at = Column(DateTime, default=now)
    completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="goals")
    skill = relationship("Skill")


class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    description = Column(Text)
    icon = Column(String, default="star")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    unlocked_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement")


class DailyStats(Base):
    __tablename__ = "daily_stats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String)  # ISO date
    xp_gained = Column(Float, default=0)
    minutes_learned = Column(Integer, default=0)
    sessions_count = Column(Integer, default=0)

    user = relationship("User", back_populates="daily_stats")
