from uuid import UUID

from fastapi import HTTPException
from fastapi import status as status_code
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.worker_profile import WorkerProfile


def update_verification_status(
    worker_id: UUID, status: str, db: Session
) -> WorkerProfile:
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == worker_id).first()
    if not profile:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail="Worker profile not found",
        )

    profile.verification_status = status
    db.commit()
    db.refresh(profile)
    return profile


def get_workers_by_status(status: str, db: Session) -> list[dict]:
    results = (
        db.query(WorkerProfile, User)
        .join(User, User.id == WorkerProfile.user_id)
        .filter(WorkerProfile.verification_status == status)
        .all()
    )

    response = []
    for profile, user in results:
        response.append(
            {
                "worker_id": profile.id,
                "user_id": user.id,
                "name": user.name,
                "phone": user.phone,
                "skill": profile.skill,
                "verification_status": profile.verification_status,
                "created_at": profile.created_at,
            }
        )
    return response
