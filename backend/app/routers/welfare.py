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
    DisbursementItem,
    DisbursementRequest,
    DisbursementResponse,
    WelfareFundSummaryResponse,
)

router = APIRouter()

VALID_CATEGORIES = {"insurance", "tool_loan", "training", "emergency", "pension"}


def _get_summary_data(db: Session):
    booking_res = (
        db.query(
            func.coalesce(func.sum(Booking.platform_fee), Decimal("0.00")).label(
                "total_fees"
            ),
            func.count(Booking.id).label("completed_bookings"),
        )
        .filter(Booking.status == "completed")
        .first()
    )
    total_fees = (
        Decimal(str(booking_res.total_fees)) if booking_res else Decimal("0.00")
    )
    completed_bookings = booking_res.completed_bookings if booking_res else 0

    disbursement_sum = db.query(
        func.coalesce(func.sum(WelfareDisbursement.amount), Decimal("0.00")).label(
            "total_disbursed"
        )
    ).scalar()
    total_disbursed = (
        Decimal(str(disbursement_sum))
        if disbursement_sum is not None
        else Decimal("0.00")
    )

    remaining_balance = max(Decimal("0.00"), total_fees - total_disbursed)

    categories_query = (
        db.query(
            WelfareDisbursement.category,
            func.sum(WelfareDisbursement.amount).label("sum_amount"),
        )
        .group_by(WelfareDisbursement.category)
        .all()
    )
    category_breakdown = {cat: Decimal(str(amt)) for cat, amt in categories_query}

    return {
        "total_fees": total_fees,
        "completed_bookings": completed_bookings,
        "total_disbursed": total_disbursed,
        "remaining_balance": remaining_balance,
        "category_breakdown": category_breakdown,
    }


@router.get("/summary", response_model=WelfareFundSummaryResponse)
def get_welfare_summary(db: Session = Depends(get_db)):
    data = _get_summary_data(db)
    return WelfareFundSummaryResponse(**data)


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
            detail="Only admins can record welfare fund disbursements",
        )

    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{payload.category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
        )

    if payload.amount <= Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disbursement amount must be greater than zero",
        )

    summary = _get_summary_data(db)
    if payload.amount > summary["remaining_balance"]:
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

    new_remaining = max(Decimal("0.00"), summary["remaining_balance"] - payload.amount)

    return DisbursementResponse(
        id=disbursement.id,
        amount=disbursement.amount,
        category=disbursement.category,
        description=disbursement.description,
        disbursed_by=disbursement.disbursed_by,
        disbursed_at=disbursement.disbursed_at,
        remaining_fund_balance=new_remaining,
    )


@router.get("/disbursements", response_model=list[DisbursementItem])
def get_welfare_disbursements(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    disbursements = (
        db.query(WelfareDisbursement)
        .order_by(WelfareDisbursement.disbursed_at.desc())
        .limit(limit)
        .all()
    )
    return disbursements
