<p align="center">
  <img src="assets/banner.png" alt="NEXORA Banner" width="100%">
</p>

# ◈ NEXORA — Skill Tree & Personal Growth Engine

[![CI](https://github.com/ISBANDURAHUMAN-R/NEXORA/actions/workflows/ci.yml/badge.svg)](https://github.com/ISBANDURAHUMAN-R/NEXORA/actions)

## ◆ About the Project
NEXORA is a web application that organizes learning activities, habits, and self-development into an interactive RPG-style skill tree. Instead of simple task lists, it structures progression across interconnected competency nodes with prerequisite dependencies and deterministic XP leveling mechanics.

```mermaid
flowchart TD
    User["&nbsp; User Study Activity / &nbsp;<br/>&nbsp; Habit Completion &nbsp;"] --> API["&nbsp; FastAPI Backend &nbsp;<br/>&nbsp; (Pydantic v2 + SQLite) &nbsp;"]
    API --> XP["&nbsp; Deterministic XP &nbsp;<br/>&nbsp; Engine (Quadratic) &nbsp;"]
    API --> Graph["&nbsp; Competency Graph &amp; &nbsp;<br/>&nbsp; Prerequisite Validator &nbsp;"]
    XP --> Level["&nbsp; Level Progression &nbsp;<br/>&nbsp; &amp; Streak Analytics &nbsp;"]
    Graph --> Unlocks["&nbsp; Node Unlocking &amp; &nbsp;<br/>&nbsp; Propagation &nbsp;"]
    Level --> DB[("&nbsp; SQLAlchemy 2.0 &nbsp;<br/>&nbsp; Persistence &nbsp;")]
    Unlocks --> DB
    DB --> UI["&nbsp; Next.js 14 App Router &nbsp;<br/>&nbsp; + Tailwind Canvas &nbsp;"]
```

## ❖ Key Features
- Interactive visual skill tree canvas with pan, zoom, and dynamic status indicators.
- Deterministic XP and leveling engine with quadratic leveling curves and difficulty multipliers.
- Session logging module recording study duration, activity notes, and earned experience.
- Rule-based recommendation engine evaluating prerequisite readiness without external AI APIs.
- Analytics dashboard featuring XP growth trajectories and weekly learning distribution charts.

## ⬢ Technologies Used
- Python 3.10+
- FastAPI & Pydantic v2
- SQLAlchemy 2.0 & SQLite
- Next.js 14 (App Router)
- React 18 & TypeScript
- Tailwind CSS
- Recharts & Lucide React

## § Requirements
- Python 3.10 or higher
- Node.js 18 or higher

## ▲ Installation & Execution
```bash
# 1. Start Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2. Start Frontend
cd ../frontend
npm install
npm run dev
```

## ※ Developer
Developer: ISBANDU RAHUMAN R  
GitHub: https://github.com/ISBANDURAHUMAN-R
