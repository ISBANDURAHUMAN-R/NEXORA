# SKILLTREE

> **Visual RPG-Style Developer Progression System**  
> A premium, deterministic skill tree and career acceleration engine for software engineers and AI practitioners.

---

## 🌟 Concept

**SKILLTREE** bridges developer productivity with visual RPG skill tree mechanics. Developers input their technical skills, current proficiencies, and deliberate practice sessions. The engine calculates:
- Interconnected Directed Acyclic Graph (DAG) dependencies
- Prerequisites and unlock conditions
- Real-time deterministic XP and level curves
- Explainable, rule-based next skill recommendations
- Multi-dimensional analytics across cognitive intensity and deliberate focus

No random XP. No childish gimmicks. Clean, futuristic dark-mode developer ergonomics.

---

## 🛠 Tech Stack

- **Backend**: Python 3.14+, FastAPI, SQLAlchemy, SQLite, Pydantic V2
- **Frontend**: Next.js (App Router), React 19, TypeScript, Tailwind CSS
- **Visualization & Charts**: Recharts, SVG/Canvas Interactive Pan-Zoom DAG Visualizer, Canvas Confetti
- **Icons**: Lucide Icons

---

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
# Server runs at http://127.0.0.1:8000
# OpenAPI Docs: http://127.0.0.1:8000/docs
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:3000
```

---

## 🕹 Features & Views

### 1. Dashboard
- **Level & Total XP Bar**: Visual progress toward overall developer level.
- **Node Breakdown**: Total (24), Mastered (8), In Progress (9), Locked (7).
- **Discipline Metrics**: Learning streak counter with consistency bonus, weekly XP velocity, and hours invested.
- **Rule-Based Recommendations**: Ranked next skills with clear rationale (gateway skills, goal alignment, momentum).

### 2. Interactive Skill Tree
- **Pan & Zoom Canvas**: Drag to pan, wheel/buttons to zoom, reset view.
- **Node State Machine**:
  - `MASTERED`: Emerald glow, 100% completion bar.
  - `IN PROGRESS`: Cyan/purple active glow with real-time level gauge.
  - `AVAILABLE`: Pulsing glow indicating all prerequisites are met.
  - `LOCKED`: Muted zinc dashed border with lock icon and required levels.
- **Connector Graph**: Curved bezier SVG edges displaying active flow vs. locked dependencies.
- **Node Inspection Drawer**: Prerequisite checklist with checkmarks, downstream unlocks, and quick session logger.

### 3. Skills Catalog
- Comprehensive library with search, category filtering (Programming, AI/ML, Data Science, Mathematics, DevOps, etc.), and status pills.
- Modal to create custom skills and wire custom prerequisite relationships.

### 4. Learning Log
- Record deliberate practice sessions with duration, activity description, cognitive intensity (Easy, Medium, Hard), and deep work focus.
- Deterministic XP calculation with itemized breakdown cards.

### 5. Telemetry & Analytics
- Interactive Recharts graphs with 7D, 30D, 90D, and All-Time filters:
  - Cumulative & daily XP velocity
  - Learning hours over time
  - Category distribution donut chart
  - Weekly consistency by day of the week
  - Most practiced skills ranking

### 6. Milestone Goals
- Set deadline-bound goals targeting specific skill levels.
- Automatic progress synchronization linked directly to learning logs.

### 7. Achievements
- Subtle gamification milestones: First Step, 7-Day Consistency, Deep Worker, Level Up, Master, Multi-Talent, etc.

### 8. Settings & XP Curves
- Fully configurable deterministic parameters:
  - 30-minute base XP
  - 60-minute base XP
  - Deep work multiplier (+10%)
  - Daily consistency multiplier (+5%)
- One-click "Reset Demo Data" button.

---

## 🧪 Testing

Run backend tests:
```bash
cd backend
python -m pytest tests/
```
All 12 engine tests, API routes, and end-to-end learning session cycles pass cleanly.
