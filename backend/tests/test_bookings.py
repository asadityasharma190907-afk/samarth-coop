import uuid
from decimal import Decimal

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.user import User
from app.services.auth import create_access_token, hash_password

client = TestClient(app)


@pytest.fixture
def citizen_token():
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
        return token, citizen.id
    finally:
        db.close()


def test_create_booking_authenticated(citizen_token):
    token, citizen_id = citizen_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
        "description": "Fix ceiling fan in living room",
    }

    response = client.post("/bookings", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()

    assert "booking_id" in data
    assert data["status"] == "pending"
    assert Decimal(str(data["job_price"])) == Decimal("500.00")
    assert data["skill"] == "electrician"
    assert float(data["lat"]) == pytest.approx(26.9124, abs=1e-4)
    assert float(data["lng"]) == pytest.approx(75.7873, abs=1e-4)
    assert data["description"] == "Fix ceiling fan in living room"

    # Verify directly in database
    db = TestingSessionLocal()
    try:
        booking_uuid = uuid.UUID(data["booking_id"])
        booking = db.query(Booking).filter(Booking.id == booking_uuid).first()
        assert booking is not None
        assert booking.citizen_id == citizen_id
        assert booking.status == "pending"
        assert booking.job_price == Decimal("500.00")
        assert booking.platform_fee == Decimal("25.00")
    finally:
        db.close()


def test_create_booking_unauthenticated():
    payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
        "description": "Fix ceiling fan",
    }
    response = client.post("/bookings", json=payload)
    assert response.status_code == 401


def test_create_booking_price_snapshot_by_category(citizen_token):
    token, _ = citizen_token
    headers = {"Authorization": f"Bearer {token}"}

    # Plumber should be 450.00
    response = client.post(
        "/bookings",
        json={"skill": "plumber", "lat": 26.9124, "lng": 75.7873},
        headers=headers,
    )
    assert response.status_code == 201
    assert Decimal(str(response.json()["job_price"])) == Decimal("450.00")

    # Carpenter should be 600.00
    response = client.post(
        "/bookings",
        json={"skill": "carpenter", "lat": 26.9124, "lng": 75.7873},
        headers=headers,
    )
    assert response.status_code == 201
    assert Decimal(str(response.json()["job_price"])) == Decimal("600.00")


def test_create_booking_validation_error(citizen_token):
    token, _ = citizen_token
    headers = {"Authorization": f"Bearer {token}"}

    # Missing skill
    response = client.post(
        "/bookings",
        json={"lat": 26.9124, "lng": 75.7873},
        headers=headers,
    )
    assert response.status_code == 422

    # Missing lat/lng
    response = client.post(
        "/bookings",
        json={"skill": "electrician"},
        headers=headers,
    )
    assert response.status_code == 422
