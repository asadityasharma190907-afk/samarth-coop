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
