from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import RegisterRequest, TokenResponse, WorkerRegisterRequest, CitizenRegisterRequest
from app.services.auth import create_access_token, register_citizen, register_worker

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    if isinstance(payload, WorkerRegisterRequest):
        new_user = register_worker(db, payload)
    else:
        new_user = register_citizen(db, payload)

    access_token = create_access_token({
        "user_id": str(new_user.id),
        "name": new_user.name,
        "role": new_user.role
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        role=new_user.role
    )
