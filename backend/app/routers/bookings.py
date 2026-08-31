from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.bookings import BookingResponse, CreateBookingRequest
from app.services.booking import create_booking

router = APIRouter()


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def post_booking(
    booking_in: CreateBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = create_booking(current_user, booking_in, db)
    return BookingResponse.model_validate(booking)
