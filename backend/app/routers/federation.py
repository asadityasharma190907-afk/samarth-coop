from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.schemas.federation import (
    EarningsDistributionResponse,
    FederationBookingResponse,
    FederationStatsResponse,
)
from app.services.federation import get_earnings_distribution

router = APIRouter()


@router.get("/stats", response_model=FederationStatsResponse)
def get_federation_stats(db: Session = Depends(get_db)):
    registered_workers = (
        db.query(func.count(User.id)).filter(User.role == "worker").scalar() or 0
    )

    welfare_stats = (
        db.query(
            func.coalesce(func.sum(Booking.platform_fee), 0).label("total_fees"),
            func.count(Booking.id).label("completed_bookings"),
        )
        .filter(Booking.status == "completed")
        .first()
    )

    return FederationStatsResponse(
        registered_workers=registered_workers,
        completed_bookings=welfare_stats.completed_bookings if welfare_stats else 0,
        welfare_fund_total=welfare_stats.total_fees if welfare_stats else 0,
    )


@router.get("/bookings", response_model=list[FederationBookingResponse])
def get_federation_bookings(db: Session = Depends(get_db)):
    # Returns all bookings, descending by creation
    bookings = (
        db.query(Booking, User)
        .join(User, User.id == Booking.citizen_id)
        .order_by(Booking.created_at.desc())
        .limit(50)  # Just latest 50 for the dashboard
        .all()
    )

    result = []
    for booking, citizen in bookings:
        result.append(
            FederationBookingResponse(
                id=booking.id,  # type: ignore
                citizen_name=citizen.name,  # type: ignore
                skill=str(booking.skill),
                status=str(booking.status),
                job_price=booking.job_price,  # type: ignore
                platform_fee=booking.platform_fee,  # type: ignore
                created_at=booking.created_at,  # type: ignore
            )
        )
    return result

@router.get("/earnings-distribution", response_model=EarningsDistributionResponse)
def get_federation_earnings_distribution(db: Session = Depends(get_db)):
    return get_earnings_distribution(db=db)
