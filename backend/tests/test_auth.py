from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import verify_password

client = TestClient(app)


def test_register_citizen_success():
    payload = {
        "name": "Ravi Sharma",
        "phone": "9876543210",
        "password": "secure123",
        "role": "citizen",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "citizen"
    assert "user_id" in data

    # Verify user row exists in DB with hashed password
    db = TestingSessionLocal()
    user = db.query(User).filter(User.phone == "9876543210").first()
    assert user is not None
    assert user.name == "Ravi Sharma"
    assert user.role == "citizen"
    assert user.password_hash != "secure123"
    assert verify_password("secure123", user.password_hash) is True
    db.close()


def test_register_duplicate_phone_conflict():
    payload = {
        "name": "Ravi Sharma",
        "phone": "9876543210",
        "password": "secure123",
        "role": "citizen",
    }
    # First registration
    response1 = client.post("/auth/register", json=payload)
    assert response1.status_code == 201

    # Second registration with same phone
    response2 = client.post("/auth/register", json=payload)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Phone number already registered"


def test_register_missing_fields_validation_error():
    payload = {"name": "Ravi Sharma"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_register_worker_success():
    payload = {
        "name": "Suresh Kumar",
        "phone": "9111111111",
        "password": "worker123",
        "role": "worker",
        "skill": "electrician",
        "lat": 26.9280,
        "lng": 75.8100,
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "worker"

    db = TestingSessionLocal()
    user = db.query(User).filter(User.phone == "9111111111").first()
    assert user is not None
    assert user.role == "worker"

    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user.id).first()
    assert profile is not None
    assert profile.skill == "electrician"
    assert profile.verification_status == "pending"
    assert profile.availability is True
    assert profile.rating is None
    db.close()


def test_register_worker_invalid_skill():
    payload = {
        "name": "Suresh Kumar",
        "phone": "9111111112",
        "password": "worker123",
        "role": "worker",
        "skill": "hacker",  # invalid
        "lat": 26.9280,
        "lng": 75.8100,
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success():
    # Register a user first
    register_payload = {
        "name": "Login Test User",
        "phone": "9000000000",
        "password": "password123",
        "role": "citizen",
    }
    client.post("/auth/register", json=register_payload)

    # Now login
    login_payload = {"phone": "9000000000", "password": "password123"}
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "citizen"
    assert "user_id" in data


def test_login_wrong_password():
    register_payload = {
        "name": "Login Test User 2",
        "phone": "9000000001",
        "password": "password123",
        "role": "citizen",
    }
    client.post("/auth/register", json=register_payload)

    login_payload = {"phone": "9000000001", "password": "wrongpassword"}
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect phone number or password"


def test_login_unregistered_phone():
    login_payload = {"phone": "9999999999", "password": "password123"}
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect phone number or password"


def test_login_missing_fields():
    login_payload = {"phone": "9000000000"}
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 422


# Dummy protected route for testing dependencies
from fastapi import Depends

from app.dependencies import get_current_user


@app.get("/test-protected")
def dummy_protected_route(user: User = Depends(get_current_user)):
    return {"user_id": str(user.id), "phone": user.phone}


def test_protected_route_success():
    # Register and login to get token
    register_payload = {
        "name": "Protected Test User",
        "phone": "9000000002",
        "password": "password123",
        "role": "citizen",
    }
    client.post("/auth/register", json=register_payload)

    login_response = client.post(
        "/auth/login", json={"phone": "9000000002", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Access protected route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/test-protected", headers=headers)
    assert response.status_code == 200
    assert response.json()["phone"] == "9000000002"


def test_protected_route_invalid_token():
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/test-protected", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_register_worker_out_of_bounds_coords():
    payload = {
        "name": "Suresh Kumar",
        "phone": "9111111115",
        "password": "worker123",
        "role": "worker",
        "skill": "electrician",
        "lat": 95.0,  # Invalid latitude > 90
        "lng": 75.8100,
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422

    payload["lat"] = 26.9280
    payload["lng"] = 185.0  # Invalid longitude > 180
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
