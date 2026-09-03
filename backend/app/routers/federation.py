from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.database import get_db
from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
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
    Worker = aliased(User)
    # Returns all bookings, descending by creation
    bookings_data = (
        db.query(Booking, User, Worker)
        .join(User, User.id == Booking.citizen_id)
        .outerjoin(
            BookingOffer,
            (BookingOffer.booking_id == Booking.id)
            & (BookingOffer.status == "accepted"),
        )
        .outerjoin(Worker, Worker.id == BookingOffer.worker_id)
        .order_by(Booking.created_at.desc())
        .limit(50)  # Just latest 50 for the dashboard
        .all()
    )

    result = []
    for booking, citizen, worker in bookings_data:
        result.append(
            FederationBookingResponse(
                id=booking.id,  # type: ignore
                citizen_name=citizen.name,  # type: ignore
                skill=str(booking.skill),
                status=str(booking.status),
                job_price=booking.job_price,  # type: ignore
                platform_fee=booking.platform_fee,  # type: ignore
                created_at=booking.created_at,  # type: ignore
                worker_name=worker.name if worker else None,
                dispute_reason=booking.dispute_reason,
            )
        )
    return result


@router.get("/earnings-distribution", response_model=EarningsDistributionResponse)
def get_federation_earnings_distribution(db: Session = Depends(get_db)):
    return get_earnings_distribution(db=db)
