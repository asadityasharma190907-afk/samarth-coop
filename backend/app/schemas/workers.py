from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class WorkerResponse(BaseModel):
    worker_id: UUID
    name: str
    phone: str
    skill: str
    lat: Decimal
    lng: Decimal
    rating: Decimal | None = None
    distance_km: float
    weekly_earnings: Decimal
    dispatch_score: Decimal
    rating_is_default: bool
    reliability_penalty_applied: bool

    class Config:
        from_attributes = True
