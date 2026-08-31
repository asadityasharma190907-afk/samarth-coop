from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.schemas.auth import CitizenRegisterRequest, WorkerRegisterRequest


def hash_password(password: str) -> str:
    # Ensure password is truncated to max 72 bytes for bcrypt standard
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def register_citizen(db: Session, payload: CitizenRegisterRequest) -> User:
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
    return new_user


def register_worker(db: Session, payload: WorkerRegisterRequest) -> User:
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
    db.flush()

    worker_profile = WorkerProfile(
        user_id=new_user.id,
        skill=payload.skill,
        lat=payload.lat,
        lng=payload.lng
    )
    db.add(worker_profile)
    db.commit()
    db.refresh(new_user)
    return new_user
