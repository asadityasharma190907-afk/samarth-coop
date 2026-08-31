from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.models.worker_profile import WorkerProfile


def accept_offer(offer_id: UUID, worker_id: UUID, db: Session) -> None:
    # Query the offer
    offer = db.query(BookingOffer).filter_by(id=offer_id).first()
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    if offer.worker_id != worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Offer does not belong to this worker"
        )

    # Check if expired
    offer_expires_at = offer.expires_at
    if offer_expires_at.tzinfo is None:
        offer_expires_at = offer_expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > offer_expires_at:
        # We can update status to expired if we want, but AD-8 says lazy check.
        offer.status = "expired"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer has expired"
        )

    # Apply row lock on booking (AD-6)
    booking = (
        db.query(Booking)
        .filter_by(id=offer.booking_id)
        .with_for_update()
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking already assigned"
        )

    # Assign booking
    booking.status = "assigned"
    
    # Update offer
    offer.status = "accepted"

    # Update worker availability
    worker_profile = db.query(WorkerProfile).filter_by(user_id=worker_id).first()
    if worker_profile:
        worker_profile.availability = False

    db.commit()
