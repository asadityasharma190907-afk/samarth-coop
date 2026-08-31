from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking_offer import BookingOffer
from app.schemas.offers import OfferResponse

router = APIRouter()


@router.get("/booking/{booking_id}", response_model=list[OfferResponse])
def get_booking_offers(booking_id: UUID, db: Session = Depends(get_db)):
    offers = (
        db.query(BookingOffer)
        .filter(BookingOffer.booking_id == booking_id)
        .order_by(BookingOffer.rank_at_offer.asc())
        .all()
    )
    if not offers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No offers found for this booking"
        )
    
    return [OfferResponse.model_validate(offer) for offer in offers]
