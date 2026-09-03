from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status as status_code
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.admin import WorkerVerificationUpdate, AdminWorkerItemResponse
from app.services.admin import update_verification_status, get_workers_by_status
from typing import Literal, List

router = APIRouter()

@router.get("/workers", response_model=List[AdminWorkerItemResponse])
def get_pending_workers(
    status: Literal["pending", "verified", "rejected"] = "pending",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status_code.HTTP_403_FORBIDDEN,
            detail="Only admins can view worker statuses",
        )
    return get_workers_by_status(status=status, db=db)

@router.patch("/workers/{id}/verify")
def verify_worker(
    id: UUID,
    payload: WorkerVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status_code.HTTP_403_FORBIDDEN,
            detail="Only admins can verify workers",
        )

    profile = update_verification_status(worker_id=id, status=payload.verification_status, db=db)
    return {
        "message": f"Worker verification status updated to {profile.verification_status}",
        "verification_status": profile.verification_status,
    }
