import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.seed import seed_data

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db_monkeypatch(monkeypatch):
    monkeypatch.setattr("app.seed.SessionLocal", TestingSessionLocal)
    yield


def login(phone: str, password: str = "password123"):
    response = client.post("/auth/login", json={"phone": phone, "password": password})
    assert response.status_code == 200, f"Login failed for {phone}: {response.text}"
    return response.json()["access_token"]


def test_demo_beat_e2e():
    # Step 1: Start fresh and seed DB
    seed_data()

    # Step 2: Ravi logs in and books electrician at Jaipur center (26.9124, 75.7873)
    ravi_token = login("9555555555")

    booking_payload = {
        "skill": "electrician",
        "lat": 26.9124,
        "lng": 75.7873,
        "description": "Fixing a main circuit board.",
        "job_price": 500,
    }

    response = client.post(
        "/bookings",
        json=booking_payload,
        headers={"Authorization": f"Bearer {ravi_token}"},
    )
    assert response.status_code == 201, response.text
    booking_data = response.json()
    import uuid

    booking_id_str = booking_data["booking_id"]
    booking_id = uuid.UUID(booking_id_str)

    # Extract worker IDs from DB to use in validation
    db = TestingSessionLocal()
    from app.models.user import User

    def get_user_id(phone: str) -> str:
        user = db.query(User).filter(User.phone == phone).first()
        assert user is not None
        return str(user.id)

    get_user_id("9111111111")
    get_user_id("9222222222")
    get_user_id("9333333333")
    meena_id = get_user_id("9444444444")
    db.close()

    # Log in all workers
    suresh_token = login("9111111111")
    priya_token = login("9222222222")
    anil_token = login("9333333333")
    meena_token = login("9444444444")

    # Step 3: Suresh Kumar (rank 1) receives offer -> declines
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {suresh_token}"}
    )
    assert res.status_code == 200
    suresh_offers = res.json()
    assert len(suresh_offers) > 0, "Suresh should have received the first offer"
    suresh_offer_id = suresh_offers[0]["id"]

    res = client.put(
        f"/booking-offers/{suresh_offer_id}",
        json={"action": "decline"},
        headers={"Authorization": f"Bearer {suresh_token}"},
    )
    assert res.status_code == 200, res.text

    # Step 4: Priya Gupta (rank 2) receives offer -> declines
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {priya_token}"}
    )
    priya_offers = res.json()
    assert len(priya_offers) > 0, "Priya should have received the second offer"
    priya_offer_id = priya_offers[0]["id"]
    res = client.put(
        f"/booking-offers/{priya_offer_id}",
        json={"action": "decline"},
        headers={"Authorization": f"Bearer {priya_token}"},
    )
    assert res.status_code == 200, res.text

    # Step 5: Anil Yadav (rank 3) receives offer -> declines
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {anil_token}"}
    )
    anil_offers = res.json()
    assert len(anil_offers) > 0, "Anil should have received the third offer"
    anil_offer_id = anil_offers[0]["id"]
    res = client.put(
        f"/booking-offers/{anil_offer_id}",
        json={"action": "decline"},
        headers={"Authorization": f"Bearer {anil_token}"},
    )
    assert res.status_code == 200, res.text

    # Step 6: Meena Verma (rank 4) receives offer -> accepts
    res = client.get(
        "/booking-offers/worker", headers={"Authorization": f"Bearer {meena_token}"}
    )
    meena_offers = res.json()
    assert len(meena_offers) > 0, "Meena should have received the fourth offer"
    meena_offer_id = meena_offers[0]["id"]
    res = client.put(
        f"/booking-offers/{meena_offer_id}",
        json={"action": "accept"},
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    assert res.status_code == 200, res.text

    # Verify booking is now accepted
    db = TestingSessionLocal()
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    assert booking is not None
    assert booking.status == "assigned"
    assert str(booking.worker_id) == meena_id
    db.close()

    # Step 7: Meena marks job complete
    res = client.put(
        f"/bookings/{booking_id}/complete",
        headers={"Authorization": f"Bearer {meena_token}"},
    )
    assert res.status_code == 200, res.text

    # Step 8: Ravi rates Meena 4 stars
    rating_payload = {"rating": 4, "review": "Great work"}
    res = client.post(
        f"/bookings/{booking_id}/rating",
        json=rating_payload,
        headers={"Authorization": f"Bearer {ravi_token}"},
    )
    assert res.status_code == 200, res.text

    # Admin login for verification steps
    admin_token = login("9000000000")

    # Step 9: Verify `GET /booking-offers/booking/{id}` -> 4 rows with correct ranks and scores
    res = client.get(
        f"/booking-offers/booking/{booking_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200, res.text
    offers_audit = res.json()
    assert len(offers_audit) == 4

    # Step 10: Verify `/welfare-fund/summary`
    res = client.get(
        "/welfare-fund/summary", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200, res.text
    # The new booking was job_price 500, fee is 25.

    # Meena had 4500 before this (4736.84 * 0.95). New job is 500 * 0.95 = 475.
    # Total weekly earnings = 4500 + 475 = 4975.0
    res = client.get(
        f"/wallet/{meena_id}", headers={"Authorization": f"Bearer {meena_token}"}
    )
    assert res.status_code == 200, res.text
    wallet_data = res.json()
    assert float(wallet_data["weekly_earnings"]) == 4975.0


def test_worker_onboarding_kyc_and_dispatch_e2e():
    """Validates the full worker onboarding, Aadhaar KYC verification, Razorpay onboarding payment,

    and subsequent dispatch booking flow end-to-end.
    """
    seed_data()

    # 1. Register a new worker
    worker_reg = {
        "name": "Vikram Singh",
        "phone": "9888877771",
        "password": "password123",
        "role": "worker",
        "skill": "plumber",
        "lat": 26.9124,
        "lng": 75.7873,
    }
    reg_res = client.post("/auth/register", json=worker_reg)
    assert reg_res.status_code == 201, reg_res.text
    vikram_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {vikram_token}"}

    # 2. Aadhaar OTP verification
    otp_res = client.post(
        "/kyc/aadhaar/send-otp",
        json={"aadhaar_number": "999988887777"},
        headers=headers,
    )
    assert otp_res.status_code == 200, otp_res.text

    verify_res = client.post(
        "/kyc/aadhaar/verify-otp",
        json={"aadhaar_number": "999988887777", "otp": "123456"},
        headers=headers,
    )
    assert verify_res.status_code == 200, verify_res.text
    assert verify_res.json()["verification_status"] == "verified"

    # 3. KYC Payment Onboarding
    order_res = client.post("/kyc/payment/create-order", headers=headers)
    assert order_res.status_code == 200, order_res.text
    order_id = order_res.json()["order_id"]

    pay_verify_res = client.post(
        "/kyc/payment/verify",
        json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": "pay_test_98765",
            "razorpay_signature": "sig_test_123",
        },
        headers=headers,
    )
    assert pay_verify_res.status_code == 200, pay_verify_res.text
    assert pay_verify_res.json()["kyc_payment_status"] == "completed"

    # 4. Citizen books a plumber
    ravi_token = login("9555555555")
    booking_res = client.post(
        "/bookings",
        json={
            "skill": "plumber",
            "lat": 26.9124,
            "lng": 75.7873,
            "description": "Fixing leaking bathroom pipe.",
            "job_price": 600,
        },
        headers={"Authorization": f"Bearer {ravi_token}"},
    )
    assert booking_res.status_code == 201, booking_res.text
    booking_id = booking_res.json()["booking_id"]

    # 5. Worker checks offers and accepts
    offers_res = client.get("/booking-offers/worker", headers=headers)
    assert offers_res.status_code == 200, offers_res.text
    offers = offers_res.json()
    assert len(offers) > 0, "Vikram should receive the booking offer"
    offer_id = offers[0]["id"]

    accept_res = client.put(
        f"/booking-offers/{offer_id}",
        json={"action": "accept"},
        headers=headers,
    )
    assert accept_res.status_code == 200, accept_res.text

    # 6. Worker completes booking
    complete_res = client.put(f"/bookings/{booking_id}/complete", headers=headers)
    assert complete_res.status_code == 200, complete_res.text

    # 7. Citizen submits 5-star rating
    rating_res = client.post(
        f"/bookings/{booking_id}/rating",
        json={"rating": 5, "review": "Excellent plumbing repair!"},
        headers={"Authorization": f"Bearer {ravi_token}"},
    )
    assert rating_res.status_code == 200, rating_res.text

    # 8. Verify wallet balance (450 * 0.95 = 427.50)
    db = TestingSessionLocal()
    from app.models.user import User

    user = db.query(User).filter(User.phone == "9888877771").first()
    assert user is not None
    user_id = str(user.id)
    db.close()

    wallet_res = client.get(f"/wallet/{user_id}", headers=headers)
    assert wallet_res.status_code == 200, wallet_res.text
    assert float(wallet_res.json()["weekly_earnings"]) == 427.5
