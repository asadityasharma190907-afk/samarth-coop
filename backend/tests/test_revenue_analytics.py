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


def test_revenue_analytics_endpoint():
    # Seed the DB (which creates 4 completed bookings with different prices/surges)
    seed_data()

    response = client.get("/analytics/revenue")
    assert response.status_code == 200

    data = response.json()
    assert data["period"] == "current_month"

    # Check that basic structural metrics are present
    assert "total_bookings" in data
    assert "completed_bookings" in data
    assert "gross_merchandise_value" in data
    assert "platform_revenue_2_5_pct" in data
    assert "welfare_fund_collected_2_5_pct" in data
    assert "payment_gateway_cost_est_2_pct" in data
    assert "net_platform_margin" in data
    assert "avg_order_value" in data
    assert "breakeven_bookings_per_month" in data
    assert "current_pct_of_breakeven" in data
    assert "surge_revenue" in data

    # Based on the seed data, there should be some completed bookings
    assert data["completed_bookings"] > 0
    assert data["gross_merchandise_value"] > 0

    # 5% platform fee split into 2.5% each
    assert data["platform_revenue_2_5_pct"] == data["welfare_fund_collected_2_5_pct"]

    # PG Cost is 2% of GMV
    assert data["payment_gateway_cost_est_2_pct"] == round(
        data["gross_merchandise_value"] * 0.02, 2
    )

    # Net platform margin
    expected_margin = (
        data["platform_revenue_2_5_pct"] - data["payment_gateway_cost_est_2_pct"]
    )
    assert data["net_platform_margin"] == round(expected_margin, 2)

    # Avg order value
    expected_aov = data["gross_merchandise_value"] / data["completed_bookings"]
    assert data["avg_order_value"] == round(expected_aov, 2)

    # Breakeven trajectory
    baseline_cost = 6750.00
    expected_pct = (data["net_platform_margin"] / baseline_cost) * 100
    assert data["current_pct_of_breakeven"] == round(expected_pct, 1)


def test_revenue_analytics_empty_db():
    # Calling endpoint without seeding data
    response = client.get("/analytics/revenue")
    assert response.status_code == 200

    data = response.json()
    assert data["total_bookings"] == 0
    assert data["completed_bookings"] == 0
    assert data["gross_merchandise_value"] == 0.0
    assert data["platform_revenue_2_5_pct"] == 0.0
    assert data["welfare_fund_collected_2_5_pct"] == 0.0
    assert data["payment_gateway_cost_est_2_pct"] == 0.0
    assert data["net_platform_margin"] == 0.0
    assert data["avg_order_value"] == 0.0
    assert data["breakeven_bookings_per_month"] == 0
    assert data["current_pct_of_breakeven"] == 0.0
    assert data["surge_revenue"] == 0.0
