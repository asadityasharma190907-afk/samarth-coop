from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.booking_offer import BookingOffer


def compute_weekly_earnings(worker_id: UUID, db: Session) -> Decimal:
    """
    Calculates how much a worker earned this week from completed bookings.
    Uses date_trunc('week', NOW()) on PostgreSQL, with a Python-computed timezone-aware fallback for SQLite.
    """
    dialect_name = db.bind.dialect.name

    if dialect_name == "sqlite":
        # Calculate Monday of the current week at 00:00:00 UTC
        now = datetime.now(timezone.utc)
        days_to_subtract = now.weekday()  # Monday is 0, Sunday is 6
        week_start = (now - timedelta(days=days_to_subtract)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        query = db.query(func.coalesce(func.sum(Booking.job_price * 0.95), 0)).filter(
            Booking.worker_id == worker_id,
            Booking.status == "completed",
            Booking.created_at >= week_start,
        )
    else:
        # PostgreSQL native date_trunc
        query = db.query(func.coalesce(func.sum(Booking.job_price * 0.95), 0)).filter(
            Booking.worker_id == worker_id,
            Booking.status == "completed",
            Booking.created_at >= func.date_trunc("week", func.now()),
        )

    result = query.scalar()
    if result is None:
        return Decimal(0)

    # Convert result to Decimal to ensure type consistency
    return Decimal(str(result))


def compute_reliability_penalty(worker_id: UUID, db: Session) -> bool:
    """
    Checks if a worker should be penalized for declining/ignoring too many offers.
    Returns True if worker has >= 5 total offers AND acceptance rate in last 10 is < 50%.
    Returns False otherwise.
    """
    recent = (
        db.query(BookingOffer)
        .filter(BookingOffer.worker_id == worker_id)
        .order_by(BookingOffer.created_at.desc())
        .limit(10)
        .all()
    )

    if len(recent) < 5:
        return False  # Grace period

    accepted = sum(1 for o in recent if o.status == "accepted")

    # Check if acceptance rate is strictly less than 50%
    return (accepted / len(recent)) < 0.5


# Math imports for haversine
from math import atan2, cos, radians, sin, sqrt

from app.models.user import User
from app.models.worker_profile import WorkerProfile


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    )
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def compute_dispatch_score(
    weekly_earnings: Decimal,
    rating: float | None,
    distance_km: float,
    reliability_penalty: bool,
) -> Decimal:
    effective_rating = Decimal(str(rating)) if rating is not None else Decimal("4.0")
    penalty = Decimal(3000) if reliability_penalty else Decimal(0)
    return (
        (Decimal(5000) - weekly_earnings) * 2
        + Decimal(1000) * effective_rating
        - Decimal(500) * Decimal(str(distance_km))
        - penalty
    )


def get_ranked_workers(skill: str, lat: float, lng: float, db: Session) -> list[dict]:
    # Query worker profiles with user detail
    profiles = (
        db.query(WorkerProfile, User)
        .join(User, WorkerProfile.user_id == User.id)
        .filter(
            WorkerProfile.skill == skill,
            WorkerProfile.verified == True,
            WorkerProfile.availability == True,
        )
        .all()
    )

    ranked = []
    for profile, user in profiles:
        distance_km = haversine_km(lat, lng, float(profile.lat), float(profile.lng))
        if distance_km > 5.0:
            continue

        weekly_earnings = compute_weekly_earnings(profile.user_id, db)
        reliability_penalty = compute_reliability_penalty(profile.user_id, db)

        rating_val = float(profile.rating) if profile.rating is not None else None

        dispatch_score = compute_dispatch_score(
            weekly_earnings=weekly_earnings,
            rating=rating_val,
            distance_km=distance_km,
            reliability_penalty=reliability_penalty,
        )

        ranked.append(
            {
                "worker_id": profile.user_id,
                "name": user.name,
                "phone": user.phone,
                "skill": profile.skill,
                "lat": profile.lat,
                "lng": profile.lng,
                "rating": profile.rating,
                "distance_km": distance_km,
                "weekly_earnings": weekly_earnings,
                "dispatch_score": dispatch_score,
                "rating_is_default": profile.rating is None,
                "reliability_penalty_applied": reliability_penalty,
            }
        )

    # Sort by dispatch_score desc
    ranked.sort(key=lambda x: x["dispatch_score"], reverse=True)
    return ranked
