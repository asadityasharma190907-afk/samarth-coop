import uuid
from decimal import Decimal

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.models.user import User
from app.models.worker_profile import WorkerProfile
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


@pytest.fixture
def seeded_worker():
    db = TestingSessionLocal()
    try:
        worker = User(
            name="Suresh Worker",
            phone="9888888888",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add(worker)
        db.commit()
        db.refresh(worker)

        profile = WorkerProfile(
            user_id=worker.id,
            skill="electrician",
            lat=26.9125,
            lng=75.7874,
            rating=4.5,
            verified=True,
            availability=True,
        )
        db.add(profile)
        db.commit()
        return worker.id
    finally:
        db.close()


def test_create_booking_authenticated(citizen_token, seeded_worker):
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

        # Verify offer is created
        offer = (
            db.query(BookingOffer)
            .filter(BookingOffer.booking_id == booking_uuid)
            .first()
        )
        assert offer is not None
        assert offer.worker_id == seeded_worker
        assert offer.status == "offered"
        assert offer.rank_at_offer == 1
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


def test_create_booking_no_workers_cancelled(citizen_token):
    token, _ = citizen_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
        "description": "Fix ceiling fan",
    }
    # No worker seeded, so should cancel
    response = client.post("/bookings", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "cancelled"

    db = TestingSessionLocal()
    try:
        booking_uuid = uuid.UUID(data["booking_id"])
        offers_count = (
            db.query(BookingOffer)
            .filter(BookingOffer.booking_id == booking_uuid)
            .count()
        )
        assert offers_count == 0
    finally:
        db.close()


def test_get_booking_offers_audit_trail(citizen_token, seeded_worker):
    token, _ = citizen_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create booking which triggers offer dispatch
    payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
        "description": "Fix ceiling fan in living room",
    }
    response = client.post("/bookings", json=payload, headers=headers)
    booking_id = response.json()["booking_id"]

    # Fetch audit trail
    response = client.get(f"/booking-offers/booking/{booking_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    offer = data[0]
    assert offer["booking_id"] == booking_id
    assert offer["worker_id"] == str(seeded_worker)
    assert offer["rank_at_offer"] == 1
    assert offer["status"] == "offered"
    assert "dispatch_score" in offer
    assert "expires_at" in offer


def test_complete_booking_success(citizen_token, seeded_worker):
    token, _ = citizen_token
    worker_token = create_access_token(
        data={"user_id": str(seeded_worker), "role": "worker"}
    )
    worker_headers = {"Authorization": f"Bearer {worker_token}"}
    citizen_headers = {"Authorization": f"Bearer {token}"}

    # Create booking
    payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
        "description": "Fix ceiling fan",
    }
    response = client.post("/bookings", json=payload, headers=citizen_headers)
    booking_id = response.json()["booking_id"]

    db = TestingSessionLocal()
    try:
        # Find offer and assign booking manually (simulate accept)
        offer = (
            db.query(BookingOffer).filter_by(booking_id=uuid.UUID(booking_id)).first()
        )
        assert offer is not None
        offer.status = "accepted"  # type: ignore
        booking = db.query(Booking).filter_by(id=uuid.UUID(booking_id)).first()
        assert booking is not None
        booking.status = "assigned"  # type: ignore

        # Make worker unavailable
        profile = db.query(WorkerProfile).filter_by(user_id=seeded_worker).first()
        assert profile is not None
        profile.availability = False  # type: ignore
        db.commit()
    finally:
        db.close()

    # Complete booking
    comp_response = client.put(
        f"/bookings/{booking_id}/complete", headers=worker_headers
    )
    assert comp_response.status_code == 200
    comp_data = comp_response.json()
    assert comp_data["status"] == "completed"

    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=uuid.UUID(booking_id)).first()
        assert booking is not None
        assert booking.status == "completed"
        assert booking.platform_fee == Decimal("25.00")

        profile = db.query(WorkerProfile).filter_by(user_id=seeded_worker).first()
        assert profile is not None
        assert profile.availability == True
    finally:
        db.close()


def test_complete_booking_forbidden(citizen_token, seeded_worker):
    token, _ = citizen_token
    citizen_headers = {"Authorization": f"Bearer {token}"}

    db = TestingSessionLocal()
    try:
        other_worker = User(
            name="Other Worker",
            phone="9999999999",
            password_hash="fake",
            role="worker",
        )
        db.add(other_worker)
        db.commit()
        db.refresh(other_worker)
        other_worker_id = other_worker.id
    finally:
        db.close()

    other_worker_token = create_access_token(
        data={"user_id": str(other_worker_id), "role": "worker"}
    )
    other_worker_headers = {"Authorization": f"Bearer {other_worker_token}"}

    payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
    }
    response = client.post("/bookings", json=payload, headers=citizen_headers)
    booking_id = response.json()["booking_id"]

    db = TestingSessionLocal()
    try:
        offer = (
            db.query(BookingOffer).filter_by(booking_id=uuid.UUID(booking_id)).first()
        )
        assert offer is not None
        offer.status = "accepted"  # type: ignore
        booking = db.query(Booking).filter_by(id=uuid.UUID(booking_id)).first()
        assert booking is not None
        booking.status = "assigned"  # type: ignore
        db.commit()
    finally:
        db.close()

    comp_response = client.put(
        f"/bookings/{booking_id}/complete", headers=other_worker_headers
    )
    assert comp_response.status_code == 403


def test_complete_unassigned_booking(citizen_token, seeded_worker):
    token, _ = citizen_token
    citizen_headers = {"Authorization": f"Bearer {token}"}
    worker_token = create_access_token(
        data={"user_id": str(seeded_worker), "role": "worker"}
    )
    worker_headers = {"Authorization": f"Bearer {worker_token}"}

    payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
    }
    response = client.post("/bookings", json=payload, headers=citizen_headers)
    booking_id = response.json()["booking_id"]

    # booking is pending, try to complete
    comp_response = client.put(
        f"/bookings/{booking_id}/complete", headers=worker_headers
    )
    assert comp_response.status_code == 400
