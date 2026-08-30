from uuid import UUID
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Ravi Sharma"})
    phone: str = Field(..., min_length=10, max_length=15, json_schema_extra={"example": "9876543210"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "secure123"})
    role: str = Field(default="citizen", json_schema_extra={"example": "citizen"})


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    role: str
