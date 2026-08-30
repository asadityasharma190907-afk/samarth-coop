import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.services.auth import verify_password

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_citizen_success():
    payload = {
        "name": "Ravi Sharma",
        "phone": "9876543210",
        "password": "secure123",
        "role": "citizen"
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
        "role": "citizen"
    }
    # First registration
    response1 = client.post("/auth/register", json=payload)
    assert response1.status_code == 201

    # Second registration with same phone
    response2 = client.post("/auth/register", json=payload)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Phone number already registered"


def test_register_missing_fields_validation_error():
    payload = {
        "name": "Ravi Sharma"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422
