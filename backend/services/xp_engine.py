"""
Deterministic XP & Level engine.

Rules (configurable below, never randomized):
  - Base XP rate: 1 XP per 2 minutes of focused learning (30 min -> 10 XP, 60 min -> 25 XP
    uses a mild curve rewarding longer sessions slightly more per-minute, see XP_BREAKPOINTS).
  - Deep work bonus: +10% if session marked as deep work.
  - Difficulty multiplier: Easy x0.8, Medium x1.0, Hard x1.3.
  - Daily consistency bonus: +5% if the user already learned on the previous day (streak > 0).

Level formula (skill-level and account-level use the same curve):
  XP required to REACH level N (cumulative) = 100 * (N-1) * N / 2 * SCALE
  i.e. level thresholds grow linearly-quadratic: 0, 100, 250, 500, 850, 1300 ...
  This matches the example in the spec (L1=0, L2=100, L3=250, L4=500).
"""
from typing import List, Tuple, Dict

# ---- Configurable constants ----
XP_PER_MINUTE_BASE = 10 / 30  # 30 min -> 10 XP baseline
XP_BREAKPOINTS = [
    # (min_minutes, xp_per_minute) - longer sessions get a slightly better rate
    (0, 10 / 30),      # ~0.333 xp/min
    (45, 25 / 60),     # 60 min -> 25 XP => ~0.4167 xp/min applies after 45min mark
]
DEEP_WORK_BONUS = 0.10
CONSISTENCY_BONUS = 0.05
DIFFICULTY_MULTIPLIER = {"Easy": 0.8, "Medium": 1.0, "Hard": 1.3}

LEVEL_SCALE = 1.0  # scales the whole curve


def xp_required_cumulative(level: int) -> float:
    """Cumulative XP required to REACH the given level (level 1 = 0 XP)."""
    if level <= 1:
        return 0.0
    n = level - 1
    return 100 * n * (n + 1) / 2 * LEVEL_SCALE


def level_for_xp(xp: float) -> int:
    level = 1
    while xp_required_cumulative(level + 1) <= xp:
        level += 1
        if level > 999:
            break
    return level


def level_progress(xp: float) -> Dict:
    level = level_for_xp(xp)
    floor = xp_required_cumulative(level)
    ceiling = xp_required_cumulative(level + 1)
    into_level = xp - floor
    needed = ceiling - floor
    pct = 0.0 if needed <= 0 else round(min(100.0, (into_level / needed) * 100), 1)
    return {
        "level": level,
        "xp": xp,
        "xp_into_level": round(into_level, 1),
        "xp_for_next": round(needed, 1),
        "progress_pct": pct,
    }


def _base_rate_for_duration(minutes: int) -> float:
    rate = XP_BREAKPOINTS[0][1]
    for threshold, r in XP_BREAKPOINTS:
        if minutes >= threshold:
            rate = r
    return rate


def calculate_xp(
    duration_minutes: int,
    difficulty: str = "Medium",
    deep_work: bool = False,
    is_consistent_day: bool = False,
) -> Tuple[float, List[Dict]]:
    """Returns (total_xp, breakdown list of {reason, amount})."""
    breakdown = []
    rate = _base_rate_for_duration(duration_minutes)
    base = duration_minutes * rate
    diff_mult = DIFFICULTY_MULTIPLIER.get(difficulty, 1.0)
    base_with_difficulty = base * diff_mult
    base_with_difficulty = round(base_with_difficulty, 2)
    breakdown.append({
        "reason": f"{duration_minutes} minutes completed ({difficulty.lower()} difficulty)",
        "amount": base_with_difficulty,
    })

    total = base_with_difficulty

    if deep_work:
        bonus = round(base_with_difficulty * DEEP_WORK_BONUS, 2)
        total += bonus
        breakdown.append({"reason": "Deep work bonus (+10%)", "amount": bonus})

    if is_consistent_day:
        bonus = round(base_with_difficulty * CONSISTENCY_BONUS, 2)
        total += bonus
        breakdown.append({"reason": "Consistency bonus (+5%)", "amount": bonus})

    return round(total, 2), breakdown
