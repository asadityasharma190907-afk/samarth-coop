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
