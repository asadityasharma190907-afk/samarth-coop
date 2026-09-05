from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BulkBookingItemRequest(BaseModel):
    skill: str = Field(
        ...,
        description="Required skill category (e.g. electrician, cleaner, plumber)",
    )
    quantity: int = Field(
        1,
        ge=1,
        description="Number of workers or recurring slots required",
    )
    schedule: str = Field(
        "daily",
        description="Recurrence schedule (e.g. daily, weekly_monday, weekly, biweekly, monthly)",
    )
    months: int = Field(
        1,
        ge=1,
        description="Contract duration in months",
    )

    @field_validator("skill")
    @classmethod
    def validate_skill_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Skill cannot be empty or whitespace")
        return v.strip().lower()


class BulkBookingRequest(BaseModel):
    institution_name: str = Field(
        ...,
        min_length=1,
        description="Name of the B2G/Enterprise institution (e.g. District Collectorate, Jaipur)",
    )
    bookings: list[BulkBookingItemRequest] = Field(
        ...,
        min_length=1,
        description="List of skill requirements and schedules",
    )

    @field_validator("institution_name")
    @classmethod
    def validate_institution_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Institution name cannot be empty or whitespace")
        return v.strip()


class BulkBookingLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill: str
    quantity: int
    schedule: str
    months: int
    base_rate: Decimal
    schedule_multiplier: int
    monthly_cost: Decimal
    total_cost: Decimal
    workers_needed: int


class BulkBookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contract_id: UUID
    institution: str
    total_bookings: int
    estimated_monthly_cost: Decimal
    cooperative_workers_needed: int
    welfare_fund_contribution: Decimal
    line_items: list[BulkBookingLineItemResponse]
