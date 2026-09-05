from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.schemas.bookings import CreateBookingRequest
from app.schemas.pricing import PricingContext
from app.services.dispatch import get_ranked_workers
from app.services.pricing import compute_fair_surge_price
from app.services.push import send_push_notification

JOB_PRICES = {
    "electrician": Decimal("500.00"),
    "plumber": Decimal("450.00"),
    "carpenter": Decimal("600.00"),
    "painter": Decimal("550.00"),
    "cleaner": Decimal("400.00"),
    "appliance repair": Decimal("500.00"),
    "gardener": Decimal("350.00"),
    "pest control": Decimal("600.00"),
    "mechanic": Decimal("500.00"),
    "mason": Decimal("650.00"),
}
DEFAULT_JOB_PRICE = Decimal("500.00")


def get_category_price(skill: str) -> Decimal:
    return JOB_PRICES.get(skill.lower().strip(), DEFAULT_JOB_PRICE)


def dispatch_first_offer(booking: Booking, db: Session) -> None:
    ranked_workers = get_ranked_workers(
        str(booking.skill),
        float(str(booking.lat)),
        float(str(booking.lng)),
        db,
        gender_preference=str(booking.gender_preference or "any"),
    )

    if not ranked_workers:
        booking.status = "cancelled"  # type: ignore
        db.commit()
        return

    top_worker = ranked_workers[0]
    offer = BookingOffer(
        booking_id=booking.id,
        worker_id=top_worker["worker_id"],
        rank_at_offer=1,
        dispatch_score=top_worker["dispatch_score"],
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)

    worker_profile = (
        db.query(WorkerProfile).filter_by(user_id=top_worker["worker_id"]).first()
    )
    if worker_profile and worker_profile.push_subscription:
        price_val = int(booking.job_price) if booking.job_price else 500
        send_push_notification(
            subscription_raw=worker_profile.push_subscription,
            title="Samarth -- New Job Offer",
            body=f"{str(booking.skill).capitalize()} work -- INR {price_val}. Tap to accept.",
            data={"offer_id": str(offer.id), "url": "/worker/offers"},
        )


def create_booking(
    citizen: User, booking_in: CreateBookingRequest, db: Session
) -> Booking:
    # Compute Fair-Surge price dynamically
    ctx = PricingContext(
        skill=booking_in.skill.lower().strip(),
        lat=float(booking_in.lat),
        lng=float(booking_in.lng),
        urgency=booking_in.urgency.value,
        hour_of_day=datetime.now(timezone.utc).hour,
    )
    pricing = compute_fair_surge_price(ctx, db)

    platform_fee = (pricing.final_price * Decimal("0.05")).quantize(Decimal("0.01"))

    new_booking = Booking(
        citizen_id=citizen.id,
        skill=booking_in.skill.lower().strip(),
        lat=booking_in.lat,
        lng=booking_in.lng,
        description=booking_in.description,
        job_price=pricing.final_price,
        platform_fee=platform_fee,
        status="pending",
        # Fair-Surge snapshot (immutable after INSERT)
        base_price=pricing.base_price,
        surge_surplus=pricing.surge_surplus,
        is_surging=pricing.is_surging,
        urgency=booking_in.urgency.value,
        gender_preference=booking_in.gender_preference,
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    dispatch_first_offer(new_booking, db)
    db.refresh(new_booking)
    return new_booking


def complete_booking(booking_id: UUID, worker_id: UUID, db: Session) -> Booking:
    # Row lock for the booking
    booking = db.query(Booking).filter_by(id=booking_id).with_for_update().first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    if booking.status != "assigned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assigned bookings can be completed",
        )

    # Verify that the worker trying to complete is the assigned worker
    accepted_offer = (
        db.query(BookingOffer)
        .filter_by(booking_id=booking_id, status="accepted")
        .first()
    )

    if not accepted_offer or accepted_offer.worker_id != worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Booking is not assigned to this worker",
        )

    # 95/5 Split computation
    platform_fee = (booking.job_price * Decimal("0.05")).quantize(Decimal("0.01"))
    booking.platform_fee = platform_fee
    booking.status = "completed"  # type: ignore

    # Make the worker available again
    worker_profile = db.query(WorkerProfile).filter_by(user_id=worker_id).first()
    if worker_profile:
        worker_profile.availability = True  # type: ignore

    db.commit()
    db.refresh(booking)
    return booking


def submit_rating(
    booking_id: UUID, rating_val: int, citizen_id: UUID, db: Session
) -> Booking:
    booking = db.query(Booking).filter_by(id=booking_id, citizen_id=citizen_id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    if booking.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed bookings can be rated",
        )

    if booking.rating is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking has already been rated",
        )

    worker_profile = (
        db.query(WorkerProfile).filter_by(user_id=booking.worker_id).first()
    )
    if not worker_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Worker profile not found"
        )

    # Running average calculation
    current_rating = worker_profile.rating
    current_count = worker_profile.rating_count or 0

    if current_rating is None:
        new_rating = Decimal(rating_val)
    else:
        new_rating = (
            (current_rating * Decimal(current_count)) + Decimal(rating_val)  # type: ignore
        ) / Decimal(current_count + 1)  # type: ignore

    worker_profile.rating = new_rating.quantize(Decimal("0.1"))  # type: ignore
    worker_profile.rating_count = current_count + 1  # type: ignore

    booking.rating = rating_val  # type: ignore

    db.commit()
    db.refresh(booking)

    return booking


def flag_booking_dispute(
    booking_id: UUID, reason: str, user_id: UUID, db: Session
) -> Booking:
    booking = db.query(Booking).filter_by(id=booking_id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    if user_id != booking.citizen_id and user_id != booking.worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to dispute this booking",
        )

    if booking.status not in ["assigned", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only assigned or completed bookings can be disputed",
        )

    booking.status = "disputed"  # type: ignore
    booking.dispute_reason = reason.strip()  # type: ignore

    db.commit()
    db.refresh(booking)

    return booking


def _recompute_trust_score(citizen: User, db: Session) -> int:
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_cancellations = (
        db.query(Booking)
        .filter(
            Booking.citizen_id == citizen.id,
            Booking.status == "cancelled",
            Booking.created_at >= thirty_days_ago,
        )
        .count()
    )

    completed_with_rating = (
        db.query(Booking)
        .filter(
            Booking.citizen_id == citizen.id,
            Booking.status == "completed",
            Booking.rating.isnot(None),
        )
        .count()
    )

    score = 100 - (10 * recent_cancellations) + (5 * completed_with_rating)
    return max(0, min(100, score))  # clamp to [0, 100]


def cancel_booking(booking_id: UUID, citizen_id: UUID, db: Session) -> Booking:
    booking = db.query(Booking).filter_by(id=booking_id, citizen_id=citizen_id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    if booking.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed or already cancelled booking",
        )

    # Revert worker availability if assigned
    if booking.status == "assigned":
        accepted_offer = (
            db.query(BookingOffer)
            .filter_by(booking_id=booking_id, status="accepted")
            .first()
        )
        if accepted_offer:
            worker_profile = (
                db.query(WorkerProfile)
                .filter_by(user_id=accepted_offer.worker_id)
                .first()
            )
            if worker_profile:
                worker_profile.availability = True  # type: ignore

    booking.status = "cancelled"  # type: ignore
    db.flush()

    citizen = db.query(User).filter_by(id=citizen_id).first()
    if citizen:
        citizen.cancellation_count = (citizen.cancellation_count or 0) + 1  # type: ignore
        citizen.citizen_trust_score = _recompute_trust_score(citizen, db)  # type: ignore

    db.commit()
    db.refresh(booking)

    return booking
