from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.worker_profile import WorkerProfile


def get_earnings_distribution(db: Session):
    dialect_name = db.bind.dialect.name

    if dialect_name == "sqlite":
        # Calculate Monday of the current week at 00:00:00 UTC
        now = datetime.now(timezone.utc)
        days_to_subtract = now.weekday()  # Monday is 0, Sunday is 6
        week_start = (now - timedelta(days=days_to_subtract)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        # PostgreSQL native date_trunc
        week_start = func.date_trunc("week", func.now())

    # Query all active/verified workers and their total earnings from completed bookings this week
    earnings_query = (
        db.query(
            WorkerProfile.user_id,
            func.coalesce(func.sum(Booking.job_price * 0.95), 0).label("earnings"),
        )
        .outerjoin(
            Booking,
            (Booking.worker_id == WorkerProfile.user_id)
            & (Booking.status == "completed")
            & (Booking.created_at >= week_start),
        )
        .group_by(WorkerProfile.user_id)
        .all()
    )

    buckets = [
        {"range_label": "₹0 - ₹500", "min_val": 0, "max_val": 500, "worker_count": 0},
        {
            "range_label": "₹501 - ₹1500",
            "min_val": 501,
            "max_val": 1500,
            "worker_count": 0,
        },
        {
            "range_label": "₹1501 - ₹3000",
            "min_val": 1501,
            "max_val": 3000,
            "worker_count": 0,
        },
        {"range_label": "₹3001+", "min_val": 3001, "max_val": None, "worker_count": 0},
    ]

    for row in earnings_query:
        earnings = float(row.earnings)
        if earnings <= 500:
            buckets[0]["worker_count"] += 1
        elif earnings <= 1500:
            buckets[1]["worker_count"] += 1
        elif earnings <= 3000:
            buckets[2]["worker_count"] += 1
        else:
            buckets[3]["worker_count"] += 1

    return {"currency": "INR", "total_workers": len(earnings_query), "buckets": buckets}
