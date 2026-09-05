from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.schemas.workers import WorkerResponse
from app.services.dispatch_v2 import get_ranked_workers_adaptive

router = APIRouter()


@router.get("", response_model=list[WorkerResponse])
def get_workers(
    skill: str = Query(..., description="Worker skill filtering"),
    lat: float = Query(..., description="Citizen latitude"),
    lng: float = Query(..., description="Citizen longitude"),
    db: Session = Depends(get_db),
):
    return get_ranked_workers_adaptive(skill, lat, lng, db)


@router.post("/me/ping", response_model=dict)
def worker_heartbeat(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workers can send a heartbeat ping",
        )

    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == current_user.id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Worker profile not found"
        )

    now = datetime.now(timezone.utc)
    profile.last_active_at = now
    db.commit()

    return {
        "last_active_at": now.isoformat(),
        "availability_bonus_eligible": True,
    }


@router.get("/me", response_model=dict)
def get_current_worker_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workers have a worker profile",
        )

    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == current_user.id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Worker profile not found"
        )

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "skill": profile.skill,
        "lat": profile.lat,
        "lng": profile.lng,
        "rating": profile.rating,
        "availability": profile.availability,
        "verification_status": profile.verification_status,
        "last_active_at": profile.last_active_at,
        "created_at": profile.created_at,
    }
