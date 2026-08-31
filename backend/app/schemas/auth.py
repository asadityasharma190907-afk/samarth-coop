from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class BaseRegisterRequest(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, json_schema_extra={"example": "Ravi Sharma"}
    )
    phone: str = Field(
        ..., min_length=10, max_length=15, json_schema_extra={"example": "9876543210"}
    )
    password: str = Field(..., min_length=6, json_schema_extra={"example": "secure123"})


class CitizenRegisterRequest(BaseRegisterRequest):
    role: Literal["citizen"] = "citizen"


AllowedSkills = Literal[
    "electrician",
    "plumber",
    "carpenter",
    "painter",
    "cleaner",
    "gardener",
    "cook",
    "driver",
    "tailor",
    "mason",
]


class WorkerRegisterRequest(BaseRegisterRequest):
    role: Literal["worker"]
    skill: AllowedSkills
    lat: float = Field(..., ge=-90.0, le=90.0, json_schema_extra={"example": 26.9280})
    lng: float = Field(..., ge=-180.0, le=180.0, json_schema_extra={"example": 75.8100})


RegisterRequest = Annotated[
    CitizenRegisterRequest | WorkerRegisterRequest, Field(discriminator="role")
]


class LoginRequest(BaseModel):
    phone: str = Field(
        ..., min_length=10, max_length=15, json_schema_extra={"example": "9876543210"}
    )
    password: str = Field(..., min_length=6, json_schema_extra={"example": "secure123"})


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    role: str
