from pydantic import BaseModel, ConfigDict


class WorkerOfferDistributionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    worker_id: str
    worker_name: str
    skill: str
    offers_count: int
    completed_bookings_count: int
    weekly_earnings: float


class IncomeRangeStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    min_earnings: float
    max_earnings: float
    median_earnings: float
    average_earnings: float
    gap_ratio: float


class FairnessMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    samarth_gini: float
    proximity_gini: float
    gini_improvement_pct: float
    income_range: IncomeRangeStats
    meena_effect_count: int
    meena_effect_description: str
    offers_distribution: list[WorkerOfferDistributionItem]
    total_active_workers: int
    total_weekly_earnings: float


class RevenueStream(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    amount: float
    percentage: float


class RevenueAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gmv: float
    platform_revenue: float
    welfare_fund: float

    avg_order_value: float
    blended_fee_percentage: float
    net_margin_per_booking: float

    breakeven_target_bookings: int
    current_bookings: int
    breakeven_percentage: float

    revenue_streams: list[RevenueStream]
