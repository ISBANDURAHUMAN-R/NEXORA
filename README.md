# SkillTree

A personal skill progression system that visualizes learning and development as an interconnected,
RPG-style skill tree — with real backend logic (deterministic XP, levels, prerequisites, and a
rule-based recommendation engine), not a static mockup.

## Stack

- **Frontend**: Next.js 14 (App Router), React, TypeScript, Tailwind CSS, Recharts, lucide-react
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite (file-based, zero setup)

## Project structure

```
skilltree/
├── backend/
│   ├── main.py                # FastAPI app + all REST endpoints
│   ├── database.py            # SQLAlchemy engine/session
│   ├── models.py               # ORM models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── seed.py                 # Demo data generator
│   ├── services/
│   │   ├── xp_engine.py         # Deterministic XP + level curve
│   │   ├── skill_engine.py      # Prerequisite/status resolution
│   │   ├── recommendation.py    # Rule-based recommendation engine
│   │   └── achievement_engine.py
│   └── requirements.txt
├── frontend/
│   ├── app/                    # Pages (dashboard, skill-tree, skills, learning, analytics, goals, achievements, settings)
│   ├── components/             # Sidebar, TopBar, SkillTreeCanvas, SkillDetailPanel, modals, UI primitives
│   ├── hooks/                  # Toast notification system
│   └── lib/                    # API client, types, formatting helpers
├── .env.example
└── .gitignore
```

## Getting started

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env          # only DATABASE_URL / CORS_ORIGINS are used here
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`. On first run it automatically creates
`skilltree.db` and seeds it with a realistic demo skill tree (an "AI Engineer" path plus
several side branches) so the app isn't empty. Interactive API docs: `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
cp ../.env.example .env.local    # only NEXT_PUBLIC_API_URL is used here
npm run dev
```

Visit `http://localhost:3000`.

## Design principles

- **Every number comes from the backend.** The frontend never calculates XP, levels, or
  progression — it only renders what `/api/*` returns. This makes the numbers trustworthy
  and prevents client-side tampering.
- **XP is deterministic, never random.** See `backend/services/xp_engine.py` for the exact
  formula and configurable constants (base rate, deep-work bonus, consistency bonus,
  difficulty multiplier).
- **Recommendations are rule-based**, not AI-generated. See
  `backend/services/recommendation.py` — no external API key required.
- **Demo data is clearly demo data.** It seeds one fictional "Demo User" and can be reset
  from Settings without affecting how the schema works for a real user later.

## Extending

- Add authentication by introducing a real session/user layer around the existing
  `get_or_create_user` helper in `main.py` — every endpoint already scopes queries by `user_id`.
- Swap SQLite for Postgres by changing `DATABASE_URL` — the SQLAlchemy models don't use any
  SQLite-specific features.
- Add more achievement rules in `achievement_engine.py`; the `check_achievements()` call in
  the learning-session endpoint runs after every logged session.
