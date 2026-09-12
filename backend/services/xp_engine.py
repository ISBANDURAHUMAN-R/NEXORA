import math
from typing import List, Dict, Any

class XpEngine:
    @staticmethod
    def calculate_session_xp(
        duration_minutes: int,
        difficulty: str = "Medium",
        is_deep_work: bool = False,
        streak_days: int = 1,
        xp_per_30min: int = 10,
        xp_per_60min: int = 25,
        deep_work_bonus_pct: int = 10,
        consistency_bonus_pct: int = 5
    ) -> Dict[str, Any]:
        """
        Deterministic XP calculation.
        30 min = xp_per_30min (default 10 XP)
        60 min = xp_per_60min (default 25 XP)
        Non-linear rate favoring longer sustained blocks: rate per minute = 25/60 ~ 0.4167 vs 10/30 ~ 0.333
        """
        breakdown: List[Dict[str, Any]] = []

        # Base calculation based on minutes
        if duration_minutes <= 30:
            base_xp = math.floor((duration_minutes / 30.0) * xp_per_30min)
        elif duration_minutes <= 60:
            # Interpolate between 30m (10 XP) and 60m (25 XP)
            t = (duration_minutes - 30.0) / 30.0
            base_xp = math.floor(xp_per_30min + t * (xp_per_60min - xp_per_30min))
        else:
            # Beyond 60 minutes, award 25 XP per hour prorated
            base_xp = math.floor((duration_minutes / 60.0) * xp_per_60min)

        base_xp = max(base_xp, 2)  # minimum 2 XP for any recorded block >= 5m

        # Difficulty multiplier
        diff_mult = 1.0
        if difficulty.lower() == "easy":
            diff_mult = 0.9
        elif difficulty.lower() == "medium":
            diff_mult = 1.0
        elif difficulty.lower() == "hard":
            diff_mult = 1.25

        difficulty_adjusted_base = math.floor(base_xp * diff_mult)
        breakdown.append({
            "label": f"{duration_minutes}m learning ({difficulty})",
            "xp": difficulty_adjusted_base,
            "icon": "Clock"
        })

        current_total = difficulty_adjusted_base

        # Deep work bonus
        if is_deep_work:
            deep_work_xp = math.ceil(difficulty_adjusted_base * (deep_work_bonus_pct / 100.0))
            if deep_work_xp > 0:
                breakdown.append({
                    "label": f"Deep work focus (+{deep_work_bonus_pct}%)",
                    "xp": deep_work_xp,
                    "icon": "Zap"
                })
                current_total += deep_work_xp

        # Consistency bonus (if streak >= 2)
        if streak_days >= 2:
            consistency_xp = math.ceil(difficulty_adjusted_base * (consistency_bonus_pct / 100.0))
            if consistency_xp > 0:
                breakdown.append({
                    "label": f"Streak consistency ({streak_days} days, +{consistency_bonus_pct}%)",
                    "xp": consistency_xp,
                    "icon": "Flame"
                })
                current_total += consistency_xp

        return {
            "total_xp": current_total,
            "breakdown": breakdown
        }
