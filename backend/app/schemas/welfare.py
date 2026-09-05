from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WelfareFundSummaryResponse(BaseModel):
    total_fees: Decimal
    completed_bookings: int
    total_disbursed: Decimal = Decimal("0.00")
    remaining_balance: Decimal = Decimal("0.00")
    category_breakdown: Dict[str, Decimal] = Field(default_factory=dict)


class DisbursementRequest(BaseModel):
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    category: str
    description: Optional[str] = None


class DisbursementResponse(BaseModel):
    id: UUID
    amount: Decimal
    category: str
    description: Optional[str] = None
    disbursed_by: Optional[UUID] = None
    disbursed_at: datetime
    remaining_fund_balance: Decimal


class DisbursementItem(BaseModel):
    id: UUID
    amount: Decimal
    category: str
    description: Optional[str] = None
    disbursed_at: datetime
