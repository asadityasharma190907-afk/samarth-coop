from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import FairnessMetricsResponse, RevenueAnalyticsResponse
from app.services.analytics import get_fairness_metrics, get_revenue_metrics

router = APIRouter()


@router.get("/fairness", response_model=FairnessMetricsResponse)
def get_fairness(db: Session = Depends(get_db)):
    return get_fairness_metrics(db=db)


@router.get("/revenue", response_model=RevenueAnalyticsResponse)
def get_revenue(db: Session = Depends(get_db)):
    return get_revenue_metrics(db=db)
