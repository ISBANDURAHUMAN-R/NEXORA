import datetime as dt
from sqlalchemy.orm import Session
from models import User, Skill, SkillPrerequisite, LearningSession, Goal, DailyStats
from services.xp_engine import xp_required_cumulative
from services.achievement_engine import ensure_achievement_rows, check_achievements

# (name, category, description, level, target_level, pos_x, pos_y, prereq_names)
SKILL_DEFS = [
    ("AI Engineer", "AI/ML", "Root career path combining software engineering and applied ML.", 6, 15, 500, 40, []),
    ("Python", "Programming", "General purpose programming language, the backbone of most ML work.", 8, 10, 260, 160, ["AI Engineer"]),
    ("SQL", "Data Science", "Querying and manipulating relational data.", 7, 10, 500, 160, ["AI Engineer"]),
    ("Math", "Mathematics", "Core mathematical foundations for machine learning.", 5, 10, 740, 160, ["AI Engineer"]),
    ("FastAPI", "Programming", "Modern Python web framework for building APIs.", 6, 10, 150, 280, ["Python"]),
    ("Statistics", "Mathematics", "Probability, distributions, and inference.", 4, 10, 740, 280, ["Math"]),
    ("Machine Learning", "AI/ML", "Supervised & unsupervised learning fundamentals.", 4, 10, 445, 400, ["Python", "Statistics"]),
    ("Deep Learning", "AI/ML", "Neural networks and gradient-based learning.", 2, 10, 445, 520, ["Machine Learning"]),
    ("Computer Vision", "AI/ML", "Applying deep learning to visual data.", 1, 10, 445, 640, ["Deep Learning"]),
    ("Data Cleaning", "Data Science", "Wrangling messy real-world datasets.", 6, 10, 130, 400, ["SQL"]),
    ("Scikit-learn", "AI/ML", "Practical ML library for classical algorithms.", 3, 10, 630, 400, ["Machine Learning"]),
    ("Linear Algebra", "Mathematics", "Vectors, matrices, and transformations.", 5, 10, 900, 280, ["Math"]),
    ("Cybersecurity Basics", "Cybersecurity", "Core principles of securing systems and data.", 2, 10, 1000, 40, []),
    ("Network Security", "Cybersecurity", "Protecting networks from intrusion.", 1, 10, 1000, 160, ["Cybersecurity Basics"]),
    ("UI Design", "Design", "Principles of visual interface design.", 3, 10, -60, 40, []),
    ("UX Research", "Design", "Understanding user needs through research.", 1, 10, -60, 160, ["UI Design"]),
    ("Public Speaking", "Communication", "Presenting ideas clearly and confidently.", 4, 10, -220, 40, []),
    ("Technical Writing", "Communication", "Writing clear docs and reports.", 5, 10, -220, 160, ["Public Speaking"]),
    ("Product Strategy", "Business", "Prioritizing what to build and why.", 2, 10, -380, 40, []),
    ("Negotiation", "Business", "Reaching favorable agreements.", 1, 10, -380, 160, ["Product Strategy"]),
    ("Git & Version Control", "Programming", "Tracking and collaborating on code changes.", 9, 10, 260, 40, []),
    ("Docker", "Programming", "Containerizing applications for deployment.", 4, 10, 150, 40, ["Git & Version Control"]),
    ("Data Visualization", "Data Science", "Communicating insight through charts.", 6, 10, 130, 520, ["Data Cleaning"]),
    ("NLP", "AI/ML", "Natural language processing fundamentals.", 1, 10, 630, 520, ["Scikit-learn"]),
]


def xp_for_level(level: int) -> float:
    """Return an XP value that places a skill mid-way through the given level."""
    floor = xp_required_cumulative(level)
    ceiling = xp_required_cumulative(level + 1)
    return round(floor + (ceiling - floor) * 0.55, 1)


def seed_demo_data(db: Session):
    # wipe existing demo user data
    db.query(DailyStats).delete()
    db.query(Goal).delete()
    db.query(LearningSession).delete()
    db.query(SkillPrerequisite).delete()
    db.query(Skill).delete()
    db.query(User).delete()
    db.commit()

    user = User(name="Demo User", is_demo=True, total_xp=0, level=1, current_streak=6, longest_streak=14,
                last_active_date=dt.date.today().isoformat())
    db.add(user)
    db.commit()
    db.refresh(user)

    name_to_skill = {}
    for name, category, desc, level, target, x, y, _ in SKILL_DEFS:
        s = Skill(
            user_id=user.id, name=name, category=category, description=desc,
            level=level, xp=xp_for_level(level), target_level=target, pos_x=x, pos_y=y,
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        name_to_skill[name] = s

    for name, *_rest, prereqs in SKILL_DEFS:
        for p_name in prereqs:
            if p_name in name_to_skill:
                db.add(SkillPrerequisite(
                    skill_id=name_to_skill[name].id,
                    prerequisite_id=name_to_skill[p_name].id,
                    required_level=3,
                ))
    db.commit()

    # account-level xp = sum of a scaled portion of skill xp, keeps numbers sane for the spec example
    user.total_xp = 7420
    user.level = 18
    db.commit()

    # Backfill 21 days of learning sessions + daily stats for charts/streak
    today = dt.date.today()
    activities = ["Guided tutorial", "Project work", "Reading docs", "Practice exercises", "Code review"]
    session_skill_cycle = ["Python", "Machine Learning", "SQL", "Statistics", "FastAPI", "Deep Learning", "Data Cleaning"]

    for i in range(21, -1, -1):
        day = today - dt.timedelta(days=i)
        # skip a couple of days to make the streak realistic (only last 6 days are unbroken)
        if 6 < i <= 9:
            continue
        skill_name = session_skill_cycle[i % len(session_skill_cycle)]
        skill = name_to_skill[skill_name]
        duration = [30, 45, 60, 25, 90][i % 5]
        difficulty = ["Easy", "Medium", "Hard"][i % 3]
        deep_work = duration >= 60

        from services.xp_engine import calculate_xp
        xp, breakdown = calculate_xp(duration, difficulty, deep_work, is_consistent_day=True)

        sess = LearningSession(
            user_id=user.id, skill_id=skill.id, duration_minutes=duration,
            activity=activities[i % len(activities)], difficulty=difficulty,
            notes="", xp_awarded=xp, xp_breakdown=str(breakdown).replace("'", '"'),
            deep_work=deep_work, session_date=day.isoformat(),
        )
        db.add(sess)

        stat = DailyStats(user_id=user.id, date=day.isoformat(), xp_gained=xp,
                           minutes_learned=duration, sessions_count=1)
        db.add(stat)
    db.commit()

    # Goals
    db.add(Goal(user_id=user.id, skill_id=name_to_skill["Machine Learning"].id,
                title="Master Machine Learning", target_level=10, deadline_days=90))
    db.add(Goal(user_id=user.id, skill_id=name_to_skill["Deep Learning"].id,
                title="Get comfortable with Deep Learning", target_level=7, deadline_days=60))
    db.commit()

    ensure_achievement_rows(db)
    check_achievements(db, user, leveled_up=True)

    return user
