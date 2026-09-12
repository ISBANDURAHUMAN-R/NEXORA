import pytest
from services.xp_engine import XpEngine
from services.level_engine import LevelEngine

def test_xp_engine_30min():
    # 30 min, Medium, no deep work, streak 1 -> 10 XP
    res = XpEngine.calculate_session_xp(
        duration_minutes=30,
        difficulty="Medium",
        is_deep_work=False,
        streak_days=1,
        xp_per_30min=10,
        xp_per_60min=25
    )
    assert res["total_xp"] == 10
    assert len(res["breakdown"]) == 1

def test_xp_engine_60min_deep_work_and_streak():
    # 60 min -> 25 base
    # Hard -> 25 * 1.25 = 31 base
    # Deep work (+10%) -> ceil(31 * 0.1) = 4
    # Streak 7 (+5%) -> ceil(31 * 0.05) = 2
    # Total = 31 + 4 + 2 = 37 XP
    res = XpEngine.calculate_session_xp(
        duration_minutes=60,
        difficulty="Hard",
        is_deep_work=True,
        streak_days=7,
        xp_per_30min=10,
        xp_per_60min=25,
        deep_work_bonus_pct=10,
        consistency_bonus_pct=5
    )
    assert res["total_xp"] == 37
    assert len(res["breakdown"]) == 3
    assert res["breakdown"][0]["xp"] == 31
    assert res["breakdown"][1]["xp"] == 4
    assert res["breakdown"][2]["xp"] == 2

def test_level_engine():
    # Level 1 should be 0 threshold
    assert LevelEngine.user_level_threshold(1) == 0
    # Higher levels strictly increasing
    t2 = LevelEngine.user_level_threshold(2)
    t3 = LevelEngine.user_level_threshold(3)
    t4 = LevelEngine.user_level_threshold(4)
    assert t2 < t3 < t4

    # Calculate user level
    lvl, cur_xp, next_xp, pct = LevelEngine.calculate_user_level(0)
    assert lvl == 1
    assert cur_xp == 0

    # Skill level calculation
    lvl, cur_xp, next_xp, pct = LevelEngine.calculate_skill_level_from_xp(2000, target_level=10)
    assert lvl == 10
    assert pct == 100.0
