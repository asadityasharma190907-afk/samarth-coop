from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import FairnessMetricsResponse
from app.services.analytics import get_fairness_metrics

router = APIRouter()


@router.get("/fairness", response_model=FairnessMetricsResponse)
def get_fairness(db: Session = Depends(get_db)):
    return get_fairness_metrics(db=db)
