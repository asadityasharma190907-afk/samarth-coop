import uuid
from decimal import Decimal

from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.user import User
from app.models.welfare_disbursement import WelfareDisbursement
from app.services.auth import create_access_token, hash_password

client = TestClient(app)


def test_welfare_summary_empty():
    response = client.get("/welfare-fund/summary")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_fees"]) == 0.0
    assert data["completed_bookings"] == 0
    assert float(data["total_disbursed"]) == 0.0
    assert float(data["remaining_balance"]) == 0.0


def test_welfare_summary_with_bookings():
    db = TestingSessionLocal()
    try:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            phone="9999999999",
            name="Test Citizen",
            password_hash="hash",
            role="citizen",
        )
        db.add(user)
        db.commit()

        # Add 2 completed bookings and 1 cancelled booking
        b1 = Booking(
            citizen_id=user_id,
            skill="plumber",
            status="completed",
            job_price=Decimal("100.00"),
            platform_fee=Decimal("5.00"),
            lat=26.0,
            lng=75.0,
        )
        b2 = Booking(
            citizen_id=user_id,
            skill="electrician",
            status="completed",
            job_price=Decimal("200.00"),
            platform_fee=Decimal("10.00"),
            lat=26.0,
            lng=75.0,
        )
        b3 = Booking(
            citizen_id=user_id,
            skill="plumber",
            status="cancelled",
            job_price=Decimal("50.00"),
            platform_fee=Decimal("2.50"),
            lat=26.0,
            lng=75.0,
        )
        db.add_all([b1, b2, b3])
        db.commit()
    finally:
        db.close()

    response = client.get("/welfare-fund/summary")
    assert response.status_code == 200
    data = response.json()

    # 5.00 + 10.00 = 15.00 (from 2 completed bookings)
    assert float(data["total_fees"]) == 15.0
    assert data["completed_bookings"] == 2
    assert float(data["remaining_balance"]) == 15.0


def test_welfare_disbursement_model_creation():
    db = TestingSessionLocal()
    try:
        admin_id = uuid.uuid4()
        admin_user = User(
            id=admin_id,
            phone="9888888888",
            name="Admin User",
            password_hash="hash",
            role="admin",
        )
        db.add(admin_user)
        db.commit()

        disbursement = WelfareDisbursement(
            amount=Decimal("5000.00"),
            category="insurance",
            description="Group health insurance premium allocation",
            disbursed_by=admin_id,
        )
        db.add(disbursement)
        db.commit()
        db.refresh(disbursement)

        assert disbursement.id is not None
        assert disbursement.amount == Decimal("5000.00")
        assert disbursement.category == "insurance"
        assert disbursement.description == "Group health insurance premium allocation"
        assert disbursement.disbursed_by == admin_id
        assert disbursement.disbursed_at is not None

        # Query back from DB
        fetched = db.query(WelfareDisbursement).filter_by(category="insurance").first()
        assert fetched is not None
        assert fetched.id == disbursement.id
    finally:
        db.close()


def test_disburse_welfare_fund_forbidden_for_citizen():
    db = TestingSessionLocal()
    try:
        citizen = User(
            name="Normal Citizen",
            phone="9111111111",
            password_hash=hash_password("pass"),
            role="citizen",
        )
        db.add(citizen)
        db.commit()
        db.refresh(citizen)
        token = create_access_token(
            data={"user_id": str(citizen.id), "role": "citizen"}
        )
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "amount": 100.0,
        "category": "insurance",
        "description": "Test disbursement",
    }
    response = client.post("/welfare-fund/disburse", json=payload, headers=headers)
    assert response.status_code == 403


def test_disburse_welfare_fund_invalid_category_and_insufficient_balance():
    db = TestingSessionLocal()
    try:
        admin = User(
            name="Welfare Admin",
            phone="9222222222",
            password_hash=hash_password("pass"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        token = create_access_token(data={"user_id": str(admin.id), "role": "admin"})

        # Add completed booking to generate balance of 100.00
        booking = Booking(
            citizen_id=admin.id,
            skill="electrician",
            status="completed",
            job_price=Decimal("2000.00"),
            platform_fee=Decimal("100.00"),
            lat=26.0,
            lng=75.0,
        )
        db.add(booking)
        db.commit()
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    # Invalid category test
    payload_invalid = {
        "amount": 50.0,
        "category": "party_fund",
        "description": "Invalid category",
    }
    res_inv = client.post(
        "/welfare-fund/disburse", json=payload_invalid, headers=headers
    )
    assert res_inv.status_code == 400

    # Insufficient balance test (150 > 100)
    payload_exceed = {
        "amount": 150.0,
        "category": "insurance",
        "description": "Exceeds balance",
    }
    res_exc = client.post(
        "/welfare-fund/disburse", json=payload_exceed, headers=headers
    )
    assert res_exc.status_code == 400
    assert res_exc.json()["detail"] == "Insufficient fund balance"


def test_disburse_welfare_fund_success_and_history():
    db = TestingSessionLocal()
    try:
        admin = User(
            name="Chief Admin",
            phone="9333333333",
            password_hash=hash_password("pass"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        token = create_access_token(data={"user_id": str(admin.id), "role": "admin"})

        # Add completed booking with platform fee 500.00
        booking = Booking(
            citizen_id=admin.id,
            skill="plumber",
            status="completed",
            job_price=Decimal("10000.00"),
            platform_fee=Decimal("500.00"),
            lat=26.0,
            lng=75.0,
        )
        db.add(booking)
        db.commit()
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    # Disburse 200.00 for insurance
    payload = {
        "amount": 200.0,
        "category": "insurance",
        "description": "Group health insurance premium",
    }
    res = client.post("/welfare-fund/disburse", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert float(data["amount"]) == 200.0
    assert data["category"] == "insurance"
    assert float(data["remaining_fund_balance"]) == 300.0

    # Verify summary
    res_sum = client.get("/welfare-fund/summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert float(sum_data["total_fees"]) == 500.0
    assert float(sum_data["total_disbursed"]) == 200.0
    assert float(sum_data["remaining_balance"]) == 300.0
    assert float(sum_data["category_breakdown"]["insurance"]) == 200.0

    # Verify disbursements history endpoint
    res_hist = client.get("/welfare-fund/disbursements")
    assert res_hist.status_code == 200
    hist_data = res_hist.json()
    assert len(hist_data) >= 1
    assert hist_data[0]["category"] == "insurance"
    assert float(hist_data[0]["amount"]) == 200.0
