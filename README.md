# 🌌 NEXORA

> **Your life is the biggest project you'll ever work on.**  
> Turn learning, habits, and self-development into a visual, RPG-style **Skill Tree**.

---

## 🎮 The NEXORA Concept

Most productivity applications focus on simple **task lists**. **NEXORA** focuses on the **person behind the tasks**.

Instead of isolated to-do items, NEXORA organizes development into an interactive, interconnected **Progression Tree**:

```text
                    SKILL
                      │
              ┌───────┴───────┐
              │               │
           LEVEL 1          LEVEL 2
              │               │
        ┌─────┴─────┐    ┌────┴────┐
        │           │    │         │
     BEGINNER     CORE  INTERMEDIATE
                            │
                        ADVANCED
                            │
                         MASTER
```

Skills can represent anything in your growth journey:
* 💻 **Programming & Tech** (Python, FastAPI, Docker, Git)
* 🧠 **AI & Machine Learning** (Deep Learning, Computer Vision, NLP)
* 📊 **Data Science & Math** (SQL, Linear Algebra, Statistics)
* 🎨 **Design & Creativity** (UI Design, UX Research)
* 🗣️ **Communication & Business** (Public Speaking, Product Strategy)
* 🏃 **Fitness, Habits & Personal Growth**

---

## ✨ Features

- **Interactive Skill Tree Canvas**: Interactive pan/zoom canvas rendering skills, prerequisite dependencies, and dynamic status glows (`locked`, `available`, `in_progress`, `mastered`).
- **Deterministic XP & Leveling Engine**:
  - Base learning rate: 10 XP per 30 minutes, 25 XP per 60 minutes.
  - Multipliers: Difficulty (`Easy` x0.8, `Medium` x1.0, `Hard` x1.3), Deep Work (+10%), Daily Consistency (+5%).
  - Smooth quadratic leveling curve: Level thresholds scale steadily ($100 \times \frac{(N-1) \times N}{2}$).
- **Learning History Log**: Track study sessions, duration, difficulty, activity details, and instant XP breakdowns.
- **Rule-Based Recommendation Engine**: Calculates candidate skill readiness based on prerequisites, active goals, and recent practice momentum—no external AI dependency needed.
- **Goals & Milestone Tracking**: Connect target skill levels to deadlines with progress visualization.
- **Analytics Dashboard**: Real-time charts for XP over time, weekly learning hours, category distribution, and practice consistency.
- **Badges & Achievements**: Unlock milestones for streaks, deep work sessions, skill mastery, and multi-disciplinary learning.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/), [Pydantic v2](https://docs.pydantic.dev/), SQLite / PostgreSQL.
- **Frontend**: [Next.js 14 (App Router)](https://nextjs.org/), React 18, TypeScript, [Tailwind CSS](https://tailwindcss.com/), [Recharts](https://recharts.org/), Lucide Icons.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload --port 8000
```

The backend API will be available at: `http://localhost:8000`  
Interactive Swagger docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the Next.js development server
npm run dev
```

The frontend dashboard will be available at: `http://localhost:3000`

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory or configure environment variables directly:

```env
# Backend Configuration
DATABASE_URL=sqlite:///./nexora.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/nexora
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📁 Repository Structure

```text
NEXORA/
├── backend/
│   ├── database.py              # SQLite / PostgreSQL connection & SessionLocal
│   ├── main.py                  # FastAPI REST endpoints & CORS configuration
│   ├── models.py                # SQLAlchemy DB models (User, Skill, Goal, etc.)
│   ├── schemas.py               # Pydantic schemas for request/response validation
│   ├── seed.py                  # Default skill tree & demo data seeder
│   ├── requirements.txt         # Python dependencies
│   └── services/
│       ├── xp_engine.py         # Deterministic XP & level calculator
│       ├── skill_engine.py      # Skill status & prerequisite validation
│       ├── recommendation.py    # Rule-based skill recommendation engine
│       └── achievement_engine.py# Achievement unlocking heuristics
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   │   ├── page.tsx             # Main dashboard
│   │   ├── skill-tree/          # Interactive visual skill tree
│   │   ├── skills/              # Skill catalog & creation
│   │   ├── learning/            # Session logging & history
│   │   ├── analytics/           # Charts & activity statistics
│   │   ├── goals/               # Goal management
│   │   ├── achievements/        # Badges & achievements
│   │   └── settings/            # Reset demo data & system rules
│   ├── components/              # UI components & tree canvas
│   ├── hooks/                   # Custom React hooks (useToast)
│   ├── lib/                     # API client, types, and formatting utilities
│   └── package.json
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔐 Privacy First

NEXORA is designed around the idea that personal life data should remain strictly under the user's control.

- Complete local execution with SQLite out of the box
- Clean REST API architecture ready for encrypted profiles or personal cloud deployment
- Zero external tracking or mandatory third-party AI dependencies

---

## 🎯 Vision

Most productivity tools track items you have to check off. NEXORA tracks who you are becoming.

**Goals → Habits → Skills → Learning → Projects → Progress**

> **Don't just manage your day. Build your system.**

---

## 👨‍💻 Developer

**Isbandu Rahuman R.**  
AI & Data Science Student • Developer • Designer • Builder

---

## ⭐ Support

If you like the concept behind **NEXORA**, consider giving the repository a ⭐!
