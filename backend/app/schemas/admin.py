from typing import Literal
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class WorkerVerificationUpdate(BaseModel):
    verification_status: Literal["pending", "verified", "rejected"]

class AdminWorkerItemResponse(BaseModel):
    worker_id: UUID
    user_id: UUID
    name: str
    phone: str
    skill: str
    verification_status: Literal["pending", "verified", "rejected"]
    created_at: datetime
