from decimal import Decimal

from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile

client = TestClient(app)


def test_get_workers_api_success():
    db = TestingSessionLocal()
    try:
        # Seed 2 Citizens
        ravi = User(
            name="Ravi Sharma", phone="9555555555", password_hash="hash", role="citizen"
        )
        priya_customer = User(
            name="Priya Customer",
            phone="9666666666",
            password_hash="hash",
            role="citizen",
        )
        db.add_all([ravi, priya_customer])
        db.flush()

        # Seed 4 Workers
        # Suresh Kumar (Expected Rank: 1st)
        suresh_u = User(
            name="Suresh Kumar", phone="9111111111", password_hash="hash", role="worker"
        )
        db.add(suresh_u)
        db.flush()
        suresh_p = WorkerProfile(
            user_id=suresh_u.id,
            skill="electrician",
            lat=Decimal("26.9280"),
            lng=Decimal("75.8100"),
            rating=Decimal("4.2"),
            availability=True,
            verification_status="verified",
        )
        db.add(suresh_p)

        # Priya Gupta (Expected Rank: 2nd)
        priya_u = User(
            name="Priya Gupta", phone="9222222222", password_hash="hash", role="worker"
        )
        db.add(priya_u)
        db.flush()
        priya_p = WorkerProfile(
            user_id=priya_u.id,
            skill="electrician",
            lat=Decimal("26.8800"),
            lng=Decimal("75.7600"),
            rating=None,
            availability=True,
            verification_status="verified",
        )
        db.add(priya_p)

        # Anil Yadav (Expected Rank: 3rd)
        anil_u = User(
            name="Anil Yadav", phone="9333333333", password_hash="hash", role="worker"
        )
        db.add(anil_u)
        db.flush()
        anil_p = WorkerProfile(
            user_id=anil_u.id,
            skill="electrician",
            lat=Decimal("26.9200"),
            lng=Decimal("75.8000"),
            rating=Decimal("4.5"),
            availability=True,
            verification_status="verified",
        )
        db.add(anil_p)

        # Meena Verma (Expected Rank: 4th)
        meena_u = User(
            name="Meena Verma", phone="9444444444", password_hash="hash", role="worker"
        )
        db.add(meena_u)
        db.flush()
        meena_p = WorkerProfile(
            user_id=meena_u.id,
            skill="electrician",
            lat=Decimal("26.9130"),
            lng=Decimal("75.7880"),
            rating=Decimal("4.9"),
            availability=True,
            verification_status="verified",
        )
        db.add(meena_p)
        db.flush()

        # Seed Bookings for earnings
        # Suresh: ₹200 earnings -> job_price = 210.53
        b_suresh = Booking(
            citizen_id=ravi.id,
            worker_id=suresh_u.id,
            skill="electrician",
            lat=Decimal("26.9280"),
            lng=Decimal("75.8100"),
            job_price=Decimal("210.53"),
            status="completed",
        )
        # Anil: ₹2,000 earnings -> job_price = 2105.26
        b_anil = Booking(
            citizen_id=ravi.id,
            worker_id=anil_u.id,
            skill="electrician",
            lat=Decimal("26.9200"),
            lng=Decimal("75.8000"),
            job_price=Decimal("2105.26"),
            status="completed",
        )
        # Meena: ₹4,500 earnings -> job_price = 4736.84
        b_meena = Booking(
            citizen_id=priya_customer.id,
            worker_id=meena_u.id,
            skill="electrician",
            lat=Decimal("26.9130"),
            lng=Decimal("75.7880"),
            job_price=Decimal("4736.84"),
            status="completed",
        )
        db.add_all([b_suresh, b_anil, b_meena])
        db.commit()
    finally:
        db.close()

    # Call endpoint
    response = client.get("/workers?skill=electrician&lat=26.9124&lng=75.7873")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4

    # Assert exact order
    assert data[0]["name"] == "Suresh Kumar"
    assert data[1]["name"] == "Priya Gupta"
    assert data[2]["name"] == "Anil Yadav"
    assert data[3]["name"] == "Meena Verma"

    # Assert fields are present
    first = data[0]
    assert "worker_id" in first
    assert "name" in first
    assert "phone" in first
    assert "skill" in first
    assert "lat" in first
    assert "lng" in first
    assert "rating" in first
    assert "distance_km" in first
    assert "weekly_earnings" in first
    assert "dispatch_score" in first
    assert "rating_is_default" in first
    assert "reliability_penalty_applied" in first


def test_get_workers_api_missing_params():
    response = client.get("/workers?skill=electrician")
    assert response.status_code == 422
