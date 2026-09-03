from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.worker_profile import WorkerProfile


from fastapi import status as status_code

def toggle_verification(worker_id: UUID, status: str, db: Session) -> WorkerProfile:
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == worker_id).first()
    if not profile:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail="Worker profile not found")

    profile.verification_status = status
    db.commit()
    db.refresh(profile)
    return profile
