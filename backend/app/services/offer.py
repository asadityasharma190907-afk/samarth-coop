import threading
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.models.worker_profile import WorkerProfile
from app.services.dispatch import get_ranked_workers

_accept_lock = threading.Lock()


def check_and_expire_offer(offer: BookingOffer, db: Session) -> bool:

    if offer.status != "offered":
        return False

    offer_expires_at = offer.expires_at
    if offer_expires_at.tzinfo is None:
        offer_expires_at = offer_expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > offer_expires_at:
        # Lock the booking to prevent race condition during cascade
        booking = (
            db.query(Booking).filter_by(id=offer.booking_id).with_for_update().first()
        )
        if not booking or booking.status != "pending":
            return False

        # Re-check offer status inside lock
        db.refresh(offer)
        if offer.status != "offered":
            return False

        offer.status = "expired"  # type: ignore
        cascade_to_next(booking, offer, db)
        return True

    return False


def cascade_to_next(booking: Booking, current_offer: BookingOffer, db: Session) -> None:
    already_offered = (
        db.query(BookingOffer.worker_id).filter_by(booking_id=booking.id).all()
    )
    excluded_ids = {row.worker_id for row in already_offered}

    ranked_workers = get_ranked_workers(
        str(booking.skill), float(str(booking.lat)), float(str(booking.lng)), db
    )

    next_worker = None
    for worker in ranked_workers:
        if worker["worker_id"] not in excluded_ids:
            next_worker = worker
            break

    if next_worker:
        new_offer = BookingOffer(
            booking_id=booking.id,
            worker_id=next_worker["worker_id"],
            rank_at_offer=current_offer.rank_at_offer + 1,
            dispatch_score=next_worker["dispatch_score"],
            status="offered",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
        )
        db.add(new_offer)
    else:
        booking.status = "cancelled"  # type: ignore

    db.commit()


def decline_offer(offer_id: UUID, worker_id: UUID, db: Session) -> None:
    offer = db.query(BookingOffer).filter_by(id=offer_id).first()
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
        )

    if offer.worker_id != worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Offer does not belong to this worker",
        )

    if check_and_expire_offer(offer, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Offer has expired"
        )

    if offer.status != "offered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot decline offer with status {offer.status}",
        )

    # Apply row lock on booking
    booking = db.query(Booking).filter_by(id=offer.booking_id).with_for_update().first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking already assigned or cancelled",
        )

    offer.status = "declined"  # type: ignore

    cascade_to_next(booking, offer, db)


def accept_offer(offer_id: UUID, worker_id: UUID, db: Session) -> None:
    # Query the offer
    offer = db.query(BookingOffer).filter_by(id=offer_id).first()
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
        )

    if offer.worker_id != worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Offer does not belong to this worker",
        )

    if check_and_expire_offer(offer, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Offer has expired"
        )

    with _accept_lock:
        # Apply row lock on booking (AD-6)
        booking = (
            db.query(Booking).filter_by(id=offer.booking_id).with_for_update().first()
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        db.refresh(booking)
        db.refresh(offer)

        if booking.status != "pending" or offer.status != "offered":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking already assigned or offer expired",
            )

        # Atomic update to guarantee concurrency safety across PostgreSQL and SQLite
        rows_updated = (
            db.query(Booking)
            .filter(Booking.id == offer.booking_id, Booking.status == "pending")
            .update(
                {Booking.status: "assigned", Booking.worker_id: worker_id},
                synchronize_session=False,
            )
        )

        if rows_updated == 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking already assigned or offer expired",
            )

        # Update offer
        offer.status = "accepted"  # type: ignore

        # Update worker availability
        worker_profile = db.query(WorkerProfile).filter_by(user_id=worker_id).first()
        if worker_profile:
            worker_profile.availability = False  # type: ignore

        db.commit()
