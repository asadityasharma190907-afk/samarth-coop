import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.user import User
from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.services.dispatch import compute_weekly_earnings, compute_reliability_penalty

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_compute_weekly_earnings_no_bookings():
    db = TestingSessionLocal()
    try:
        worker_id = uuid4()
        earnings = compute_weekly_earnings(worker_id, db)
        assert earnings == Decimal("0")
    finally:
        db.close()


def test_compute_weekly_earnings_completed_bookings():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        worker = User(name="Suresh", phone="9111111111", password_hash="hash", role="worker")
        db.add_all([citizen, worker])
        db.flush()

        # Seed completed booking in current week
        b1 = Booking(
            citizen_id=citizen.id,
            worker_id=worker.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("210.53"),
            status="completed",
            created_at=datetime.now(timezone.utc)
        )
        db.add(b1)
        db.commit()

        earnings = compute_weekly_earnings(worker.id, db)
        # Expected payout = 210.53 * 0.95 = 200.0035 (database Numeric scale might round it)
        assert abs(earnings - Decimal("200.00")) < Decimal("0.05")
    finally:
        db.close()


def test_compute_weekly_earnings_ignores_non_completed():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        worker = User(name="Suresh", phone="9111111111", password_hash="hash", role="worker")
        db.add_all([citizen, worker])
        db.flush()

        b_pending = Booking(
            citizen_id=citizen.id,
            worker_id=worker.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("100.00"),
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        b_cancelled = Booking(
            citizen_id=citizen.id,
            worker_id=worker.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("500.00"),
            status="cancelled",
            created_at=datetime.now(timezone.utc)
        )
        db.add_all([b_pending, b_cancelled])
        db.commit()

        earnings = compute_weekly_earnings(worker.id, db)
        assert earnings == Decimal("0")
    finally:
        db.close()


def test_compute_weekly_earnings_ignores_previous_weeks():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        worker = User(name="Suresh", phone="9111111111", password_hash="hash", role="worker")
        db.add_all([citizen, worker])
        db.flush()

        # Completed booking 10 days ago (definitely previous ISO week)
        old_time = datetime.now(timezone.utc) - timedelta(days=10)
        b_old = Booking(
            citizen_id=citizen.id,
            worker_id=worker.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("1000.00"),
            status="completed",
            created_at=old_time
        )
        db.add(b_old)
        db.commit()

        earnings = compute_weekly_earnings(worker.id, db)
        assert earnings == Decimal("0")
    finally:
        db.close()


def test_reliability_penalty_grace_period():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        worker = User(name="Suresh", phone="9111111111", password_hash="hash", role="worker")
        db.add_all([citizen, worker])
        db.flush()

        booking = Booking(
            citizen_id=citizen.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("500.00"),
            status="pending",
        )
        db.add(booking)
        db.flush()

        # Less than 5 offers total (grace period)
        for i in range(4):
            offer = BookingOffer(
                booking_id=booking.id,
                worker_id=worker.id,
                rank_at_offer=1,
                dispatch_score=Decimal("1000.00"),
                status="declined",
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                created_at=datetime.now(timezone.utc) - timedelta(minutes=i)
            )
            db.add(offer)
        db.commit()

        penalty = compute_reliability_penalty(worker.id, db)
        assert penalty is False
    finally:
        db.close()


def test_reliability_penalty_applied():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        worker = User(name="Suresh", phone="9111111111", password_hash="hash", role="worker")
        db.add_all([citizen, worker])
        db.flush()

        booking = Booking(
            citizen_id=citizen.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("500.00"),
            status="pending",
        )
        db.add(booking)
        db.flush()

        # 6 offers, 2 accepted (acceptance rate = 33.3% < 50%) -> penalty should apply
        statuses = ["accepted", "accepted", "declined", "declined", "declined", "declined"]
        for i, status in enumerate(statuses):
            offer = BookingOffer(
                booking_id=booking.id,
                worker_id=worker.id,
                rank_at_offer=1,
                dispatch_score=Decimal("1000.00"),
                status=status,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                created_at=datetime.now(timezone.utc) - timedelta(minutes=i)
            )
            db.add(offer)
        db.commit()

        penalty = compute_reliability_penalty(worker.id, db)
        assert penalty is True
    finally:
        db.close()


def test_reliability_penalty_exactly_fifty_percent():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        worker = User(name="Suresh", phone="9111111111", password_hash="hash", role="worker")
        db.add_all([citizen, worker])
        db.flush()

        booking = Booking(
            citizen_id=citizen.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("500.00"),
            status="pending",
        )
        db.add(booking)
        db.flush()

        # 10 offers, 5 accepted (exactly 50%) -> no penalty
        statuses = ["accepted"] * 5 + ["declined"] * 5
        for i, status in enumerate(statuses):
            offer = BookingOffer(
                booking_id=booking.id,
                worker_id=worker.id,
                rank_at_offer=1,
                dispatch_score=Decimal("1000.00"),
                status=status,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                created_at=datetime.now(timezone.utc) - timedelta(minutes=i)
            )
            db.add(offer)
        db.commit()

        penalty = compute_reliability_penalty(worker.id, db)
        assert penalty is False
    finally:
        db.close()


def test_reliability_penalty_evaluates_only_last_ten():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        worker = User(name="Suresh", phone="9111111111", password_hash="hash", role="worker")
        db.add_all([citizen, worker])
        db.flush()

        booking = Booking(
            citizen_id=citizen.id,
            skill="electrician",
            lat=26.9280,
            lng=75.8100,
            job_price=Decimal("500.00"),
            status="pending",
        )
        db.add(booking)
        db.flush()

        # Total 12 offers.
        # Older 2 are accepted (not in last 10).
        # Last 10 has 4 accepted, 6 declined (acceptance rate = 40% < 50%) -> penalty applies
        # We insert from oldest to newest (newest has smaller created_at delta, i.e. created_at is closer to now).
        # So created_at = now - i minutes, where i goes from 11 down to 0.
        # i = 11: accepted (oldest, rank 12)
        # i = 10: accepted (old old, rank 11)
        # last 10 (i=9 to 0): 4 accepted, 6 declined
        statuses = [
            "accepted",  # i = 11
            "accepted",  # i = 10
            "accepted",  # i = 9 (in last 10)
            "accepted",  # i = 8 (in last 10)
            "accepted",  # i = 7 (in last 10)
            "accepted",  # i = 6 (in last 10)
            "declined",  # i = 5 (in last 10)
            "declined",  # i = 4 (in last 10)
            "declined",  # i = 3 (in last 10)
            "declined",  # i = 2 (in last 10)
            "declined",  # i = 1 (in last 10)
            "declined",  # i = 0 (newest, in last 10)
        ]
        # Reverse status order so list represents oldest to newest (since delta = 11 - idx minutes)
        # So status[0] gets delta = 11 minutes (oldest). status[11] gets delta = 0 minutes (newest).
        for i, status in enumerate(statuses):
            offer = BookingOffer(
                booking_id=booking.id,
                worker_id=worker.id,
                rank_at_offer=1,
                dispatch_score=Decimal("1000.00"),
                status=status,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                created_at=datetime.now(timezone.utc) - timedelta(minutes=(11 - i))
            )
            db.add(offer)
        db.commit()

        penalty = compute_reliability_penalty(worker.id, db)
        assert penalty is True
    finally:
        db.close()

