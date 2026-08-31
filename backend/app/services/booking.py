from decimal import Decimal
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.booking import Booking
from app.models.user import User
from app.schemas.bookings import CreateBookingRequest

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


def create_booking(
    citizen: User,
    booking_in: CreateBookingRequest,
    db: Session
) -> Booking:
    # Snapshot job_price from category rate
    job_price = get_category_price(booking_in.skill)
    platform_fee = (job_price * Decimal("0.05")).quantize(Decimal("0.01"))
    
    new_booking = Booking(
        citizen_id=citizen.id,
        skill=booking_in.skill.lower().strip(),
        lat=booking_in.lat,
        lng=booking_in.lng,
        description=booking_in.description,
        job_price=job_price,
        platform_fee=platform_fee,
        status="pending",
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking
