import csv
import io
from datetime import datetime, timedelta, timezone
from typing import TypedDict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile


def get_earnings_distribution(db: Session):
    dialect_name = db.get_bind().dialect.name

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

    class Bucket(TypedDict):
        range_label: str
        min_val: int
        max_val: int | None
        worker_count: int

    buckets: list[Bucket] = [
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


def generate_weekly_earnings_csv(db: Session) -> str:
    dialect_name = db.get_bind().dialect.name
    if dialect_name == "sqlite":
        now = datetime.now(timezone.utc)
        days_to_subtract = now.weekday()
        week_start = (now - timedelta(days=days_to_subtract)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        week_start = func.date_trunc("week", func.now())

    # Query all workers and their total earnings from completed bookings this week
    query = (
        db.query(
            User.id,
            User.name,
            WorkerProfile.skill,
            WorkerProfile.rating,
            func.count(Booking.id).label("completed_jobs"),
            func.coalesce(func.sum(Booking.job_price * 0.95), 0).label("earnings"),
            func.coalesce(func.sum(Booking.platform_fee), 0).label("welfare_fund"),
        )
        .join(WorkerProfile, User.id == WorkerProfile.user_id)
        .outerjoin(
            Booking,
            (Booking.worker_id == User.id)
            & (Booking.status == "completed")
            & (Booking.created_at >= week_start),
        )
        .filter(User.role == "worker")
        .group_by(User.id, User.name, WorkerProfile.skill, WorkerProfile.rating)
        .order_by(User.name)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Worker ID",
            "Worker Name",
            "Skill",
            "Rating",
            "Completed Jobs This Week",
            "Weekly Earnings (INR)",
            "Welfare Fund Contributed (INR)",
        ]
    )

    for row in query:
        rating = float(row.rating) if row.rating is not None else 4.0
        writer.writerow(
            [
                str(row.id),
                row.name,
                row.skill,
                f"{rating:.1f}",
                row.completed_jobs,
                f"{float(row.earnings):.2f}",
                f"{float(row.welfare_fund):.2f}",
            ]
        )

    return output.getvalue()
