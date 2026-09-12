import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import Skill
from services.demo_seed import reset_demo_data

from routers import (
    dashboard,
    skills,
    tree,
    learning,
    analytics,
    goals,
    achievements,
    settings,
    demo
)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Skill).count() == 0:
            print("[SKILLTREE] Seeding initial demo data...")
            reset_demo_data(db)
            print("[SKILLTREE] Demo data seeded successfully.")
    finally:
        db.close()

# Initialize tables immediately so TestClient and direct imports work seamlessly
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="SKILLTREE API",
    description="Deterministic RPG-style Developer Skill Progression Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(dashboard.router)
app.include_router(skills.router)
app.include_router(tree.router)
app.include_router(learning.router)
app.include_router(analytics.router)
app.include_router(goals.router)
app.include_router(achievements.router)
app.include_router(settings.router)
app.include_router(demo.router)

@app.get("/")
def root():
    return {
        "app": "SKILLTREE API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
