"""Unit and integration tests for the Fair-Surge pricing engine."""

import uuid
from decimal import Decimal

import pytest
from conftest import TestingSessionLocal

from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.schemas.pricing import PricingContext
from app.services.pricing import BASE_RATES, _time_multiplier, compute_fair_surge_price

# ── helpers ──────────────────────────────────────────────────────────────────


def _add_worker(db, skill: str, lat: float, lng: float, phone_suffix: str = ""):
    """Insert a verified, available worker and return its user_id."""
    user = User(
        name="Test Worker",
        phone=f"91111{phone_suffix or str(uuid.uuid4().int)[:10]}",
        password_hash="fakehash",
        role="worker",
    )
    db.add(user)
    db.flush()  # get user.id

    profile = WorkerProfile(
        user_id=user.id,
        skill=skill,
        lat=lat,
        lng=lng,
        verification_status="verified",
        availability=True,
    )
    db.add(profile)
    db.commit()
    return user.id


def _add_booking(db, skill: str, lat: float, lng: float, status: str = "pending"):
    """Insert a booking row and return its id."""
    citizen = User(
        name="Test Citizen",
        phone=f"92222{str(uuid.uuid4().int)[:10]}",
        password_hash="fakehash",
        role="citizen",
    )
    db.add(citizen)
    db.flush()

    bk = Booking(
        citizen_id=citizen.id,
        skill=skill,
        lat=lat,
        lng=lng,
        job_price=Decimal(500),
        status=status,
    )
    db.add(bk)
    db.commit()
    return bk.id


# Centre of Jaipur (used as the pricing request location throughout)
_LAT = 26.9124
_LNG = 75.7873


# ── time-multiplier unit tests (pure logic, no DB) ───────────────────────────


def test_time_multiplier_day():
    assert _time_multiplier(12) == Decimal("1.0")


def test_time_multiplier_boundary_day_start():
    assert _time_multiplier(6) == Decimal("1.0")


def test_time_multiplier_boundary_day_end():
    # Hour 20 switches to evening
    assert _time_multiplier(20) == Decimal("1.15")


def test_time_multiplier_evening():
    assert _time_multiplier(21) == Decimal("1.15")


def test_time_multiplier_night_late():
    assert _time_multiplier(23) == Decimal("1.25")


def test_time_multiplier_night_early():
    assert _time_multiplier(3) == Decimal("1.25")


# ── skill validation ──────────────────────────────────────────────────────────


def test_unknown_skill_raises():
    db = TestingSessionLocal()
    try:
        ctx = PricingContext(
            skill="juggler",
            lat=_LAT,
            lng=_LNG,
            urgency="normal",
            hour_of_day=12,
        )
        with pytest.raises(ValueError, match="Unknown skill"):
            compute_fair_surge_price(ctx, db)
    finally:
        db.close()


# ── zero supply → price must be P_max ────────────────────────────────────────


def test_zero_supply_returns_p_max():
    """With no workers in radius the S-multiplier is clamped to 1.5 → final_price = P_max."""
    db = TestingSessionLocal()
    try:
        # No workers seeded — S = 0
        ctx = PricingContext(
            skill="electrician",
            lat=_LAT,
            lng=_LNG,
            urgency="normal",
            hour_of_day=12,
        )
        result = compute_fair_surge_price(ctx, db)
        expected_max = (BASE_RATES["electrician"] * Decimal("1.50")).quantize(Decimal("1.00"))
        assert result.final_price == expected_max  # ₹750.00
    finally:
        db.close()


# ── extreme demand spike → price still capped at P_max ───────────────────────


def test_extreme_demand_spike_capped_at_p_max():
    """D=10, S=1 → S_multiplier > 1.5, must be clamped to 1.5."""
    db = TestingSessionLocal()
    try:
        _add_worker(db, "electrician", _LAT, _LNG, phone_suffix="10001")
        for i in range(10):
            _add_booking(db, "electrician", _LAT, _LNG)

        ctx = PricingContext(
            skill="electrician",
            lat=_LAT,
            lng=_LNG,
            urgency="normal",
            hour_of_day=12,
        )
        result = compute_fair_surge_price(ctx, db)
        expected_max = (BASE_RATES["electrician"] * Decimal("1.50")).quantize(Decimal("1.00"))
        assert result.final_price == expected_max
    finally:
        db.close()


# ── balanced supply/demand → no surge ────────────────────────────────────────


def test_balanced_supply_demand_no_surge():
    """D=S → ratio=1 → S_multiplier=1.0 → final_price = base."""
    db = TestingSessionLocal()
    try:
        _add_worker(db, "electrician", _LAT, _LNG, phone_suffix="20001")
        _add_booking(db, "electrician", _LAT, _LNG)

        ctx = PricingContext(
            skill="electrician",
            lat=_LAT,
            lng=_LNG,
            urgency="normal",
            hour_of_day=12,
        )
        result = compute_fair_surge_price(ctx, db)
        assert result.final_price == BASE_RATES["electrician"].quantize(Decimal("1.00"))
    finally:
        db.close()


# ── oversupply → price at P_min ──────────────────────────────────────────────


def test_oversupply_price_floored_at_p_min():
    """D=1, S=10 → ratio=0.1 → S_multiplier=1.0 (no surge, D<S) → base → but P_min = 0.90*base.
    S_multiplier formula: 1 + 0.4*max(0, ratio-1). With ratio<1, max(0, …)=0 → mult=1.
    So final = base = 500 which is above P_min=450. Assert final == base."""
    db = TestingSessionLocal()
    try:
        for i in range(10):
            _add_worker(db, "electrician", _LAT, _LNG, phone_suffix=f"3000{i}")
        _add_booking(db, "electrician", _LAT, _LNG)

        ctx = PricingContext(
            skill="electrician",
            lat=_LAT,
            lng=_LNG,
            urgency="normal",
            hour_of_day=12,
        )
        result = compute_fair_surge_price(ctx, db)
        # No surge when D < S; price stays at base
        assert result.final_price == BASE_RATES["electrician"].quantize(Decimal("1.00"))
    finally:
        db.close()


# ── urgency multiplier applied correctly ──────────────────────────────────────


def test_urgency_emergency_multiplier():
    """With 1 worker, 1 booking (balanced → S_mult=1), emergency → price = base*1.35."""
    db = TestingSessionLocal()
    try:
        _add_worker(db, "plumber", _LAT, _LNG, phone_suffix="40001")
        _add_booking(db, "plumber", _LAT, _LNG)

        ctx = PricingContext(
            skill="plumber",
            lat=_LAT,
            lng=_LNG,
            urgency="emergency",
            hour_of_day=12,
        )
        result = compute_fair_surge_price(ctx, db)
        base = BASE_RATES["plumber"]
        expected = (base * Decimal("1.35")).quantize(Decimal("1.00"))
        p_max = (base * Decimal("1.50")).quantize(Decimal("1.00"))
        assert result.final_price == min(expected, p_max)
    finally:
        db.close()


# ── payout distribution sanity ────────────────────────────────────────────────


def test_worker_payout_is_at_least_95_percent_of_base():
    """Worker must always receive at least base*0.95 regardless of surge level."""
    db = TestingSessionLocal()
    try:
        _add_worker(db, "electrician", _LAT, _LNG, phone_suffix="50001")
        _add_booking(db, "electrician", _LAT, _LNG)

        ctx = PricingContext(
            skill="electrician",
            lat=_LAT,
            lng=_LNG,
            urgency="urgent",
            hour_of_day=12,
        )
        result = compute_fair_surge_price(ctx, db)
        min_payout = (BASE_RATES["electrician"] * Decimal("0.95")).quantize(Decimal("1.00"))
        assert result.worker_payout >= min_payout
    finally:
        db.close()


def test_fee_plus_welfare_plus_payout_equals_final_price():
    """Conservation: worker_payout + platform_fee + welfare_fund == final_price (to ₹1 rounding)."""
    db = TestingSessionLocal()
    try:
        _add_worker(db, "electrician", _LAT, _LNG, phone_suffix="60001")
        for _ in range(3):
            _add_booking(db, "electrician", _LAT, _LNG)

        ctx = PricingContext(
            skill="electrician",
            lat=_LAT,
            lng=_LNG,
            urgency="urgent",
            hour_of_day=21,
        )
        result = compute_fair_surge_price(ctx, db)
        total = result.worker_payout + result.platform_fee + result.welfare_fund
        # Allow ±₹1 due to individual quantize rounding
        assert abs(total - result.final_price) <= Decimal("1.00")
    finally:
        db.close()


# ── workers outside 5km radius are excluded ───────────────────────────────────


def test_workers_outside_radius_not_counted():
    """Workers > 5 km away must not count as supply → zero supply → P_max."""
    db = TestingSessionLocal()
    try:
        # Delhi coordinates — ~260 km from Jaipur
        _add_worker(db, "electrician", 28.6139, 77.2090, phone_suffix="70001")

        ctx = PricingContext(
            skill="electrician",
            lat=_LAT,
            lng=_LNG,
            urgency="normal",
            hour_of_day=12,
        )
        result = compute_fair_surge_price(ctx, db)
        expected_max = (BASE_RATES["electrician"] * Decimal("1.50")).quantize(Decimal("1.00"))
        assert result.final_price == expected_max
    finally:
        db.close()


# ── multipliers dict is present ───────────────────────────────────────────────


def test_result_contains_multipliers():
    db = TestingSessionLocal()
    try:
        ctx = PricingContext(
            skill="cleaner",
            lat=_LAT,
            lng=_LNG,
            urgency="normal",
            hour_of_day=10,
        )
        result = compute_fair_surge_price(ctx, db)
        assert "s_multiplier" in result.multipliers_applied
        assert "u_multiplier" in result.multipliers_applied
        assert "t_multiplier" in result.multipliers_applied
    finally:
        db.close()
