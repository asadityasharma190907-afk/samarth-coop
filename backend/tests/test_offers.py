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
            verification_status="verified",
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
            dispatch_score=Decimal(10000),
            status="offered",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)

        token = create_access_token(data={"user_id": str(worker.id), "role": "worker"})

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
        assert booking is not None
        assert booking.status == "assigned"

        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer is not None
        assert offer.status == "accepted"

        profile = db.query(WorkerProfile).filter_by(user_id=worker_id).first()
        assert profile is not None
        assert profile.availability == False
    finally:
        db.close()


def test_accept_offer_already_assigned(worker_with_offer):
    token, _, booking_id, offer_id = worker_with_offer
    headers = {"Authorization": f"Bearer {token}"}

    # Manually set booking to assigned to simulate double-accept
    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking is not None
        booking.status = "assigned"  # type: ignore
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
    token, _, _, offer_id = worker_with_offer
    headers = {"Authorization": f"Bearer {token}"}

    # Manually expire the offer
    db = TestingSessionLocal()
    try:
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer is not None
        offer.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)  # type: ignore
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
        assert offer is not None
        assert offer.status == "expired"
    finally:
        db.close()


def test_decline_offer_success_cascade(worker_with_offer):
    token, _, booking_id, offer_id = worker_with_offer

    # Add a second worker to catch the cascade
    db = TestingSessionLocal()
    try:
        worker2 = User(
            name="Priya Worker",
            phone="9777777777",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add(worker2)
        db.commit()
        db.refresh(worker2)

        profile2 = WorkerProfile(
            user_id=worker2.id,
            skill="electrician",
            lat=26.9125,
            lng=75.7874,
            rating=4.0,
            verification_status="verified",
            availability=True,
        )
        db.add(profile2)
        db.commit()
        worker2_id = worker2.id
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/booking-offers/{offer_id}",
        json={"action": "decline"},
        headers=headers,
    )

    assert response.status_code == 200

    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking is not None
        assert booking.status == "pending"

        old_offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert old_offer is not None
        assert old_offer.status == "declined"

        # Check new offer
        new_offer = db.query(BookingOffer).filter_by(worker_id=worker2_id).first()
        assert new_offer is not None
        assert new_offer.status == "offered"
        assert new_offer.rank_at_offer == 2
        assert new_offer.booking_id == booking_id
    finally:
        db.close()


def test_cascade_exhaustion_cancels_booking(worker_with_offer):
    token, _, booking_id, offer_id = worker_with_offer
    headers = {"Authorization": f"Bearer {token}"}

    # Only 1 worker in DB, declining should exhaust options
    response = client.put(
        f"/booking-offers/{offer_id}",
        json={"action": "decline"},
        headers=headers,
    )

    assert response.status_code == 200

    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking is not None
        assert booking.status == "cancelled"

        old_offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert old_offer is not None
        assert old_offer.status == "declined"
    finally:
        db.close()


def test_lazy_expiry_on_read(worker_with_offer):
    _, _, booking_id, offer_id = worker_with_offer

    # Add a second worker to catch the cascade
    db = TestingSessionLocal()
    try:
        worker2 = User(
            name="Priya Worker 2",
            phone="9777777778",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add(worker2)
        db.commit()
        db.refresh(worker2)

        profile2 = WorkerProfile(
            user_id=worker2.id,
            skill="electrician",
            lat=26.9125,
            lng=75.7874,
            rating=4.0,
            verification_status="verified",
            availability=True,
        )
        db.add(profile2)
        db.commit()

        # Manually expire the first offer
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer is not None
        offer.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)  # type: ignore
        db.commit()
    finally:
        db.close()

    # Read the offers (triggers lazy expiry)
    response = client.get(f"/booking-offers/booking/{booking_id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    # The first offer should be expired
    assert data[0]["worker_name"] == "Suresh Worker"
    assert data[0]["status"] == "expired"

    # The second offer should be offered
    assert data[1]["worker_name"] == "Priya Worker 2"
    assert data[1]["status"] == "offered"
    assert data[1]["rank_at_offer"] == 2


def test_lazy_expiry_on_action(worker_with_offer):
    token, _, booking_id, offer_id = worker_with_offer

    # Manually expire the first offer
    db = TestingSessionLocal()
    try:
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer is not None
        offer.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)  # type: ignore
        db.commit()
    finally:
        db.close()

    # Act on the offer (triggers lazy expiry)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/booking-offers/{offer_id}",
        json={"action": "accept"},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Offer has expired"

    db = TestingSessionLocal()
    try:
        # According to the lazy expiry, it should also update status
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer is not None
        assert offer.status == "expired"

        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking is not None
        assert (
            booking.status == "cancelled"
        )  # Because there are no more workers to cascade to
    finally:
        db.close()


def test_worker_offers_citizen_trust_tiers(worker_with_offer):
    token, _, booking_id, _ = worker_with_offer
    headers = {"Authorization": f"Bearer {token}"}

    # Case 1: Citizen trust score = 100 (Normal / >= 80)
    response = client.get("/booking-offers/worker", headers=headers)
    assert response.status_code == 200
    offers = response.json()
    assert len(offers) == 1
    assert offers[0]["citizen_trust_score"] == 100
    assert offers[0]["citizen_trust_level"] is None

    # Case 2: Citizen trust score = 70 (60-79 -> high_cancellation)
    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        citizen = db.query(User).filter_by(id=booking.citizen_id).first()
        citizen.citizen_trust_score = 70
        db.commit()
    finally:
        db.close()

    response = client.get("/booking-offers/worker", headers=headers)
    assert response.status_code == 200
    offers = response.json()
    assert offers[0]["citizen_trust_score"] == 70
    assert offers[0]["citizen_trust_level"] == "high_cancellation"

    # Case 3: Citizen trust score = 50 (40-59 -> confirm_required)
    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        citizen = db.query(User).filter_by(id=booking.citizen_id).first()
        citizen.citizen_trust_score = 50
        db.commit()
    finally:
        db.close()

    response = client.get("/booking-offers/worker", headers=headers)
    assert response.status_code == 200
    offers = response.json()
    assert offers[0]["citizen_trust_score"] == 50
    assert offers[0]["citizen_trust_level"] == "confirm_required"

    # Case 4: Citizen trust score = 30 (< 40 -> restricted)
    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        citizen = db.query(User).filter_by(id=booking.citizen_id).first()
        citizen.citizen_trust_score = 30
        db.commit()
    finally:
        db.close()

    response = client.get("/booking-offers/worker", headers=headers)
    assert response.status_code == 200
    offers = response.json()
    assert offers[0]["citizen_trust_score"] == 30
    assert offers[0]["citizen_trust_level"] == "restricted"
