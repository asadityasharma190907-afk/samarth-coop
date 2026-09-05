from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.booking import Booking
from app.models.user import User
from app.models.welfare_disbursement import WelfareDisbursement
from app.schemas.welfare import (
    DisbursementRequest,
    DisbursementResponse,
    WelfareFundSummaryResponse,
)

router = APIRouter()


@router.get("/summary", response_model=WelfareFundSummaryResponse)
def get_welfare_summary(db: Session = Depends(get_db)):
    result = (
        db.query(
            func.coalesce(func.sum(Booking.platform_fee), 0).label("total_fees"),
            func.count(Booking.id).label("completed_bookings"),
        )
        .filter(Booking.status == "completed")
        .first()
    )

    disbursements = db.query(
        func.coalesce(func.sum(WelfareDisbursement.amount), 0).label(
            "total_disbursements"
        )
    ).first()

    total_fees = result.total_fees if result else Decimal("0.00")
    completed_bookings = result.completed_bookings if result else 0
    total_disbursements = (
        disbursements.total_disbursements if disbursements else Decimal("0.00")
    )
    remaining_balance = total_fees - total_disbursements

    return WelfareFundSummaryResponse(
        total_fees=total_fees,
        completed_bookings=completed_bookings,
        total_disbursements=total_disbursements,
        remaining_balance=remaining_balance,
    )


@router.post(
    "/disburse",
    response_model=DisbursementResponse,
    status_code=status.HTTP_201_CREATED,
)
def disburse_welfare_fund(
    payload: DisbursementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can disburse welfare funds",
        )

    # Calculate current balance
    total_fees = db.query(func.coalesce(func.sum(Booking.platform_fee), 0)).filter(
        Booking.status == "completed"
    ).scalar() or Decimal("0.00")
    total_disbursed = db.query(
        func.coalesce(func.sum(WelfareDisbursement.amount), 0)
    ).scalar() or Decimal("0.00")
    current_balance = total_fees - total_disbursed

    if payload.amount > current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient fund balance",
        )

    disbursement = WelfareDisbursement(
        amount=payload.amount,
        category=payload.category,
        description=payload.description,
        disbursed_by=current_user.id,
    )
    db.add(disbursement)
    db.commit()
    db.refresh(disbursement)

    return DisbursementResponse(
        id=disbursement.id,
        amount=disbursement.amount,
        category=disbursement.category,
        description=disbursement.description,
        disbursed_at=disbursement.disbursed_at,
        remaining_fund_balance=current_balance - disbursement.amount,
    )
