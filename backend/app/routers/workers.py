from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.workers import WorkerResponse
from app.services.dispatch import get_ranked_workers

router = APIRouter()


@router.get("", response_model=list[WorkerResponse])
def get_workers(
    skill: str = Query(..., description="Worker skill filtering"),
    lat: float = Query(..., description="Citizen latitude"),
    lng: float = Query(..., description="Citizen longitude"),
    db: Session = Depends(get_db),
):
    return get_ranked_workers(skill, lat, lng, db)
