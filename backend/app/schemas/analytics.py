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


class RevenueAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: str
    total_bookings: int
    completed_bookings: int
    gross_merchandise_value: float
    platform_revenue_2_5_pct: float
    welfare_fund_collected_2_5_pct: float
    payment_gateway_cost_est_2_pct: float
    net_platform_margin: float
    avg_order_value: float
    breakeven_bookings_per_month: int
    current_pct_of_breakeven: float
    surge_revenue: float
