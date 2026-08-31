from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.booking import Booking
from app.models.user import User
from app.schemas.wallet import EarningsEntry, WalletResponse
from app.services.dispatch import compute_weekly_earnings

router = APIRouter()


@router.get("/{worker_id}", response_model=WalletResponse)
def get_worker_wallet(
    worker_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only workers have wallets"
        )
    if current_user.id != worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view another worker's wallet",
        )

    weekly_earnings = compute_weekly_earnings(worker_id, db)

    completed_bookings = (
        db.query(Booking)
        .filter(Booking.worker_id == worker_id, Booking.status == "completed")
        .order_by(Booking.created_at.desc())
        .all()
    )

    lifetime_earnings = Decimal("0.00")
    entries = []

    for b in completed_bookings:
        worker_payout = b.job_price - b.platform_fee
        lifetime_earnings += worker_payout

        entries.append(
            EarningsEntry(
                date=b.created_at.date(),
                skill=str(b.skill),
                job_price=b.job_price,
                worker_payout=worker_payout,
                platform_fee=b.platform_fee,
            )
        )

    return WalletResponse(
        weekly_earnings=weekly_earnings,
        lifetime_earnings=lifetime_earnings,
        entries=entries,
    )
