from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    WorkerRegisterRequest,
)
from app.services.auth import (
    authenticate_user,
    create_access_token,
    register_citizen,
    register_worker,
)

router = APIRouter()


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    if isinstance(payload, WorkerRegisterRequest):
        new_user = register_worker(db, payload)
    else:
        new_user = register_citizen(db, payload)

    access_token = create_access_token(
        {"user_id": str(new_user.id), "name": new_user.name, "role": new_user.role}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        role=new_user.role,
    )


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.phone, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {"user_id": str(user.id), "name": user.name, "role": user.role}
    )

    return TokenResponse(
        access_token=access_token, token_type="bearer", user_id=user.id, role=user.role
    )
