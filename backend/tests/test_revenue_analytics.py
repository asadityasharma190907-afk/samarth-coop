import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed_data

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db_monkeypatch(monkeypatch):
    monkeypatch.setattr("app.seed.SessionLocal", TestingSessionLocal)
    yield

def test_get_revenue_analytics():
    seed_data()
    response = client.get("/analytics/revenue")
    assert response.status_code == 200
    data = response.json()
    assert "gmv" in data
    assert "platform_revenue" in data
    assert "revenue_streams" in data
    assert isinstance(data["revenue_streams"], list)
