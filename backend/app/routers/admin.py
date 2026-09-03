from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.admin import WorkerVerificationUpdate
from app.services.admin import toggle_verification

router = APIRouter()


@router.patch("/workers/{id}/verify")
def verify_worker(
    id: UUID,
    payload: WorkerVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify workers",
        )

    profile = toggle_verification(worker_id=id, status=payload.verification_status, db=db)
    return {
        "message": "Worker verification updated successfully",
        "verification_status": profile.verification_status,
    }
