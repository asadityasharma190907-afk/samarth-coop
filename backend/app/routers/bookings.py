from datetime import datetime, timezone
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
    DisputeBookingRequest,
    DisputeBookingResponse,
    PricePreviewResponse,
    RatingRequest,
    UrgencyTier,
)
from app.schemas.pricing import PricingContext
from app.services.booking import (
    cancel_booking,
    complete_booking,
    create_booking,
    flag_booking_dispute,
    submit_rating,
)
from app.services.dispatch import haversine_km
from app.services.pricing import compute_fair_surge_price

router = APIRouter()


@router.get("", response_model=list[BookingResponse])
def get_recent_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .filter(
            (Booking.citizen_id == current_user.id)
            | (Booking.worker_id == current_user.id)
        )
        .order_by(Booking.created_at.desc())
        .limit(20)
        .all()
    )
    return [BookingResponse.model_validate(b) for b in bookings]


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def post_booking(
    booking_in: CreateBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = create_booking(current_user, booking_in, db)
    return BookingResponse.model_validate(booking)


@router.get("/price-preview", response_model=PricePreviewResponse)
def get_price_preview(
    skill: str,
    lat: float,
    lng: float,
    urgency: UrgencyTier = UrgencyTier.normal,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clean_skill = skill.lower().strip()
    ctx = PricingContext(
        skill=clean_skill,
        lat=lat,
        lng=lng,
        urgency=urgency.value,
        hour_of_day=datetime.now(timezone.utc).hour,
    )
    try:
        pricing = compute_fair_surge_price(ctx, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    u_mult = pricing.multipliers_applied.get("u_multiplier", 1.0)
    surge_reason = "High demand in your area" if pricing.is_surging else "Normal demand"

    return PricePreviewResponse(
        skill=clean_skill,
        base_price=pricing.base_price,
        final_price=pricing.final_price,
        surge_surplus=pricing.surge_surplus,
        is_surging=pricing.is_surging,
        surge_reason=surge_reason,
        urgency_multiplier=u_mult,
        worker_earns=pricing.worker_payout,
        welfare_fund_contribution=pricing.welfare_fund,
        platform_fee=pricing.platform_fee,
    )


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
                    verification_status=profile.verification_status,  # type: ignore
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


@router.post("/{booking_id}/dispute", response_model=DisputeBookingResponse)
def dispute_booking(
    booking_id: UUID,
    payload: DisputeBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = flag_booking_dispute(booking_id, payload.reason, current_user.id, db)  # type: ignore
    return DisputeBookingResponse(
        booking_id=booking.id,  # type: ignore
        status=booking.status,  # type: ignore
        dispute_reason=booking.dispute_reason,  # type: ignore
        message="Dispute registered. Cooperative mediation initiated.",
    )


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking_endpoint(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = cancel_booking(booking_id, current_user.id, db)  # type: ignore
    return BookingResponse.model_validate(booking)
