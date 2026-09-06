import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.worker_profile import WorkerProfile

router = APIRouter(tags=["Push Notifications"])


class PushSubscriptionSchema(BaseModel):
    subscription: dict[str, Any]


@router.get("/vapid-public-key")
def get_vapid_public_key():
    """Returns the VAPID public key required by frontend PushManager.subscribe()."""
    return {"public_key": settings.VAPID_PUBLIC_KEY}


@router.post("/subscribe", status_code=status.HTTP_200_OK)
def subscribe_push_notifications(
    body: PushSubscriptionSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Subscribes a worker user to browser Web Push notifications."""
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workers can subscribe to offer push notifications",
        )

    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == current_user.id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker profile not found",
        )

    profile.push_subscription = json.dumps(body.subscription)
    db.commit()
    db.refresh(profile)

    return {
        "status": "subscribed",
        "message": "Push notification subscription saved successfully",
    }
