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
from app.services.dispatch import compute_weekly_earnings, compute_reliability_penalty, get_ranked_workers
from conftest import TestingSessionLocal


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


from app.models.worker_profile import WorkerProfile


def test_get_ranked_workers_milestone_gate_success():
    db = TestingSessionLocal()
    try:
        # Seed 2 Citizens
        ravi = User(name="Ravi Sharma", phone="9555555555", password_hash="hash", role="citizen")
        priya_customer = User(name="Priya Customer", phone="9666666666", password_hash="hash", role="citizen")
        db.add_all([ravi, priya_customer])
        db.flush()

        # Seed 4 Workers
        # Suresh Kumar (Expected Rank: 1st)
        suresh_u = User(name="Suresh Kumar", phone="9111111111", password_hash="hash", role="worker")
        db.add(suresh_u)
        db.flush()
        suresh_p = WorkerProfile(
            user_id=suresh_u.id, skill="electrician", lat=Decimal("26.9280"), lng=Decimal("75.8100"),
            rating=Decimal("4.2"), availability=True, verified=True
        )
        db.add(suresh_p)

        # Priya Gupta (Expected Rank: 2nd)
        priya_u = User(name="Priya Gupta", phone="9222222222", password_hash="hash", role="worker")
        db.add(priya_u)
        db.flush()
        priya_p = WorkerProfile(
            user_id=priya_u.id, skill="electrician", lat=Decimal("26.8800"), lng=Decimal("75.7600"),
            rating=None, availability=True, verified=True
        )
        db.add(priya_p)

        # Anil Yadav (Expected Rank: 3rd)
        anil_u = User(name="Anil Yadav", phone="9333333333", password_hash="hash", role="worker")
        db.add(anil_u)
        db.flush()
        anil_p = WorkerProfile(
            user_id=anil_u.id, skill="electrician", lat=Decimal("26.9200"), lng=Decimal("75.8000"),
            rating=Decimal("4.5"), availability=True, verified=True
        )
        db.add(anil_p)

        # Meena Verma (Expected Rank: 4th)
        meena_u = User(name="Meena Verma", phone="9444444444", password_hash="hash", role="worker")
        db.add(meena_u)
        db.flush()
        meena_p = WorkerProfile(
            user_id=meena_u.id, skill="electrician", lat=Decimal("26.9130"), lng=Decimal("75.7880"),
            rating=Decimal("4.9"), availability=True, verified=True
        )
        db.add(meena_p)
        db.flush()

        # Seed Bookings for earnings
        # Suresh: ₹200 earnings -> job_price = 210.53
        b_suresh = Booking(
            citizen_id=ravi.id, worker_id=suresh_u.id, skill="electrician",
            lat=Decimal("26.9280"), lng=Decimal("75.8100"), job_price=Decimal("210.53"), status="completed"
        )
        # Anil: ₹2,000 earnings -> job_price = 2105.26
        b_anil = Booking(
            citizen_id=ravi.id, worker_id=anil_u.id, skill="electrician",
            lat=Decimal("26.9200"), lng=Decimal("75.8000"), job_price=Decimal("2105.26"), status="completed"
        )
        # Meena: ₹4,500 earnings -> job_price = 4736.84
        b_meena = Booking(
            citizen_id=priya_customer.id, worker_id=meena_u.id, skill="electrician",
            lat=Decimal("26.9130"), lng=Decimal("75.7880"), job_price=Decimal("4736.84"), status="completed"
        )
        db.add_all([b_suresh, b_anil, b_meena])
        db.commit()

        # Call get_ranked_workers at Jaipur center
        workers = get_ranked_workers("electrician", 26.9124, 75.7873, db)
        
        # Verify exactly 4 workers returned
        assert len(workers) == 4
        
        # Verify rank order Suresh Kumar > Priya Gupta > Anil Yadav > Meena Verma
        assert workers[0]["name"] == "Suresh Kumar"
        assert workers[1]["name"] == "Priya Gupta"
        assert workers[2]["name"] == "Anil Yadav"
        assert workers[3]["name"] == "Meena Verma"

        # Verify rating_is_default flag
        assert workers[0]["rating_is_default"] is False
        assert workers[1]["rating_is_default"] is True
        
        # Verify scores are correct
        # Suresh Kumar: ~12400-12550
        assert 12000 < float(workers[0]["dispatch_score"]) < 12600
        # Priya Gupta: ~11700-12000
        assert 11500 < float(workers[1]["dispatch_score"]) < 12100
        # Anil Yadav: ~9700-9800
        assert 9500 < float(workers[2]["dispatch_score"]) < 10000
        # Meena Verma: ~5700-5900
        assert 5500 < float(workers[3]["dispatch_score"]) < 6000
    finally:
        db.close()


def test_get_ranked_workers_excludes_unverified_and_unavailable():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        db.add(citizen)
        db.flush()

        # Worker 1: unverified
        w1_u = User(name="Unverified Worker", phone="9111111111", password_hash="hash", role="worker")
        db.add(w1_u)
        db.flush()
        w1_p = WorkerProfile(
            user_id=w1_u.id, skill="electrician", lat=Decimal("26.9280"), lng=Decimal("75.8100"),
            rating=Decimal("4.2"), availability=True, verified=False
        )
        db.add(w1_p)

        # Worker 2: unavailable
        w2_u = User(name="Unavailable Worker", phone="9222222222", password_hash="hash", role="worker")
        db.add(w2_u)
        db.flush()
        w2_p = WorkerProfile(
            user_id=w2_u.id, skill="electrician", lat=Decimal("26.9280"), lng=Decimal("75.8100"),
            rating=Decimal("4.2"), availability=False, verified=True
        )
        db.add(w2_p)

        # Worker 3: verified & available (should be returned)
        w3_u = User(name="Valid Worker", phone="9333333333", password_hash="hash", role="worker")
        db.add(w3_u)
        db.flush()
        w3_p = WorkerProfile(
            user_id=w3_u.id, skill="electrician", lat=Decimal("26.9280"), lng=Decimal("75.8100"),
            rating=Decimal("4.2"), availability=True, verified=True
        )
        db.add(w3_p)
        db.commit()

        workers = get_ranked_workers("electrician", 26.9124, 75.7873, db)
        assert len(workers) == 1
        assert workers[0]["name"] == "Valid Worker"
    finally:
        db.close()


def test_get_ranked_workers_excludes_out_of_radius():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        db.add(citizen)
        db.flush()

        # Worker far away (> 5km away, e.g. ~10km away)
        w1_u = User(name="Far Away Worker", phone="9111111111", password_hash="hash", role="worker")
        db.add(w1_u)
        db.flush()
        w1_p = WorkerProfile(
            user_id=w1_u.id, skill="electrician", lat=Decimal("27.0000"), lng=Decimal("75.8500"),
            rating=Decimal("4.2"), availability=True, verified=True
        )
        db.add(w1_p)
        db.commit()

        workers = get_ranked_workers("electrician", 26.9124, 75.7873, db)
        assert len(workers) == 0
    finally:
        db.close()


def test_get_ranked_workers_reliability_penalty_applied():
    db = TestingSessionLocal()
    try:
        citizen = User(name="Ravi", phone="9555555555", password_hash="hash", role="citizen")
        db.add(citizen)
        db.flush()

        # Worker A (Reliable)
        wA_u = User(name="Reliable Worker", phone="9111111111", password_hash="hash", role="worker")
        db.add(wA_u)
        db.flush()
        wA_p = WorkerProfile(
            user_id=wA_u.id, skill="electrician", lat=Decimal("26.9280"), lng=Decimal("75.8100"),
            rating=Decimal("4.0"), availability=True, verified=True
        )
        db.add(wA_p)

        # Worker B (Unreliable - gets penalty)
        wB_u = User(name="Unreliable Worker", phone="9222222222", password_hash="hash", role="worker")
        db.add(wB_u)
        db.flush()
        wB_p = WorkerProfile(
            user_id=wB_u.id, skill="electrician", lat=Decimal("26.9280"), lng=Decimal("75.8100"),
            rating=Decimal("4.0"), availability=True, verified=True
        )
        db.add(wB_p)
        db.flush()

        # Seed booking to attach offers to
        booking = Booking(
            citizen_id=citizen.id,
            skill="electrician",
            lat=Decimal("26.9280"),
            lng=Decimal("75.8100"),
            job_price=Decimal("500.00"),
            status="pending",
        )
        db.add(booking)
        db.flush()

        # Seed 5 offers for Worker B, all declined (0% acceptance rate -> penalty applied)
        for i in range(5):
            offer = BookingOffer(
                booking_id=booking.id,
                worker_id=wB_u.id,
                rank_at_offer=1,
                dispatch_score=Decimal("1000.00"),
                status="declined",
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                created_at=datetime.now(timezone.utc) - timedelta(minutes=i)
            )
            db.add(offer)

        db.commit()

        # Get ranked workers
        workers = get_ranked_workers("electrician", 26.9280, 75.8100, db)

        # Both should be present since they are at the center (0 distance) and verified/available
        assert len(workers) == 2

        # Worker A should be 1st, Worker B should be 2nd
        assert workers[0]["name"] == "Reliable Worker"
        assert workers[1]["name"] == "Unreliable Worker"

        # Verify score difference is exactly 3000
        score_A = float(workers[0]["dispatch_score"])
        score_B = float(workers[1]["dispatch_score"])
        assert abs(score_A - score_B - 3000.0) < 0.01

        # Verify flags
        assert workers[0]["reliability_penalty_applied"] is False
        assert workers[1]["reliability_penalty_applied"] is True

    finally:
        db.close()



