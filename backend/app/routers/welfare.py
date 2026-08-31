from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking
from app.schemas.welfare import WelfareFundSummaryResponse

router = APIRouter()


@router.get("/summary", response_model=WelfareFundSummaryResponse)
def get_welfare_summary(db: Session = Depends(get_db)):
    result = (
        db.query(
            func.coalesce(func.sum(Booking.platform_fee), 0).label("total_fees"),
            func.count(Booking.id).label("completed_bookings"),
        )
        .filter(Booking.status == "completed")
        .first()
    )

    return WelfareFundSummaryResponse(
        total_fees=result.total_fees if result else 0,
        completed_bookings=result.completed_bookings if result else 0,
    )
