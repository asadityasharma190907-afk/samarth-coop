from decimal import Decimal

from conftest import TestingSessionLocal

from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import hash_password


def test_worker_profile_kyc_fields_defaults():
    db = TestingSessionLocal()
    try:
        user = User(
            name="Test KYC Worker",
            phone="9999912345",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add(user)
        db.flush()

        profile = WorkerProfile(
            user_id=user.id,
            skill="plumber",
            lat=Decimal("26.9000"),
            lng=Decimal("75.8000"),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        # Verify default values
        assert profile.police_verification_status == "pending"
        assert profile.kyc_payment_status == "pending"
        assert profile.father_name is None
        assert profile.date_of_birth is None
        assert profile.aadhaar_number is None
    finally:
        db.close()


def test_worker_profile_kyc_fields_population():
    db = TestingSessionLocal()
    try:
        user = User(
            name="Test Full KYC Worker",
            phone="9999954321",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add(user)
        db.flush()

        profile = WorkerProfile(
            user_id=user.id,
            skill="electrician",
            lat=Decimal("26.9100"),
            lng=Decimal("75.8100"),
            father_name="Vikram Singh",
            date_of_birth="1991-07-12",
            domicile="Rajasthan",
            local_address="12 Main St, Jaipur",
            marital_status="married",
            experience_years=7,
            languages_spoken="Hindi, English",
            aadhaar_number="987654321012",
            police_verification_status="verified",
            kyc_payment_status="completed",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        assert profile.father_name == "Vikram Singh"
        assert profile.date_of_birth == "1991-07-12"
        assert profile.domicile == "Rajasthan"
        assert profile.local_address == "12 Main St, Jaipur"
        assert profile.marital_status == "married"
        assert profile.experience_years == 7
        assert profile.languages_spoken == "Hindi, English"
        assert profile.aadhaar_number == "987654321012"
        assert profile.police_verification_status == "verified"
        assert profile.kyc_payment_status == "completed"
    finally:
        db.close()
