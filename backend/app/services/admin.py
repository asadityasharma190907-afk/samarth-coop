from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.worker_profile import WorkerProfile


def toggle_verification(worker_id: UUID, verified: bool, db: Session) -> WorkerProfile:
    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == worker_id).first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Worker profile not found")

    profile.verified = verified
    db.commit()
    db.refresh(profile)
    return profile
