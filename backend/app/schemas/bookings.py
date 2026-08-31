from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from uuid import UUID
from typing import Optional
from datetime import datetime


class CreateBookingRequest(BaseModel):
    skill: str = Field(..., description="Required skill category (e.g. electrician, plumber)")
    lat: Decimal = Field(..., description="Citizen latitude")
    lng: Decimal = Field(..., description="Citizen longitude")
    description: Optional[str] = Field(None, description="Optional job description")


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: UUID
    status: str
    job_price: Decimal
    platform_fee: Optional[Decimal] = None
    skill: Optional[str] = None
    lat: Optional[Decimal] = None
    lng: Optional[Decimal] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
