import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_dashboard():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "user_level" in data
    assert "total_xp" in data
    assert "total_skills" in data
    assert "mastered_skills" in data
    assert "in_progress_skills" in data
    assert "locked_skills" in data
    assert data["total_skills"] >= 20

def test_skill_tree():
    response = client.get("/api/skill-tree")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 20
    assert len(data["edges"]) >= 10

def test_get_skills():
    response = client.get("/api/skills")
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) >= 20

def test_analytics():
    response = client.get("/api/analytics?timeframe=30d")
    assert response.status_code == 200
    data = response.json()
    assert "xp_over_time" in data
    assert "category_distribution" in data

def test_goals():
    response = client.get("/api/goals")
    assert response.status_code == 200
    goals = response.json()
    assert isinstance(goals, list)

def test_achievements():
    response = client.get("/api/achievements")
    assert response.status_code == 200
    achs = response.json()
    assert len(achs) >= 6

def test_record_learning_session():
    # Fetch a skill to learn
    skills_resp = client.get("/api/skills")
    assert skills_resp.status_code == 200
    skills = skills_resp.json()
    target_skill = next(s for s in skills if s["status"] in ("IN_PROGRESS", "AVAILABLE"))

    post_data = {
        "skill_id": target_skill["id"],
        "duration_minutes": 60,
        "activity": "Deep learning research session",
        "difficulty": "Hard",
        "notes": "Testing integration flow with full XP breakdown",
        "is_deep_work": True
    }
    resp = client.post("/api/learning", json=post_data)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["xp_earned"] > 0
    assert len(res_data["xp_breakdown"]) >= 2
    assert "session" in res_data
    assert res_data["session"]["activity"] == "Deep learning research session"

def test_reset_demo_data():
    resp = client.post("/api/demo/reset")
    assert resp.status_code == 200
    dash_resp = client.get("/api/dashboard")
    assert dash_resp.status_code == 200
    data = dash_resp.json()
    assert data["total_skills"] == 24
    assert data["mastered_skills"] == 8
    assert data["in_progress_skills"] == 9
    assert data["locked_skills"] == 7
