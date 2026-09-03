import uuid
from datetime import datetime, timedelta, timezone

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.seed import seed_data

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db_monkeypatch(monkeypatch):
    monkeypatch.setattr("app.seed.SessionLocal", TestingSessionLocal)
    yield


def login(phone: str, password: str = "password123"):
    response = client.post("/auth/login", json={"phone": phone, "password": password})
    assert response.status_code == 200, f"Login failed for {phone}: {response.text}"
    return response.json()["access_token"]


def backdate_offer_expiry(booking_id: uuid.UUID, rank: int, worker_id: uuid.UUID):
    db = TestingSessionLocal()
    try:
        offer = (
            db.query(BookingOffer)
            .filter_by(booking_id=booking_id, worker_id=worker_id, rank_at_offer=rank)
            .first()
        )
        assert offer is not None, (
            f"No offer found for worker {worker_id} at rank {rank}"
        )

        # Backdate the expiration to 10 seconds ago
        offer.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)  # type: ignore
        db.commit()
    finally:
        db.close()


def get_worker_id(phone: str) -> uuid.UUID:
    db = TestingSessionLocal()
    from app.models.user import User

    try:
        user = db.query(User).filter(User.phone == phone).first()
        assert user is not None
        return user.id
    finally:
        db.close()


def get_offer_status(offer_id: uuid.UUID) -> str:
    db = TestingSessionLocal()
    try:
        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer is not None
        return offer.status
    finally:
        db.close()


def test_lazy_expiry_cascade_e2e():
    # 1. Start fresh and seed DB
    seed_data()

    # Phones mapped from seed.py / test_e2e_demo.py
    # Ravi: 9555555555
    # Suresh: 9111111111 (Rank 1)
    # Priya: 9222222222 (Rank 2)
    # Anil: 9333333333 (Rank 3)
    # Meena: 9444444444 (Rank 4)

    suresh_id = get_worker_id("9111111111")
    priya_id = get_worker_id("9222222222")
    anil_id = get_worker_id("9333333333")
    meena_id = get_worker_id("9444444444")

    suresh_token = login("9111111111")
    priya_token = login("9222222222")
    anil_token = login("9333333333")
    meena_token = login("9444444444")
    admin_token = login("9000000000")

    ravi_token = login("9555555555")
    booking_payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
        "description": "Fixing a main circuit board.",
        "job_price": 500,
    }

    # Step 1: Citizen Ravi books electrician → Offer dispatched to Suresh (Rank 1, expires in 2 min)
    res = client.post(
        "/bookings",
        json=booking_payload,
        headers={"Authorization": f"Bearer {ravi_token}"},
    )
    assert res.status_code == 201, res.text
    booking_id = uuid.UUID(res.json()["booking_id"])

    # Verify Suresh got the offer (Rank 1)
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {suresh_token}"}
    )
    assert res.status_code == 200
    suresh_offers = res.json()
    assert len(suresh_offers) == 1
    suresh_offer_id = uuid.UUID(suresh_offers[0]["id"])
    assert suresh_offers[0]["rank_at_offer"] == 1

    # Step 2: Artificially backdate Suresh's offer
    backdate_offer_expiry(booking_id, 1, suresh_id)

    # Step 3 & 4: Priya calls GET /booking-offers/worker
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {priya_token}"}
    )
    assert res.status_code == 200
    priya_offers = res.json()
    # It should have lazily expired Suresh's offer and dispatched to Priya
    assert len(priya_offers) == 1
    priya_offer_id = uuid.UUID(priya_offers[0]["id"])
    assert priya_offers[0]["rank_at_offer"] == 2

    # Verify Suresh's offer is now "expired"
    assert get_offer_status(suresh_offer_id) == "expired"

    # Step 5: Repeat for Priya to reach Anil
    backdate_offer_expiry(booking_id, 2, priya_id)
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {anil_token}"}
    )
    assert res.status_code == 200
    anil_offers = res.json()
    assert len(anil_offers) == 1
    anil_offer_id = uuid.UUID(anil_offers[0]["id"])
    assert anil_offers[0]["rank_at_offer"] == 3
    assert get_offer_status(priya_offer_id) == "expired"

    # Repeat for Anil to reach Meena
    backdate_offer_expiry(booking_id, 3, anil_id)
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {meena_token}"}
    )
    assert res.status_code == 200
    meena_offers = res.json()
    assert len(meena_offers) == 1
    assert meena_offers[0]["rank_at_offer"] == 4
    assert get_offer_status(anil_offer_id) == "expired"

    # Repeat for Meena to exhaust cascade
    backdate_offer_expiry(booking_id, 4, meena_id)
    # Trigger lazy cascade reading as admin to verify it handles exhaust correctly
    res = client.get(
        f"/booking-offers/booking/{booking_id!s}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    all_offers = res.json()
    assert len(all_offers) == 4
    for o in all_offers:
        assert o["status"] == "expired"

    # Verify booking status automatically transitions to 'cancelled'
    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking is not None
        assert booking.status == "cancelled"
    finally:
        db.close()
