from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FederationStatsResponse(BaseModel):
    registered_workers: int
    completed_bookings: int
    welfare_fund_total: Decimal


class FederationBookingResponse(BaseModel):
    id: UUID
    citizen_name: str
    skill: str
    status: str
    job_price: Decimal
    platform_fee: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
