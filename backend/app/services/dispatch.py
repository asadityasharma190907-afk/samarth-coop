import os
import sys
from decimal import Decimal
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.booking import Booking


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

        query = db.query(
            func.coalesce(func.sum(Booking.job_price * 0.95), 0)
        ).filter(
            Booking.worker_id == worker_id,
            Booking.status == "completed",
            Booking.created_at >= week_start
        )
    else:
        # PostgreSQL native date_trunc
        query = db.query(
            func.coalesce(func.sum(Booking.job_price * 0.95), 0)
        ).filter(
            Booking.worker_id == worker_id,
            Booking.status == "completed",
            Booking.created_at >= func.date_trunc("week", func.now())
        )

    result = query.scalar()
    if result is None:
        return Decimal("0")
    
    # Convert result to Decimal to ensure type consistency
    return Decimal(str(result))
