from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.services.auth import hash_password, create_access_token

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.phone == payload.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered"
        )

    hashed_pwd = hash_password(payload.password)
    new_user = User(
        name=payload.name,
        phone=payload.phone,
        password_hash=hashed_pwd,
        role=payload.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

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
