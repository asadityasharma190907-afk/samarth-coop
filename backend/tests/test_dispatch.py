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
from app.services.dispatch import compute_weekly_earnings

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
