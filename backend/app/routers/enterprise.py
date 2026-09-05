import math
import uuid
from decimal import Decimal

from fastapi import APIRouter, status

from app.schemas.enterprise import (
    BulkBookingLineItemResponse,
    BulkBookingRequest,
    BulkBookingResponse,
)
from app.services.booking import JOB_PRICES

router = APIRouter()

DEFAULT_SKILL_RATE = Decimal("500.00")

SCHEDULE_MULTIPLIERS = {
    "daily": 22,
    "weekly": 4,
    "weekly_monday": 4,
    "weekly_tuesday": 4,
    "weekly_wednesday": 4,
    "weekly_thursday": 4,
    "weekly_friday": 4,
    "weekly_saturday": 4,
    "weekly_sunday": 4,
    "biweekly": 2,
    "bi_weekly": 2,
    "fortnightly": 2,
    "monthly": 1,
    "one_time": 1,
}


def get_schedule_multiplier(schedule: str) -> int:
    sched = schedule.lower().strip()
    if sched in SCHEDULE_MULTIPLIERS:
        return SCHEDULE_MULTIPLIERS[sched]
    if "daily" in sched:
        return 22
    if "week" in sched:
        return 4
    if "bi" in sched or "fortnight" in sched:
        return 2
    return 1


def calculate_workers_needed(quantity: int, schedule_multiplier: int) -> int:
    # Full time baseline is ~22 working days/month
    # If daily (22 days), full workforce is deployed (workers = quantity)
    # If part-time / weekly (e.g. 4 days), cooperative workers can be pooled across accounts
    if schedule_multiplier >= 20:
        return quantity
    return max(1, math.ceil((quantity * schedule_multiplier) / 22))


@router.post(
    "/bookings",
    response_model=BulkBookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate B2G / Enterprise bulk booking contract estimate",
)
def create_enterprise_bulk_booking(payload: BulkBookingRequest) -> BulkBookingResponse:
    contract_id = uuid.uuid4()
    line_items: list[BulkBookingLineItemResponse] = []

    total_bookings = 0
    total_monthly_cost = Decimal("0.00")
    total_workers_needed = 0

    for item in payload.bookings:
        normalized_skill = item.skill.lower().strip()
        base_rate = JOB_PRICES.get(normalized_skill, DEFAULT_SKILL_RATE)
        multiplier = get_schedule_multiplier(item.schedule)

        monthly_cost = base_rate * item.quantity * multiplier
        total_cost = monthly_cost * item.months
        workers_needed = calculate_workers_needed(item.quantity, multiplier)

        line_items.append(
            BulkBookingLineItemResponse(
                skill=item.skill,
                quantity=item.quantity,
                schedule=item.schedule,
                months=item.months,
                base_rate=base_rate,
                schedule_multiplier=multiplier,
                monthly_cost=monthly_cost,
                total_cost=total_cost,
                workers_needed=workers_needed,
            )
        )

        total_bookings += item.quantity
        total_monthly_cost += monthly_cost
        total_workers_needed += workers_needed

    welfare_contribution = (total_monthly_cost * Decimal("0.05")).quantize(
        Decimal("0.01")
    )

    return BulkBookingResponse(
        contract_id=contract_id,
        institution=payload.institution_name,
        total_bookings=total_bookings,
        estimated_monthly_cost=total_monthly_cost.quantize(Decimal("0.01")),
        cooperative_workers_needed=total_workers_needed,
        welfare_fund_contribution=welfare_contribution,
        line_items=line_items,
    )
