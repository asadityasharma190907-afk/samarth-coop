from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.schemas.bookings import (
    AssignedWorkerDetail,
    BookingResponse,
    CreateBookingRequest,
    RatingRequest,
)
from app.services.booking import complete_booking, create_booking, submit_rating
from app.services.dispatch import haversine_km

router = APIRouter()


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def post_booking(
    booking_in: CreateBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = create_booking(current_user, booking_in, db)
    return BookingResponse.model_validate(booking)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: UUID, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    response_obj = BookingResponse.model_validate(booking)

    if booking.status == "assigned":
        # Find the accepted offer
        accepted_offer = (
            db.query(BookingOffer)
            .filter(
                BookingOffer.booking_id == booking_id, BookingOffer.status == "accepted"
            )
            .first()
        )

        if accepted_offer:
            worker = db.query(User).filter(User.id == accepted_offer.worker_id).first()
            profile = (
                db.query(WorkerProfile)
                .filter(WorkerProfile.user_id == accepted_offer.worker_id)
                .first()
            )

            if worker and profile:
                distance = haversine_km(
                    float(str(booking.lat)),
                    float(str(booking.lng)),
                    float(str(profile.lat)),
                    float(str(profile.lng)),
                )

                response_obj.assigned_worker = AssignedWorkerDetail(
                    id=worker.id,  # type: ignore
                    name=worker.name,  # type: ignore
                    skill=str(profile.skill),
                    rating=profile.rating,  # type: ignore
                    verified=bool(profile.verified),
                    distance_km=round(distance, 1),
                )

    return response_obj


@router.put("/{booking_id}/complete", response_model=BookingResponse)
def complete_booking_endpoint(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = complete_booking(booking_id, current_user.id, db)  # type: ignore
    return BookingResponse.model_validate(booking)


@router.post("/{booking_id}/rating", response_model=BookingResponse)
def rate_booking(
    booking_id: UUID,
    payload: RatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = submit_rating(booking_id, payload.rating, current_user.id, db)  # type: ignore
    return BookingResponse.model_validate(booking)
