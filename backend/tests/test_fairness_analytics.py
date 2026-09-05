import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed_data
from app.services.analytics import compute_gini

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db_monkeypatch(monkeypatch):
    monkeypatch.setattr("app.seed.SessionLocal", TestingSessionLocal)
    yield


def test_compute_gini_unit():
    assert compute_gini([]) == 0.0
    assert compute_gini([500.0]) == 0.0
    assert compute_gini([0.0, 0.0, 0.0]) == 0.0
    # Perfect equality
    assert compute_gini([1000.0, 1000.0, 1000.0, 1000.0]) == 0.0
    # Inequality
    gini = compute_gini([0.0, 200.0, 2000.0, 4500.0])
    assert 0.0 < gini < 1.0


def test_fairness_analytics_endpoint():
    seed_data()

    response = client.get("/analytics/fairness")
    assert response.status_code == 200

    data = response.json()
    assert "samarth_gini" in data
    assert "proximity_gini" in data
    assert "gini_improvement_pct" in data
    assert "income_range" in data
    assert "meena_effect_count" in data
    assert "meena_effect_description" in data
    assert "offers_distribution" in data
    assert data["total_active_workers"] == 4

    # Validate income range
    income = data["income_range"]
    assert income["min_earnings"] == 0.0  # Priya
    assert income["max_earnings"] == 4500.0  # Meena
    assert income["average_earnings"] > 0

    # Validate offers distribution
    offers = data["offers_distribution"]
    assert len(offers) == 4
    worker_names = [o["worker_name"] for o in offers]
    assert "Suresh Kumar" in worker_names
    assert "Priya Gupta" in worker_names
    assert "Anil Yadav" in worker_names
    assert "Meena Verma" in worker_names

    # Check Gini comparison
    assert data["samarth_gini"] < data["proximity_gini"]
    assert data["gini_improvement_pct"] > 0
