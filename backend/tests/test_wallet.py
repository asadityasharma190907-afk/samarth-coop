import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import create_access_token

client = TestClient(app)


def test_wallet_empty():
    db = TestingSessionLocal()
    try:
        worker_id = uuid.uuid4()
        worker = User(
            id=worker_id,
            name="Wallet Test",
            phone="1111111111",
            password_hash="fake",
            role="worker",
        )
        db.add(worker)
        profile = WorkerProfile(
            user_id=worker_id,
            skill="electrician",
            lat=26.0,
            lng=75.0,
            verified=True,
            availability=True,
        )
        db.add(profile)
        db.commit()
    finally:
        db.close()

    token = create_access_token(data={"user_id": str(worker_id), "role": "worker"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/wallet/{worker_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["weekly_earnings"]) == 0.0
    assert float(data["lifetime_earnings"]) == 0.0
    assert data["entries"] == []


def test_wallet_forbidden():
    db = TestingSessionLocal()
    try:
        citizen_id = uuid.uuid4()
        citizen = User(
            id=citizen_id, name="Cit", phone="333", password_hash="f", role="citizen"
        )
        db.add(citizen)

        worker2_id = uuid.uuid4()
        worker2 = User(
            id=worker2_id, name="W2", phone="444", password_hash="f", role="worker"
        )
        db.add(worker2)
        profile2 = WorkerProfile(
            user_id=worker2_id,
            skill="plumber",
            lat=26.0,
            lng=75.0,
            verified=True,
            availability=True,
        )
        db.add(profile2)

        db.commit()
    finally:
        db.close()

    token = create_access_token(data={"user_id": str(citizen_id), "role": "citizen"})
    headers = {"Authorization": f"Bearer {token}"}

    # Citizen trying to access wallet
    response = client.get(f"/wallet/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 403

    # Worker trying to access someone else's wallet
    token2 = create_access_token(data={"user_id": str(worker2_id), "role": "worker"})
    headers2 = {"Authorization": f"Bearer {token2}"}
    response2 = client.get(f"/wallet/{uuid.uuid4()}", headers=headers2)
    assert response2.status_code == 403


def test_wallet_with_earnings():
    db = TestingSessionLocal()
    try:
        worker_id = uuid.uuid4()
        worker = User(
            id=worker_id,
            name="Rich Worker",
            phone="2222222222",
            password_hash="fake",
            role="worker",
        )
        db.add(worker)
        profile = WorkerProfile(
            user_id=worker_id,
            skill="plumber",
            lat=26.0,
            lng=75.0,
            verified=True,
            availability=True,
        )
        db.add(profile)
        db.commit()

        # Add a completed booking
        booking1 = Booking(
            id=uuid.uuid4(),
            citizen_id=uuid.uuid4(),
            worker_id=worker_id,
            skill="plumber",
            lat=26.0,
            lng=75.0,
            status="completed",
            job_price=Decimal("1000.00"),
            platform_fee=Decimal("50.00"),
            created_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.add(booking1)

        # Add an old completed booking (from 2 weeks ago) - will count towards lifetime but not weekly
        booking2 = Booking(
            id=uuid.uuid4(),
            citizen_id=uuid.uuid4(),
            worker_id=worker_id,
            skill="plumber",
            lat=26.0,
            lng=75.0,
            status="completed",
            job_price=Decimal("500.00"),
            platform_fee=Decimal("25.00"),
            created_at=datetime.now(timezone.utc) - timedelta(days=14),
        )
        db.add(booking2)
        db.commit()
    finally:
        db.close()

    token = create_access_token(data={"user_id": str(worker_id), "role": "worker"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/wallet/{worker_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # weekly: 1000 * 0.95 = 950
    assert float(data["weekly_earnings"]) == 950.0

    # lifetime: 950 + (500 - 25) = 950 + 475 = 1425
    assert float(data["lifetime_earnings"]) == 1425.0

    assert len(data["entries"]) == 2

    # Latest first
    assert float(data["entries"][0]["job_price"]) == 1000.0
    assert float(data["entries"][0]["worker_payout"]) == 950.0
    assert float(data["entries"][1]["job_price"]) == 500.0
    assert float(data["entries"][1]["worker_payout"]) == 475.0
