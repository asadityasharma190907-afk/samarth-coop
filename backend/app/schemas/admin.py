from pydantic import BaseModel


class WorkerVerificationUpdate(BaseModel):
    verified: bool
