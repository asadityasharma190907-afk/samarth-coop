from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class EarningsEntry(BaseModel):
    date: date
    skill: str
    job_price: Decimal
    worker_payout: Decimal
    platform_fee: Decimal


class WalletResponse(BaseModel):
    weekly_earnings: Decimal
    lifetime_earnings: Decimal
    entries: list[EarningsEntry]
