# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.models import User, Referral, RewardConfig

client = TestClient(app)

# Setup test database
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    # Clean up
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Backend is Running" in response.json()["status"]

def test_generate_referral_code():
    response = client.post("/api/referral/generate", params={"user_id": "TestUser"})
    assert response.status_code == 200
    data = response.json()
    assert "referral_code" in data
    assert data["referral_code"].startswith("SVH-")

def test_analytics_summary():
    response = client.get("/api/referral/analytics/summary", params={"user_id": "TestUser"})
    assert response.status_code == 200
    data = response.json()
    assert "my_referral_code" in data
    assert "total_referrals" in data
    assert "conversion_rate" in data

def test_admin_endpoint_without_auth():
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 403  # Forbidden without admin token

def test_admin_endpoint_with_auth():
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": "Bearer admin-token"}
    )
    assert response.status_code == 200

def test_reward_summary():
    response = client.get("/api/rewards/summary", params={"user_id": "TestUser"})
    assert response.status_code == 200
    data = response.json()
    assert "total_earned" in data
    assert "pending" in data
    assert "credited" in data