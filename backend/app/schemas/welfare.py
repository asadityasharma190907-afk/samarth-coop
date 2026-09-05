from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WelfareFundSummaryResponse(BaseModel):
    total_fees: Decimal
    completed_bookings: int
    total_disbursements: Decimal = Decimal("0.00")
    remaining_balance: Decimal = Decimal("0.00")


class DisbursementRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    category: Literal["insurance", "tool_loan", "training", "emergency", "pension"]
    description: str | None = None


class DisbursementResponse(BaseModel):
    id: UUID
    amount: Decimal
    category: str
    description: str | None
    disbursed_at: datetime
    remaining_fund_balance: Decimal

    model_config = ConfigDict(from_attributes=True)
