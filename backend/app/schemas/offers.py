from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OfferResponse(BaseModel):
    id: UUID
    booking_id: UUID
    worker_id: UUID
    rank_at_offer: int
    dispatch_score: Decimal
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkerOfferDetail(OfferResponse):
    job_price: Decimal
    skill: str
    lat: Decimal
    lng: Decimal
    distance_km: float


class OfferActionRequest(BaseModel):
    action: str
