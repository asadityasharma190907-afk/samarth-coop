from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateBookingRequest(BaseModel):
    skill: str = Field(
        ..., description="Required skill category (e.g. electrician, plumber)"
    )
    lat: Decimal = Field(..., description="Citizen latitude")
    lng: Decimal = Field(..., description="Citizen longitude")
    description: str | None = Field(None, description="Optional job description")


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    booking_id: UUID = Field(validation_alias="id")
    status: str
    job_price: Decimal
    platform_fee: Decimal | None = None
    skill: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    description: str | None = None
    created_at: datetime | None = None
