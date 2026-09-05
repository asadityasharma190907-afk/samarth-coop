from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PricingContext(BaseModel):
    skill: str
    lat: float
    lng: float
    urgency: Literal["normal", "urgent", "emergency"] = "normal"
    hour_of_day: int


class PricingResult(BaseModel):
    base_price: Decimal
    final_price: Decimal
    surge_surplus: Decimal
    is_surging: bool
    worker_payout: Decimal
    platform_fee: Decimal
    welfare_fund: Decimal
    multipliers_applied: dict[str, float]

    model_config = ConfigDict(from_attributes=True)
