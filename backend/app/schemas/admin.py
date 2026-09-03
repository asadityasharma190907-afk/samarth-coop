from typing import Literal
from pydantic import BaseModel


class WorkerVerificationUpdate(BaseModel):
    verification_status: Literal["pending", "verified", "rejected"]

