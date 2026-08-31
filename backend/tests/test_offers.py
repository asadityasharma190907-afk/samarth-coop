import uuid
from datetime import datetime, timedelta, timezone
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
def worker_with_offer():
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
        db.commit()
        db.refresh(citizen)
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

        booking = Booking(
            citizen_id=citizen.id,
            skill="electrician",
            lat=26.9124,
            lng=75.7873,
            description="Fix fan",
            job_price=Decimal("500.00"),
            platform_fee=Decimal("25.00"),
            status="pending",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        offer = BookingOffer(
            booking_id=booking.id,
            worker_id=worker.id,
            rank_at_offer=1,
            dispatch_score=Decimal("10000"),
            status="offered",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)

        token = create_access_token(
            data={"user_id": str(worker.id), "role": "worker"}
        )
        
        return token, worker.id, booking.id, offer.id
    finally:
        db.close()


def test_accept_offer_success(worker_with_offer):
    token, worker_id, booking_id, offer_id = worker_with_offer
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put(
        f"/booking-offers/{offer_id}",
        json={"action": "accept"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking.status == "assigned"
        
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer.status == "accepted"
        
        profile = db.query(WorkerProfile).filter_by(user_id=worker_id).first()
        assert profile.availability == False
    finally:
        db.close()


def test_accept_offer_already_assigned(worker_with_offer):
    token, worker_id, booking_id, offer_id = worker_with_offer
    headers = {"Authorization": f"Bearer {token}"}

    # Manually set booking to assigned to simulate double-accept
    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        booking.status = "assigned"
        db.commit()
    finally:
        db.close()

    response = client.put(
        f"/booking-offers/{offer_id}",
        json={"action": "accept"},
        headers=headers,
    )
    assert response.status_code == 409
    assert "already assigned" in response.json()["detail"]


def test_accept_expired_offer(worker_with_offer):
    token, worker_id, booking_id, offer_id = worker_with_offer
    headers = {"Authorization": f"Bearer {token}"}

    # Manually expire the offer
    db = TestingSessionLocal()
    try:
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        offer.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        db.commit()
    finally:
        db.close()

    response = client.put(
        f"/booking-offers/{offer_id}",
        json={"action": "accept"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"]

    db = TestingSessionLocal()
    try:
        # According to the lazy expiry, it should also update status
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer.status == "expired"
    finally:
        db.close()
