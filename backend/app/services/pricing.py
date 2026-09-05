from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.worker_profile import WorkerProfile
from app.schemas.pricing import PricingContext, PricingResult
from app.services.dispatch import haversine_km

# Base rates per skill (₹)
BASE_RATES = {
    "electrician": Decimal(500),
    "plumber": Decimal(450),
    "carpenter": Decimal(500),
    "painter": Decimal(400),
    "cleaner": Decimal(350),
    "ac_mechanic": Decimal(600),
    "welder": Decimal(550),
    "mason": Decimal(450),
    "gardener": Decimal(300),
    "pest_control": Decimal(550),
}

URGENCY_MULTIPLIERS = {
    "normal": Decimal("1.0"),
    "urgent": Decimal("1.20"),
    "emergency": Decimal("1.35"),
}

TIME_MULTIPLIERS = {
    "day": Decimal("1.0"),  # 06:00-20:00
    "evening": Decimal("1.15"),  # 20:00-23:00
    "night": Decimal("1.25"),  # 23:00-06:00
}


def _time_multiplier(hour: int) -> Decimal:
    if 6 <= hour < 20:
        return TIME_MULTIPLIERS["day"]
    if 20 <= hour < 23:
        return TIME_MULTIPLIERS["evening"]
    return TIME_MULTIPLIERS["night"]


def compute_fair_surge_price(ctx: PricingContext, db: Session) -> PricingResult:
    # Validate skill
    if ctx.skill not in BASE_RATES:
        raise ValueError(f"Unknown skill: {ctx.skill}")

    base_price = BASE_RATES[ctx.skill]

    # Supply: verified, available workers within 5km
    workers = (
        db.query(WorkerProfile)
        .filter(
            WorkerProfile.skill == ctx.skill,
            WorkerProfile.verification_status == "verified",
            WorkerProfile.availability.is_(True),
        )
        .all()
    )
    supply = sum(
        1
        for wp in workers
        if haversine_km(ctx.lat, ctx.lng, float(wp.lat), float(wp.lng)) <= 5.0
    )

    # Demand: pending/assigned bookings within 5km
    bookings = (
        db.query(Booking)
        .filter(
            Booking.skill == ctx.skill,
            Booking.status.in_(["pending", "accepted", "assigned"]),
        )
        .all()
    )
    demand = sum(
        1
        for bk in bookings
        if haversine_km(ctx.lat, ctx.lng, float(bk.lat), float(bk.lng)) <= 5.0
    )

    # Supply multiplier
    if supply == 0:
        s_multiplier = Decimal("1.5")
    else:
        ratio = Decimal(demand) / Decimal(supply)
        s_multiplier = Decimal(1) + Decimal("0.4") * max(Decimal(0), ratio - Decimal(1))
        s_multiplier = min(max(s_multiplier, Decimal("0.85")), Decimal("1.50"))

    u_multiplier = URGENCY_MULTIPLIERS[ctx.urgency]
    t_multiplier = _time_multiplier(ctx.hour_of_day)

    raw_price = base_price * s_multiplier * u_multiplier * t_multiplier

    p_min = (base_price * Decimal("0.90")).quantize(Decimal("1.00"))
    p_max = (base_price * Decimal("1.50")).quantize(Decimal("1.00"))
    final_price = raw_price.quantize(Decimal("1.00"))
    final_price = max(final_price, p_min)
    final_price = min(final_price, p_max)

    surplus = final_price - base_price
    platform_fee = (base_price * Decimal("0.05")).quantize(Decimal("1.00"))
    worker_base = (base_price * Decimal("0.95")).quantize(Decimal("1.00"))
    extra_worker = (surplus * Decimal("0.70")).quantize(Decimal("1.00"))
    welfare_fund = (surplus * Decimal("0.20")).quantize(Decimal("1.00"))
    platform_reserve = (surplus * Decimal("0.10")).quantize(Decimal("1.00"))
    worker_payout = worker_base + extra_worker
    platform_fee = platform_fee + platform_reserve

    multipliers = {
        "s_multiplier": float(s_multiplier),
        "u_multiplier": float(u_multiplier),
        "t_multiplier": float(t_multiplier),
    }

    return PricingResult(
        base_price=base_price,
        final_price=final_price,
        worker_payout=worker_payout,
        platform_fee=platform_fee,
        welfare_fund=welfare_fund,
        multipliers_applied=multipliers,
    )
