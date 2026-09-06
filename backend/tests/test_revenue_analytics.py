from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_revenue_analytics(setup_db):
    response = client.get("/analytics/revenue")
    assert response.status_code == 200
    data = response.json()
    assert "gmv" in data
    assert "platform_revenue" in data
    assert "revenue_streams" in data
    assert isinstance(data["revenue_streams"], list)
