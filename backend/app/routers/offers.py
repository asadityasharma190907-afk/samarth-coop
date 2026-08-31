from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.schemas.offers import OfferActionRequest, OfferResponse, WorkerOfferDetail
from app.services.dispatch import haversine_km
from app.services.offer import accept_offer, check_and_expire_offer, decline_offer

router = APIRouter()


@router.get("/booking/{booking_id}", response_model=list[OfferResponse])
def get_booking_offers(booking_id: UUID, db: Session = Depends(get_db)):
    offers = (
        db.query(BookingOffer)
        .filter(BookingOffer.booking_id == booking_id)
        .order_by(BookingOffer.rank_at_offer.asc())
        .all()
    )

    # Lazy check for expiry on read
    expired_any = False
    for offer in offers:
        if check_and_expire_offer(offer, db):
            expired_any = True

    if expired_any:
        # Re-fetch offers to include newly cascaded ones
        offers = (
            db.query(BookingOffer)
            .filter(BookingOffer.booking_id == booking_id)
            .order_by(BookingOffer.rank_at_offer.asc())
            .all()
        )
    if not offers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No offers found for this booking",
        )

    return [OfferResponse.model_validate(offer) for offer in offers]


@router.get("/worker", response_model=list[WorkerOfferDetail])
def get_worker_offers(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # Get active offers for the worker
    offers = (
        db.query(BookingOffer)
        .filter(
            BookingOffer.worker_id == current_user.id, BookingOffer.status == "offered"
        )
        .all()
    )

    # Lazily expire them
    active_offers = []
    for offer in offers:
        if check_and_expire_offer(offer, db):
            continue
        active_offers.append(offer)

    # Get worker profile for location
    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == current_user.id).first()
    )
    if not profile:
        return []

    result = []
    for offer in active_offers:
        booking = db.query(Booking).filter(Booking.id == offer.booking_id).first()
        if not booking:
            continue

        distance = haversine_km(
            float(str(booking.lat)),
            float(str(booking.lng)),
            float(str(profile.lat)),
            float(str(profile.lng)),
        )

        detail_data = OfferResponse.model_validate(offer).model_dump()
        detail_data.update(
            {
                "job_price": booking.job_price,
                "skill": booking.skill,
                "lat": booking.lat,
                "lng": booking.lng,
                "distance_km": round(distance, 1),
            }
        )
        result.append(WorkerOfferDetail(**detail_data))

    # Return in descending order by created time (newest first)
    result.sort(key=lambda x: x.created_at, reverse=True)
    return result


@router.put("/{offer_id}", status_code=status.HTTP_200_OK)
def update_offer_status(
    offer_id: UUID,
    action_req: OfferActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    action = action_req.action.lower()
    if action not in ["accept", "decline"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only 'accept' and 'decline' actions are supported",
        )

    if action == "accept":
        accept_offer(offer_id, cast(UUID, current_user.id), db)
        return {"status": "success", "message": "Offer accepted and booking assigned"}
    else:
        decline_offer(offer_id, cast(UUID, current_user.id), db)
        return {"status": "success", "message": "Offer declined"}
