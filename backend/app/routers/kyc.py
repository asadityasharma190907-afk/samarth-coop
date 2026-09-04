import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.schemas.kyc import (
    AadhaarSendOTPRequest,
    AadhaarSendOTPResponse,
    AadhaarVerifyOTPRequest,
    AadhaarVerifyOTPResponse,
    PaymentCreateOrderResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)

router = APIRouter()


@router.post("/aadhaar/send-otp", response_model=AadhaarSendOTPResponse)
def send_aadhaar_otp(payload: AadhaarSendOTPRequest):
    if not payload.aadhaar_number.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aadhaar number must contain exactly 12 digits",
        )

    return AadhaarSendOTPResponse(
        status="success",
        transaction_id=f"tx_{uuid.uuid4().hex[:12]}",
        message="OTP sent successfully to registered mobile number",
    )


@router.post("/aadhaar/verify-otp", response_model=AadhaarVerifyOTPResponse)
def verify_aadhaar_otp(
    payload: AadhaarVerifyOTPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workers can undergo KYC verification",
        )

    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == current_user.id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_44_NOT_FOUND
            if hasattr(status, "HTTP_404_NOT_FOUND")
            else 404,
            detail="Worker profile not found",
        )

    if not payload.aadhaar_number.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aadhaar number must contain exactly 12 digits",
        )

    # In test mode, accept standard 6-digit OTP ("123456" or any numeric string)
    if not payload.otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP format. OTP must be a 6-digit number",
        )

    profile.aadhaar_number = payload.aadhaar_number
    profile.verification_status = "verified"
    profile.police_verification_status = "verified"
    db.commit()
    db.refresh(profile)

    return AadhaarVerifyOTPResponse(
        status="success",
        message="Aadhaar OTP verified successfully",
        verification_status="verified",
    )


@router.post("/payment/create-order", response_model=PaymentCreateOrderResponse)
def create_kyc_payment_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workers can pay KYC verification fees",
        )

    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == current_user.id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Worker profile not found",
        )

    order_id = f"order_test_{uuid.uuid4().hex[:10]}"
    return PaymentCreateOrderResponse(
        order_id=order_id,
        amount=50000,
        currency="INR",
        status="created",
    )


@router.post("/payment/verify", response_model=PaymentVerifyResponse)
def verify_kyc_payment(
    payload: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "worker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workers can verify KYC payments",
        )

    profile = (
        db.query(WorkerProfile).filter(WorkerProfile.user_id == current_user.id).first()
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Worker profile not found",
        )

    profile.kyc_payment_status = "completed"
    db.commit()
    db.refresh(profile)

    return PaymentVerifyResponse(
        status="success",
        message="KYC payment verified successfully",
        kyc_payment_status="completed",
    )
