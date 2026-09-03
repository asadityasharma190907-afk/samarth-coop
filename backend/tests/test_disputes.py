import uuid

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import create_access_token, hash_password

client = TestClient(app)


@pytest.fixture
def test_users():
    db = TestingSessionLocal()
    try:
        citizen = User(
            name="Ravi Citizen",
            phone="9555555555",
            password_hash=hash_password("password123"),
            role="citizen",
        )
        db.add(citizen)

        worker = User(
            name="Suresh Worker",
            phone="9888888888",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add(worker)

        other_user = User(
            name="Other Citizen",
            phone="9111111111",
            password_hash=hash_password("password123"),
            role="citizen",
        )
        db.add(other_user)

        db.commit()
        db.refresh(citizen)
        db.refresh(worker)
        db.refresh(other_user)

        profile = WorkerProfile(
            user_id=worker.id,
            skill="electrician",
            lat=26.9125,
            lng=75.7874,
            rating=4.5,
            verification_status="verified",
            availability=True,
        )
        db.add(profile)
        db.commit()

        c_token = create_access_token(
            data={"user_id": str(citizen.id), "role": "citizen"}
        )
        w_token = create_access_token(
            data={"user_id": str(worker.id), "role": "worker"}
        )
        o_token = create_access_token(
            data={"user_id": str(other_user.id), "role": "citizen"}
        )

        return {
            "citizen_id": citizen.id,
            "citizen_token": c_token,
            "worker_id": worker.id,
            "worker_token": w_token,
            "other_token": o_token,
        }
    finally:
        db.close()


@pytest.fixture
def assigned_booking(test_users):
    db = TestingSessionLocal()
    booking_id = uuid.uuid4()
    try:
        booking = Booking(
            id=booking_id,
            citizen_id=test_users["citizen_id"],
            worker_id=test_users["worker_id"],
            skill="electrician",
            lat=26.9,
            lng=75.7,
            job_price=500,
            status="assigned",
        )
        db.add(booking)
        db.commit()
        return booking_id
    finally:
        db.close()


@pytest.fixture
def pending_booking(test_users):
    db = TestingSessionLocal()
    booking_id = uuid.uuid4()
    try:
        booking = Booking(
            id=booking_id,
            citizen_id=test_users["citizen_id"],
            skill="electrician",
            lat=26.9,
            lng=75.7,
            job_price=500,
            status="pending",
        )
        db.add(booking)
        db.commit()
        return booking_id
    finally:
        db.close()


def test_dispute_booking_by_citizen(test_users, assigned_booking):
    headers = {"Authorization": f"Bearer {test_users['citizen_token']}"}
    payload = {"reason": "Worker never showed up."}

    response = client.post(
        f"/bookings/{assigned_booking}/dispute", json=payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disputed"
    assert data["dispute_reason"] == "Worker never showed up."
    assert "mediation initiated" in data["message"]

    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=assigned_booking).first()
        assert booking is not None
        assert booking.status == "disputed"
        assert booking.dispute_reason == "Worker never showed up."
    finally:
        db.close()


def test_dispute_booking_by_worker(test_users, assigned_booking):
    headers = {"Authorization": f"Bearer {test_users['worker_token']}"}
    payload = {"reason": "Citizen refused to pay for materials."}

    response = client.post(
        f"/bookings/{assigned_booking}/dispute", json=payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disputed"
    assert data["dispute_reason"] == "Citizen refused to pay for materials."


def test_dispute_booking_unauthorized(test_users, assigned_booking):
    headers = {"Authorization": f"Bearer {test_users['other_token']}"}
    payload = {"reason": "I am an interloper."}

    response = client.post(
        f"/bookings/{assigned_booking}/dispute", json=payload, headers=headers
    )
    assert response.status_code == 403


def test_dispute_invalid_state(test_users, pending_booking):
    headers = {"Authorization": f"Bearer {test_users['citizen_token']}"}
    payload = {"reason": "I don't like this pending booking."}

    response = client.post(
        f"/bookings/{pending_booking}/dispute", json=payload, headers=headers
    )
    assert response.status_code == 400


def test_dispute_empty_reason(test_users, assigned_booking):
    headers = {"Authorization": f"Bearer {test_users['citizen_token']}"}

    # Empty string
    response = client.post(
        f"/bookings/{assigned_booking}/dispute", json={"reason": ""}, headers=headers
    )
    assert response.status_code == 422

    # Whitespace only
    response = client.post(
        f"/bookings/{assigned_booking}/dispute", json={"reason": "   "}, headers=headers
    )
    assert response.status_code == 422
