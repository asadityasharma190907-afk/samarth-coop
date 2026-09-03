import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.seed import seed_data
from app.services.auth import create_access_token, hash_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db_monkeypatch(monkeypatch):
    # Monkeypatch SessionLocal in seed to use TestingSessionLocal from conftest
    monkeypatch.setattr("app.seed.SessionLocal", TestingSessionLocal)
    yield


def test_earnings_distribution_with_seed_data():
    seed_data()

    response = client.get("/federation/earnings-distribution")
    assert response.status_code == 200

    data = response.json()
    assert data["currency"] == "INR"
    assert data["total_workers"] == 4

    buckets = data["buckets"]
    assert len(buckets) == 4

    # Check ranges
    assert buckets[0]["range_label"] == "₹0 - ₹500"
    assert buckets[1]["range_label"] == "₹501 - ₹1500"
    assert buckets[2]["range_label"] == "₹1501 - ₹3000"
    assert buckets[3]["range_label"] == "₹3001+"

    # Based on seed data:
    # Suresh earned: 210.53 * 0.95 = 200 -> bucket 0
    # Priya earned: 0 -> bucket 0
    # Anil earned: 2105.26 * 0.95 = 2000 -> bucket 2
    # Meena earned: 4736.84 * 0.95 = 4500 -> bucket 3

    # Verify bucket 0 (0 - 500)
    assert buckets[0]["worker_count"] == 2

    # Verify bucket 1 (501 - 1500)
    assert buckets[1]["worker_count"] == 0

    # Verify bucket 2 (1501 - 3000)
    assert buckets[2]["worker_count"] == 1

    # Verify bucket 3 (3001+)
    assert buckets[3]["worker_count"] == 1


def test_export_earnings_unauthorized():
    response = client.get("/federation/export-earnings")
    assert response.status_code == 401


def test_export_earnings_forbidden():
    db = TestingSessionLocal()
    try:
        citizen = User(
            name="Ravi Citizen",
            phone="9555555555",
            password_hash=hash_password("password123"),
            role="citizen",
        )
        db.add(citizen)
        db.commit()
        db.refresh(citizen)
        token = create_access_token(
            data={"user_id": str(citizen.id), "role": "citizen"}
        )
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/federation/export-earnings", headers=headers)
    assert response.status_code == 403


def test_export_earnings_success():
    seed_data()

    db = TestingSessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        assert admin is not None
        token = create_access_token(data={"user_id": str(admin.id), "role": "admin"})
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/federation/export-earnings", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert (
        "samarth_weekly_earnings_report.csv" in response.headers["content-disposition"]
    )

    csv_content = response.text
    assert (
        "Worker ID,Worker Name,Skill,Rating,Completed Jobs This Week,Weekly Earnings (INR),Welfare Fund Contributed (INR)"
        in csv_content
    )
    assert "Suresh Kumar,electrician,4.2,1,200.00,10.53" in csv_content
    assert "Meena Verma,electrician,4.9,1,4500.00,236.84" in csv_content
