import uuid
from decimal import Decimal

from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.user import User

client = TestClient(app)


def test_welfare_summary_empty():
    response = client.get("/welfare-fund/summary")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_fees"]) == 0.0
    assert data["completed_bookings"] == 0


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


def test_welfare_disbursement_model_creation():
    from app.models.welfare_disbursement import WelfareDisbursement

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
