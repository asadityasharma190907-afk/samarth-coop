from decimal import Decimal

from pydantic import BaseModel


class WelfareFundSummaryResponse(BaseModel):
    total_fees: Decimal
    completed_bookings: int
