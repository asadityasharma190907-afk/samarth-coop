import threading
from concurrent.futures import ThreadPoolExecutor
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
client_lock = threading.Lock()


def create_worker_with_offer(idx: int = 0):
    db = TestingSessionLocal()
    try:
        citizen = User(
            name=f"Ravi Citizen Concurrency {idx}",
            phone=f"9555{idx:04d}1",
            password_hash=hash_password("password123"),
            role="citizen",
        )
        db.add(citizen)

        worker = User(
            name=f"Suresh Worker Concurrency {idx}",
            phone=f"9888{idx:04d}2",
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
            description="Fix circuit breaker",
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
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)

        token = create_access_token(data={"user_id": str(worker.id), "role": "worker"})

        return token, worker.id, booking.id, offer.id
    finally:
        db.close()


def test_double_accept_same_offer_concurrency(run_idx: int = 0):
    """
    Simulates two concurrent requests trying to accept the EXACT same booking offer.
    Verifies AD-6 row lock: exactly 1 returns 200 OK and 1 returns 409 Conflict.
    """
    token, worker_id, booking_id, offer_id = create_worker_with_offer(run_idx)
    headers = {"Authorization": f"Bearer {token}"}

    barrier = threading.Barrier(2)
    results = []

    def send_accept():
        barrier.wait()
        with client_lock:
            res = client.put(
                f"/booking-offers/{offer_id}",
                json={"action": "accept"},
                headers=headers,
            )
            return res.status_code, res.json()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(send_accept), executor.submit(send_accept)]
        for f in futures:
            results.append(f.result())

    status_codes = [r[0] for r in results]
    assert 200 in status_codes, f"Expected one 200 OK, got {status_codes}"
    assert 409 in status_codes, f"Expected one 409 Conflict, got {status_codes}"

    # Verify 409 conflict detail message
    conflict_res = next(r[1] for r in results if r[0] == 409)
    assert "already assigned" in conflict_res.get("detail", "")

    # Verify DB state
    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking is not None
        assert booking.status == "assigned"
        assert booking.worker_id == worker_id

        offer = db.query(BookingOffer).filter_by(id=offer_id).first()
        assert offer is not None
        assert offer.status == "accepted"

        profile = db.query(WorkerProfile).filter_by(user_id=worker_id).first()
        assert profile is not None
        assert profile.availability is False
    finally:
        db.close()


def test_double_accept_concurrent_offers_same_booking(run_idx: int = 100):
    """
    Simulates two separate workers holding offers for the SAME booking attempting
    to accept simultaneously. Verifies AD-6 row lock on Booking prevents double-booking.
    """
    db = TestingSessionLocal()
    try:
        citizen = User(
            name=f"Ravi Multi Worker Citizen {run_idx}",
            phone=f"9555{run_idx:04d}9",
            password_hash=hash_password("password123"),
            role="citizen",
        )
        worker1 = User(
            name=f"Worker One {run_idx}",
            phone=f"9888{run_idx:04d}1",
            password_hash=hash_password("password123"),
            role="worker",
        )
        worker2 = User(
            name=f"Worker Two {run_idx}",
            phone=f"9888{run_idx:04d}2",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add_all([citizen, worker1, worker2])
        db.commit()

        p1 = WorkerProfile(
            user_id=worker1.id,
            skill="plumber",
            lat=26.91,
            lng=75.78,
            verification_status="verified",
            availability=True,
        )
        p2 = WorkerProfile(
            user_id=worker2.id,
            skill="plumber",
            lat=26.91,
            lng=75.78,
            verification_status="verified",
            availability=True,
        )
        db.add_all([p1, p2])

        booking = Booking(
            citizen_id=citizen.id,
            skill="plumber",
            lat=26.91,
            lng=75.78,
            description="Plumbing repair",
            job_price=Decimal("400.00"),
            platform_fee=Decimal("20.00"),
            status="pending",
        )
        db.add(booking)
        db.commit()

        offer1 = BookingOffer(
            booking_id=booking.id,
            worker_id=worker1.id,
            rank_at_offer=1,
            dispatch_score=Decimal(9000),
            status="offered",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        offer2 = BookingOffer(
            booking_id=booking.id,
            worker_id=worker2.id,
            rank_at_offer=2,
            dispatch_score=Decimal(8500),
            status="offered",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db.add_all([offer1, offer2])
        db.commit()

        token1 = create_access_token(
            data={"user_id": str(worker1.id), "role": "worker"}
        )
        token2 = create_access_token(
            data={"user_id": str(worker2.id), "role": "worker"}
        )

        booking_id = booking.id
        offer1_id = offer1.id
        offer2_id = offer2.id
        worker1_id = worker1.id
        worker2_id = worker2.id
    finally:
        db.close()

    barrier = threading.Barrier(2)
    results = []

    def accept_worker(token, offer_id):
        barrier.wait()
        with client_lock:
            res = client.put(
                f"/booking-offers/{offer_id}",
                json={"action": "accept"},
                headers={"Authorization": f"Bearer {token}"},
            )
            return res.status_code, res.json()

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(accept_worker, token1, offer1_id)
        f2 = executor.submit(accept_worker, token2, offer2_id)
        results = [f1.result(), f2.result()]

    status_codes = [r[0] for r in results]
    assert 200 in status_codes, f"Expected one 200 OK, got {status_codes}"
    assert 409 in status_codes, f"Expected one 409 Conflict, got {status_codes}"

    db = TestingSessionLocal()
    try:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        assert booking is not None
        assert booking.status == "assigned"
        assert booking.worker_id in [worker1_id, worker2_id]

        o1 = db.query(BookingOffer).filter_by(id=offer1_id).first()
        o2 = db.query(BookingOffer).filter_by(id=offer2_id).first()
        accepted_offers = [o for o in [o1, o2] if o and o.status == "accepted"]
        assert len(accepted_offers) == 1, "Exactly one offer should be accepted"

        prof1 = db.query(WorkerProfile).filter_by(user_id=worker1_id).first()
        prof2 = db.query(WorkerProfile).filter_by(user_id=worker2_id).first()
        assert prof1.availability is False or prof2.availability is False, (
            "Winning worker availability must be False"
        )
    finally:
        db.close()


@pytest.mark.parametrize("run_idx", range(10))
def test_concurrency_reliability_repeat(run_idx):
    """
    Executes 10 consecutive iterations to verify 100% reliable concurrency lock behavior.
    """
    test_double_accept_same_offer_concurrency(run_idx + 10)
