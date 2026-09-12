import math
from typing import Tuple

class LevelEngine:
    # --- Overall User Level Calculation ---
    @staticmethod
    def user_level_threshold(level: int) -> int:
        """Cumulative XP needed to reach a given user level."""
        if level <= 1:
            return 0
        # Level 2 -> 100
        # Level 3 -> 250
        # Level 4 -> 500
        # Level 5 -> 880
        # Level 6 -> 1400
        # Level 18 -> ~10000
        return math.floor(70.0 * math.pow(level - 1, 1.7))

    @classmethod
    def calculate_user_level(cls, total_xp: int) -> Tuple[int, int, int, float]:
        """
        Given user total_xp, calculate:
        (level, current_level_xp, next_level_xp, progress_percentage)
        """
        if total_xp <= 0:
            return 1, 0, cls.user_level_threshold(2), 0.0

        level = 1
        while cls.user_level_threshold(level + 1) <= total_xp:
            level += 1

        level_start_xp = cls.user_level_threshold(level)
        level_end_xp = cls.user_level_threshold(level + 1)

        current_level_xp = total_xp - level_start_xp
        span = max(level_end_xp - level_start_xp, 1)
        next_level_xp = span
        pct = min(100.0, max(0.0, round((current_level_xp / span) * 100.0, 1)))

        return level, current_level_xp, next_level_xp, pct

    # --- Skill Level Calculation ---
    @staticmethod
    def skill_level_threshold(level: int) -> int:
        """Cumulative XP needed for a skill to reach a given level."""
        if level <= 1:
            return 0
        # Level 2: 60 XP
        # Level 3: 150 XP
        # Level 4: 280 XP
        # Level 5: 450 XP
        # Level 6: 660 XP
        # Level 7: 920 XP
        # Level 8: 1230 XP
        # Level 9: 1590 XP
        # Level 10: 2000 XP
        return math.floor(40.0 * math.pow(level - 1, 1.7))

    @classmethod
    def calculate_skill_level_from_xp(cls, xp: int, target_level: int = 10) -> Tuple[int, int, int, float]:
        """
        Given a skill's total XP, returns:
        (level, current_level_xp, next_level_xp, progress_pct)
        """
        if xp <= 0:
            return 1, 0, cls.skill_level_threshold(2), 0.0

        level = 1
        while level < target_level and cls.skill_level_threshold(level + 1) <= xp:
            level += 1

        if level >= target_level:
            # Skill is mastered!
            level_start_xp = cls.skill_level_threshold(target_level)
            return target_level, xp - level_start_xp, xp - level_start_xp, 100.0

        level_start_xp = cls.skill_level_threshold(level)
        level_end_xp = cls.skill_level_threshold(level + 1)

        current_level_xp = xp - level_start_xp
        span = max(level_end_xp - level_start_xp, 1)
        next_level_xp = span
        pct = min(100.0, max(0.0, round((current_level_xp / span) * 100.0, 1)))

        return level, current_level_xp, next_level_xp, pct
