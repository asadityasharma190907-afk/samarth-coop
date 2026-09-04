from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.models.worker_profile import WorkerProfile

client = TestClient(app)


def test_send_aadhaar_otp_success():
    payload = {"aadhaar_number": "123456789012"}
    response = client.post("/kyc/aadhaar/send-otp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "transaction_id" in data
    assert "OTP sent" in data["message"]


def test_send_aadhaar_otp_invalid_aadhaar():
    payload = {"aadhaar_number": "12345"}  # Not 12 digits
    response = client.post("/kyc/aadhaar/send-otp", json=payload)
    assert response.status_code == 422


def test_verify_aadhaar_otp_success():
    # Register worker first
    reg_payload = {
        "name": "Aadhaar Test Worker",
        "phone": "9777766665",
        "password": "worker123",
        "role": "worker",
        "skill": "electrician",
        "lat": 26.9100,
        "lng": 75.8000,
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    verify_payload = {"aadhaar_number": "123456789012", "otp": "123456"}
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/kyc/aadhaar/verify-otp", json=verify_payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["verification_status"] == "verified"

    # Verify DB state
    db = TestingSessionLocal()
    user = db.query(User).filter(User.phone == "9777766665").first()
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user.id).first()
    assert profile.aadhaar_number == "123456789012"
    assert profile.verification_status == "verified"
    assert profile.police_verification_status == "verified"
    db.close()


def test_verify_aadhaar_otp_unauthorized():
    verify_payload = {"aadhaar_number": "123456789012", "otp": "123456"}
    response = client.post("/kyc/aadhaar/verify-otp", json=verify_payload)
    assert response.status_code == 401


def test_create_kyc_payment_order_success():
    reg_payload = {
        "name": "Payment Test Worker",
        "phone": "9777766664",
        "password": "worker123",
        "role": "worker",
        "skill": "plumber",
        "lat": 26.9100,
        "lng": 75.8000,
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/kyc/payment/create-order", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "order_id" in data
    assert data["amount"] == 50000
    assert data["currency"] == "INR"
    assert data["status"] == "created"


def test_verify_kyc_payment_success():
    reg_payload = {
        "name": "Payment Verify Worker",
        "phone": "9777766663",
        "password": "worker123",
        "role": "worker",
        "skill": "carpenter",
        "lat": 26.9100,
        "lng": 75.8000,
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    verify_payload = {
        "razorpay_order_id": "order_test_12345",
        "razorpay_payment_id": "pay_test_12345",
        "razorpay_signature": "simulated_signature_abc123",
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/kyc/payment/verify", json=verify_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["kyc_payment_status"] == "completed"

    # Verify DB state
    db = TestingSessionLocal()
    user = db.query(User).filter(User.phone == "9777766663").first()
    profile = db.query(WorkerProfile).filter(WorkerProfile.user_id == user.id).first()
    assert profile.kyc_payment_status == "completed"
    db.close()
