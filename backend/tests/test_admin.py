import uuid

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import create_access_token, hash_password

client = TestClient(app)


@pytest.fixture
def admin_token():
    db = TestingSessionLocal()
    try:
        admin = User(
            name="Admin User",
            phone="9000000000",
            password_hash=hash_password("password123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        token = create_access_token(data={"user_id": str(admin.id), "role": "admin"})
        return token, admin.id
    finally:
        db.close()


@pytest.fixture
def citizen_token():
    db = TestingSessionLocal()
    try:
        citizen = User(
            name="Ravi Citizen",
            phone="9555555555",
            password_hash=hash_password("password123"),
            role="citizen",
        )
        db.add(citizen)
        db.commit()
        db.refresh(citizen)
        token = create_access_token(
            data={"user_id": str(citizen.id), "role": "citizen"}
        )
        return token, citizen.id
    finally:
        db.close()


@pytest.fixture
def test_worker():
    db = TestingSessionLocal()
    try:
        worker = User(
            name="Test Worker",
            phone="9998887776",
            password_hash=hash_password("password123"),
            role="worker",
        )
        db.add(worker)
        db.commit()
        db.refresh(worker)

        profile = WorkerProfile(
            user_id=worker.id,
            skill="electrician",
            lat=26.9125,
            lng=75.7874,
            rating=4.5,
            verification_status="verified",
            availability=True,
        )
        db.add(profile)
        db.commit()
        return worker.id
    finally:
        db.close()


def test_verify_worker_forbidden_for_citizen(citizen_token, test_worker):
    token, _ = citizen_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"verification_status": "pending"}

    response = client.patch(
        f"/admin/workers/{test_worker}/verify", json=payload, headers=headers
    )
    assert response.status_code == 403


def test_verify_worker_success(admin_token, test_worker):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}

    # Set to False
    payload = {"verification_status": "pending"}
    response = client.patch(
        f"/admin/workers/{test_worker}/verify", json=payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["verification_status"] == "pending"

    # Check DB
    db = TestingSessionLocal()
    try:
        profile = db.query(WorkerProfile).filter_by(user_id=test_worker).first()
        assert profile.verification_status == "pending"
    finally:
        db.close()

    # Set back to True
    payload = {"verification_status": "verified"}
    response = client.patch(
        f"/admin/workers/{test_worker}/verify", json=payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["verification_status"] == "verified"

    db = TestingSessionLocal()
    try:
        profile = db.query(WorkerProfile).filter_by(user_id=test_worker).first()
        assert profile.verification_status == "verified"
    finally:
        db.close()


def test_verify_worker_not_found(admin_token):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"verification_status": "pending"}
    fake_id = str(uuid.uuid4())

    response = client.patch(
        f"/admin/workers/{fake_id}/verify", json=payload, headers=headers
    )
    assert response.status_code == 404


def test_unverified_worker_excluded_from_dispatch(admin_token, test_worker):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}

    # Worker is verified initially, should be in pool
    response = client.get("/workers?skill=electrician&lat=26.9124&lng=75.7873")
    assert response.status_code == 200
    workers = response.json()
    assert any(w["worker_id"] == str(test_worker) for w in workers)

    # Unverify worker
    payload = {"verification_status": "pending"}
    client.patch(f"/admin/workers/{test_worker}/verify", json=payload, headers=headers)

    # Worker should not be in pool
    response = client.get("/workers?skill=electrician&lat=26.9124&lng=75.7873")
    assert response.status_code == 200
    workers = response.json()
    assert not any(w["worker_id"] == str(test_worker) for w in workers)


def test_get_admin_workers_pending(admin_token, test_worker):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}

    # First, let's make sure the test_worker is pending
    payload = {"verification_status": "pending"}
    client.patch(f"/admin/workers/{test_worker}/verify", json=payload, headers=headers)

    response = client.get("/admin/workers?status=pending", headers=headers)
    assert response.status_code == 200
    workers = response.json()
    assert isinstance(workers, list)

    # test_worker should be in the pending list
    assert any(w["user_id"] == str(test_worker) for w in workers)
    for w in workers:
        assert w["verification_status"] == "pending"


def test_get_admin_workers_verified(admin_token, test_worker):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}

    # Let's make sure the test_worker is verified
    payload = {"verification_status": "verified"}
    client.patch(f"/admin/workers/{test_worker}/verify", json=payload, headers=headers)

    response = client.get("/admin/workers?status=verified", headers=headers)
    assert response.status_code == 200
    workers = response.json()

    # test_worker should be in the verified list
    assert any(w["user_id"] == str(test_worker) for w in workers)
    for w in workers:
        assert w["verification_status"] == "verified"


def test_get_admin_workers_forbidden(citizen_token):
    token, _ = citizen_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/admin/workers", headers=headers)
    assert response.status_code == 403
