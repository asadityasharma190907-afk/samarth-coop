import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed_data

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
