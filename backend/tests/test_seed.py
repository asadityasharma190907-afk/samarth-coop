import pytest
from conftest import TestingSessionLocal

from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.seed import seed_data


@pytest.fixture(autouse=True)
def setup_db_monkeypatch(monkeypatch):
    # Monkeypatch SessionLocal in seed to use TestingSessionLocal from conftest
    monkeypatch.setattr("app.seed.SessionLocal", TestingSessionLocal)
    yield


def test_seed_data_success():
    seed_data()

    db = TestingSessionLocal()
    try:
        # Check users count
        users = db.query(User).all()
        assert len(users) == 7

        citizens = db.query(User).filter(User.role == "citizen").all()
        assert len(citizens) == 2
        citizen_names = {c.name for c in citizens}
        assert citizen_names == {"Ravi Sharma", "Priya Customer"}

        workers = db.query(User).filter(User.role == "worker").all()
        assert len(workers) == 4

        # Check Suresh Kumar
        suresh = db.query(User).filter(User.phone == "9111111111").first()
        assert suresh is not None
        assert suresh.name == "Suresh Kumar"
        suresh_prof = (
            db.query(WorkerProfile).filter(WorkerProfile.user_id == suresh.id).first()
        )
        assert suresh_prof is not None
        assert float(suresh_prof.lat) == 26.9280
        assert float(suresh_prof.lng) == 75.8100
        assert float(suresh_prof.rating) == 4.2
        assert suresh_prof.verified is True
        assert suresh_prof.availability is True

        # Check Priya Gupta (cold start -> rating None)
        priya = db.query(User).filter(User.phone == "9222222222").first()
        assert priya is not None
        priya_prof = (
            db.query(WorkerProfile).filter(WorkerProfile.user_id == priya.id).first()
        )
        assert priya_prof is not None
        assert priya_prof.rating is None
        assert priya_prof.verified is True

        # Check Anil Yadav
        anil = db.query(User).filter(User.phone == "9333333333").first()
        assert anil is not None
        anil_prof = (
            db.query(WorkerProfile).filter(WorkerProfile.user_id == anil.id).first()
        )
        assert anil_prof is not None
        assert float(anil_prof.rating) == 4.5

        # Check Meena Verma
        meena = db.query(User).filter(User.phone == "9444444444").first()
        assert meena is not None
        meena_prof = (
            db.query(WorkerProfile).filter(WorkerProfile.user_id == meena.id).first()
        )
        assert meena_prof is not None
        assert float(meena_prof.rating) == 4.9

        # Check completed bookings
        bookings = db.query(Booking).filter(Booking.status == "completed").all()
        assert len(bookings) == 3

        suresh_b = db.query(Booking).filter(Booking.worker_id == suresh.id).first()
        assert suresh_b is not None
        assert float(suresh_b.job_price) == 210.53

        anil_b = db.query(Booking).filter(Booking.worker_id == anil.id).first()
        assert anil_b is not None
        assert float(anil_b.job_price) == 2105.26

        meena_b = db.query(Booking).filter(Booking.worker_id == meena.id).first()
        assert meena_b is not None
        assert float(meena_b.job_price) == 4736.84
    finally:
        db.close()


def test_seed_data_idempotent():
    # Run seed_data twice to verify idempotency
    seed_data()
    seed_data()

    db = TestingSessionLocal()
    try:
        users = db.query(User).all()
        assert len(users) == 7
        worker_profiles = db.query(WorkerProfile).all()
        assert len(worker_profiles) == 4
        bookings = db.query(Booking).all()
        assert len(bookings) == 3
    finally:
        db.close()
