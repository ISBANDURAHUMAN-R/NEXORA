from datetime import datetime, timedelta, date
import json
from sqlalchemy.orm import Session
from database import Base, engine
from models import (
    User, Skill, SkillPrerequisite, LearningSession, Goal,
    Achievement, UserAchievement, Settings, DailyStats
)
from services.achievement_engine import DEFAULT_ACHIEVEMENTS
from services.level_engine import LevelEngine

def reset_demo_data(db: Session):
    # Clear all tables
    db.query(UserAchievement).delete()
    db.query(Achievement).delete()
    db.query(LearningSession).delete()
    db.query(Goal).delete()
    db.query(SkillPrerequisite).delete()
    db.query(Skill).delete()
    db.query(DailyStats).delete()
    db.query(Settings).delete()
    db.query(User).delete()
    db.commit()

    # 1. Create Default Settings
    settings = Settings(
        xp_per_30min=10,
        xp_per_60min=25,
        deep_work_bonus_pct=10,
        consistency_bonus_pct=5,
        is_demo_mode=True
    )
    db.add(settings)

    # 2. Create User (Level 18, 7420 XP as specified in prompt)
    # Cumulative XP for Level 18 ~ 7420 XP
    lvl, cur_xp, next_xp, pct = LevelEngine.calculate_user_level(7420)
    user = User(
        username="alex_developer",
        level=18,
        total_xp=7420,
        current_level_xp=7420 - LevelEngine.user_level_threshold(18),
        next_level_xp=LevelEngine.user_level_threshold(19) - LevelEngine.user_level_threshold(18),
        streak_days=12,
        last_active_date=date.today()
    )
    db.add(user)
    db.flush()

    # 3. Create Achievements
    for ach_data in DEFAULT_ACHIEVEMENTS:
        ach = Achievement(**ach_data)
        db.add(ach)
        db.flush()
        db.add(UserAchievement(achievement_id=ach.id, unlocked=False, current_value=0))
    db.flush()

    # 4. Define 24 Skills with realistic tree coordinates (X, Y)
    # Layout structure:
    # Tier 1 (Foundations): Git, Math, Python, SQL, Data Structures
    # Tier 2: Statistics, Linear Algebra, FastAPI, TypeScript, Algorithms
    # Tier 3: React, Docker, Machine Learning, Scikit-Learn
    # Tier 4: Next.js, Deep Learning, MLOps, System Design
    # Tier 5: PyTorch, Computer Vision, Natural Language Processing, Kubernetes
    # Tier 6: Reinforcement Learning, AI Engineer (Cap Stone)
    skills_data = [
        # Foundations (Tier 1: y = 100)
        {"name": "Git & Version Control", "slug": "git", "category": "Programming", "level": 10, "xp": 2100, "target_level": 10, "icon": "GitBranch", "color": "#10b981", "x": 100, "y": 100, "desc": "Branching strategies, rebase, merge conflicts, Git flow."},
        {"name": "Python Programming", "slug": "python", "category": "Programming", "level": 10, "xp": 2400, "target_level": 10, "icon": "Terminal", "color": "#06b6d4", "x": 300, "y": 100, "desc": "Core syntax, OOP, generators, async programming, typing."},
        {"name": "SQL & Relational DBs", "slug": "sql", "category": "Data Science", "level": 10, "xp": 2050, "target_level": 10, "icon": "Database", "color": "#3b82f6", "x": 500, "y": 100, "desc": "Complex joins, indexing, query execution plans, PostgreSQL."},
        {"name": "Discrete Mathematics", "slug": "math", "category": "Mathematics", "level": 10, "xp": 2000, "target_level": 10, "icon": "Binary", "color": "#8b5cf6", "x": 700, "y": 100, "desc": "Set theory, boolean algebra, combinatorics, proof methods."},
        {"name": "Data Structures", "slug": "data-structures", "category": "Computer Science", "level": 10, "xp": 2000, "target_level": 10, "icon": "Layers", "color": "#10b981", "x": 900, "y": 100, "desc": "Trees, graphs, heaps, hash maps, complexity analysis."},

        # Tier 2: y = 260
        {"name": "FastAPI Web Framework", "slug": "fastapi", "category": "Programming", "level": 10, "xp": 2200, "target_level": 10, "icon": "Zap", "color": "#06b6d4", "x": 200, "y": 260, "desc": "High performance async APIs, Pydantic v2, OpenAPI, dependency injection."},
        {"name": "Statistics & Probability", "slug": "statistics", "category": "Mathematics", "level": 10, "xp": 2000, "target_level": 10, "icon": "PieChart", "color": "#8b5cf6", "x": 600, "y": 260, "desc": "Bayesian inference, hypothesis testing, distributions, p-values."},
        {"name": "Linear Algebra", "slug": "linear-algebra", "category": "Mathematics", "level": 10, "xp": 2000, "target_level": 10, "icon": "Grid", "color": "#8b5cf6", "x": 800, "y": 260, "desc": "Vectors, matrices, eigenvalues, SVD, tensor transformations."},
        {"name": "TypeScript", "slug": "typescript", "category": "Programming", "level": 6, "xp": 720, "target_level": 10, "icon": "Code2", "color": "#3b82f6", "x": 400, "y": 260, "desc": "Type systems, generics, utility types, compile-time safety."},
        {"name": "Algorithms & Optimization", "slug": "algorithms", "category": "Computer Science", "level": 7, "xp": 980, "target_level": 10, "icon": "Cpu", "color": "#ec4899", "x": 1000, "y": 260, "desc": "Dynamic programming, graph algorithms, Dijkstra, branch and bound."},

        # Tier 3: y = 420
        {"name": "Docker & Containers", "slug": "docker", "category": "DevOps", "level": 5, "xp": 500, "target_level": 10, "icon": "Box", "color": "#06b6d4", "x": 100, "y": 420, "desc": "Multi-stage builds, compose files, container networking, volumes."},
        {"name": "React Architecture", "slug": "react", "category": "Programming", "level": 6, "xp": 750, "target_level": 10, "icon": "Atom", "color": "#06b6d4", "x": 300, "y": 420, "desc": "Hooks, state management, reconciliation, custom hooks, memoization."},
        {"name": "Machine Learning", "slug": "machine-learning", "category": "AI/ML", "level": 4, "xp": 380, "target_level": 10, "icon": "BrainCircuit", "color": "#a855f7", "x": 700, "y": 420, "desc": "Supervised, unsupervised, random forests, gradient boosting, cross-validation."},
        {"name": "Scikit-Learn & Pandas", "slug": "scikit-learn", "category": "Data Science", "level": 5, "xp": 540, "target_level": 10, "icon": "Table", "color": "#f59e0b", "x": 900, "y": 420, "desc": "Data preprocessing, feature engineering, pipeline construction."},

        # Tier 4: y = 580
        {"name": "Next.js Fullstack", "slug": "nextjs", "category": "Programming", "level": 4, "xp": 310, "target_level": 10, "icon": "Globe", "color": "#ffffff", "x": 300, "y": 580, "desc": "App router, server components, server actions, streaming SSR."},
        {"name": "Deep Learning", "slug": "deep-learning", "category": "AI/ML", "level": 3, "xp": 190, "target_level": 10, "icon": "Network", "color": "#ec4899", "x": 700, "y": 580, "desc": "Backpropagation, neural architectures, activation functions, loss landscapes."},
        {"name": "System Design", "slug": "system-design", "category": "Computer Science", "level": 4, "xp": 340, "target_level": 10, "icon": "Server", "color": "#14b8a6", "x": 500, "y": 580, "desc": "Distributed caching, load balancing, sharding, consensus, CAP theorem."},
        {"name": "MLOps & CI/CD", "slug": "mlops", "category": "DevOps", "level": 2, "xp": 80, "target_level": 10, "icon": "Workflow", "color": "#f97316", "x": 900, "y": 580, "desc": "Model registry, data versioning (DVC), drift monitoring, inference latency."},

        # Tier 5: y = 740
        {"name": "PyTorch Framework", "slug": "pytorch", "category": "AI/ML", "level": 3, "xp": 200, "target_level": 10, "icon": "Flame", "color": "#ef4444", "x": 600, "y": 740, "desc": "Tensors, autograd, custom modules, training loops, CUDA acceleration."},
        {"name": "Computer Vision", "slug": "computer-vision", "category": "AI/ML", "level": 1, "xp": 0, "target_level": 10, "icon": "Eye", "color": "#a855f7", "x": 800, "y": 740, "desc": "CNNs, object detection (YOLO), image segmentation, OpenCV, embeddings."},
        {"name": "Natural Language Processing", "slug": "nlp", "category": "AI/ML", "level": 1, "xp": 0, "target_level": 10, "icon": "MessageSquareText", "color": "#06b6d4", "x": 1000, "y": 740, "desc": "Transformers, tokenization, BERT, LLM fine-tuning, RAG, prompt engineering."},
        {"name": "Kubernetes Orchestration", "slug": "kubernetes", "category": "DevOps", "level": 1, "xp": 0, "target_level": 10, "icon": "Boxes", "color": "#3b82f6", "x": 200, "y": 740, "desc": "Pods, deployments, statefulsets, ingress controllers, helm charts."},

        # Tier 6: y = 900
        {"name": "Reinforcement Learning", "slug": "reinforcement-learning", "category": "AI/ML", "level": 1, "xp": 0, "target_level": 10, "icon": "Target", "color": "#eab308", "x": 700, "y": 900, "desc": "Markov decision processes, Q-learning, policy gradients, PPO, actor-critic."},
        {"name": "AI Engineer (Master Tier)", "slug": "ai-engineer", "category": "AI/ML", "level": 1, "xp": 0, "target_level": 10, "icon": "Sparkles", "color": "#8b5cf6", "x": 900, "y": 900, "desc": "Autonomous agents, multi-modal foundation models, production alignment and orchestration."}
    ]

    skill_records = {}
    for item in skills_data:
        skill = Skill(
            name=item["name"],
            slug=item["slug"],
            category=item["category"],
            level=item["level"],
            xp=item["xp"],
            target_level=item["target_level"],
            icon=item["icon"],
            color=item["color"],
            description=item["desc"],
            position_x=float(item["x"]),
            position_y=float(item["y"])
        )
        db.add(skill)
        db.flush()
        skill_records[item["slug"]] = skill

    # 5. Define Prerequisites (Interconnecting DAG)
    # Mastered: 8 (Git, Python, SQL, Math, Data Structures, FastAPI, Statistics, Linear Algebra)
    # In Progress: 9 (TypeScript, Algorithms, Docker, React, Machine Learning, Scikit-Learn, Next.js, Deep Learning, System Design, MLOps, PyTorch - actually 9 of these have level>1)
    # Locked: 7 (Computer Vision, NLP, Kubernetes, Reinforcement Learning, AI Engineer, etc. requiring higher level prereqs)
    prereqs = [
        # FastAPI depends on Python
        ("fastapi", "python", 5),
        # Statistics depends on Math
        ("statistics", "math", 4),
        # Linear Algebra depends on Math
        ("linear-algebra", "math", 4),
        # TypeScript depends on Python
        ("typescript", "python", 4),
        # Algorithms depends on Data Structures
        ("algorithms", "data-structures", 5),
        # React depends on TypeScript
        ("react", "typescript", 4),
        # Docker depends on Git
        ("docker", "git", 4),
        # Machine Learning depends on Python, Statistics, Linear Algebra
        ("machine-learning", "python", 5),
        ("machine-learning", "statistics", 4),
        ("machine-learning", "linear-algebra", 4),
        # Scikit-Learn depends on Machine Learning, SQL
        ("scikit-learn", "machine-learning", 2),
        ("scikit-learn", "sql", 4),
        # Next.js depends on React, FastAPI
        ("nextjs", "react", 5),
        ("nextjs", "fastapi", 5),
        # Deep Learning depends on Machine Learning
        ("deep-learning", "machine-learning", 3),
        # System Design depends on FastAPI, Docker, Algorithms (Algorithms req 9, current is 7 -> LOCKED)
        ("system-design", "fastapi", 5),
        ("system-design", "docker", 4),
        ("system-design", "algorithms", 9),
        # MLOps depends on Docker, Scikit-Learn (Scikit-Learn req 8, current is 5 -> LOCKED)
        ("mlops", "docker", 4),
        ("mlops", "scikit-learn", 8),
        # PyTorch depends on Deep Learning
        ("pytorch", "deep-learning", 3),
        # Computer Vision depends on Deep Learning (required level 6, current is 3 -> LOCKED)
        ("computer-vision", "deep-learning", 6),
        # NLP depends on Deep Learning (required level 6, current is 3 -> LOCKED)
        ("nlp", "deep-learning", 6),
        # Kubernetes depends on Docker (required level 8, current is 5 -> LOCKED)
        ("kubernetes", "docker", 8),
        # Reinforcement Learning depends on PyTorch (required level 5, current is 3 -> LOCKED)
        ("reinforcement-learning", "pytorch", 5),
        # AI Engineer depends on NLP (req 5) and Computer Vision (req 5) -> LOCKED
        ("ai-engineer", "nlp", 5),
        ("ai-engineer", "computer-vision", 5)
    ]

    for child_slug, parent_slug, req_level in prereqs:
        child = skill_records[child_slug]
        parent = skill_records[parent_slug]
        pr = SkillPrerequisite(
            skill_id=child.id,
            prerequisite_id=parent.id,
            required_level=req_level
        )
        db.add(pr)
    db.flush()

    # 6. Create Realistic Goals
    goals_data = [
        {"title": "Master Machine Learning Foundations", "slug": "machine-learning", "target_level": 10, "deadline_days": 90, "completed": False},
        {"title": "Reach Deep Learning Level 8", "slug": "deep-learning", "target_level": 8, "deadline_days": 60, "completed": False},
        {"title": "Complete Next.js App Router Architecture", "slug": "nextjs", "target_level": 8, "deadline_days": 45, "completed": False},
    ]
    for g in goals_data:
        db.add(Goal(
            title=g["title"],
            skill_id=skill_records[g["slug"]].id,
            target_level=g["target_level"],
            deadline_days=g["deadline_days"],
            completed=g["completed"],
            created_at=datetime.utcnow() - timedelta(days=14)
        ))
    db.flush()

    # 7. Create Learning Sessions over past 30 days
    sample_sessions = [
        {"slug": "machine-learning", "min": 60, "activity": "Gradient descent and cross validation", "diff": "Medium", "deep": True, "notes": "Implemented ridge and lasso regression from scratch", "days_ago": 0},
        {"slug": "deep-learning", "min": 90, "activity": "Backpropagation mathematics and loss curves", "diff": "Hard", "deep": True, "notes": "Derived chain rule for convolutional layers", "days_ago": 1},
        {"slug": "fastapi", "min": 60, "activity": "FastAPI practice with async DB drivers", "diff": "Medium", "deep": False, "notes": "Built REST API with Pydantic v2 schemas and JWT middleware", "days_ago": 2},
        {"slug": "pytorch", "min": 45, "activity": "Custom Dataset and DataLoader pipelines", "diff": "Medium", "deep": True, "notes": "Benchmarked num_workers on GPU memory throughput", "days_ago": 3},
        {"slug": "machine-learning", "min": 60, "activity": "Ensemble methods with XGBoost & LightGBM", "diff": "Medium", "deep": True, "notes": "Tuned hyper-parameters with Optuna bayesian search", "days_ago": 4},
        {"slug": "nextjs", "min": 45, "activity": "Server Actions and Streaming SSR", "diff": "Easy", "deep": False, "notes": "Implemented optimistic UI updates with useOptimistic", "days_ago": 5},
        {"slug": "system-design", "min": 60, "activity": "Distributed caching with Redis & CDN invalidation", "diff": "Hard", "deep": True, "notes": "Analyzed cache stampede mitigation strategies", "days_ago": 6},
        {"slug": "statistics", "min": 60, "activity": "Bayesian inference and conjugate priors", "diff": "Hard", "deep": True, "notes": "Beta-Binomial models and credible intervals", "days_ago": 8},
        {"slug": "docker", "min": 45, "activity": "Multi-stage production Dockerfiles", "diff": "Medium", "deep": False, "notes": "Reduced image footprint from 1.2GB to 85MB using distroless", "days_ago": 10},
        {"slug": "algorithms", "min": 60, "activity": "Dynamic programming memoization & tabulation", "diff": "Hard", "deep": True, "notes": "Solved 0/1 knapsack and longest common subsequence", "days_ago": 12},
    ]

    for s in sample_sessions:
        skill = skill_records[s["slug"]]
        created_time = datetime.utcnow() - timedelta(days=s["days_ago"], hours=3)
        base_xp = 25 if s["min"] >= 60 else 15
        breakdown = [
            {"label": f"{s['min']} minutes completed ({s['diff']})", "xp": base_xp, "icon": "Clock"},
        ]
        total = base_xp
        if s["deep"]:
            breakdown.append({"label": "Deep work focus (+10%)", "xp": 3, "icon": "Zap"})
            total += 3
        breakdown.append({"label": "Streak consistency bonus", "xp": 2, "icon": "Flame"})
        total += 2

        db.add(LearningSession(
            skill_id=skill.id,
            duration_minutes=s["min"],
            activity=s["activity"],
            difficulty=s["diff"],
            notes=s["notes"],
            is_deep_work=s["deep"],
            xp_earned=total,
            xp_breakdown=json.dumps(breakdown),
            created_at=created_time
        ))

    # 8. Create DailyStats for past 30 days
    today = date.today()
    for i in range(30):
        day_date = today - timedelta(days=29 - i)
        date_str = day_date.strftime("%Y-%m-%d")
        # Vary slightly for realism: active during weekdays, some on weekends
        is_active = (i % 3 != 0) or (i > 18)
        minutes = 45 + (i * 7) % 75 if is_active else 0
        xp = (minutes // 2) + 10 if minutes > 0 else 0
        sess_count = 1 if (minutes > 0 and minutes < 70) else (2 if minutes >= 70 else 0)

        db.add(DailyStats(
            date_str=date_str,
            xp_gained=xp,
            minutes_spent=minutes,
            sessions_count=sess_count
        ))

    db.commit()

    # 9. Update achievements for user
    from services.achievement_engine import AchievementEngine
    AchievementEngine.evaluate_achievements(db, user)
    db.commit()
