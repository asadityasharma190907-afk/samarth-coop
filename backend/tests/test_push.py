import json

from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.worker_profile import WorkerProfile
from app.services.push import send_push_notification

client = TestClient(app)


def test_get_vapid_public_key():
    response = client.get("/push/vapid-public-key")
    assert response.status_code == 200
    data = response.json()
    assert "public_key" in data
    assert len(data["public_key"]) > 0


def test_subscribe_push_as_worker():
    # Register worker
    res = client.post(
        "/auth/register",
        json={
            "name": "Push Worker",
            "phone": "9998887771",
            "password": "secure123",
            "role": "worker",
            "skill": "electrician",
            "lat": 26.9124,
            "lng": 75.7873,
        },
    )
    assert res.status_code == 201
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sub_data = {
        "subscription": {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-token-123",
            "keys": {"p256dh": "test-p256dh-key", "auth": "test-auth-key"},
        }
    }
    sub_res = client.post("/push/subscribe", json=sub_data, headers=headers)
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "subscribed"

    db = TestingSessionLocal()
    try:
        profile = db.query(WorkerProfile).first()
        assert profile is not None
        assert profile.push_subscription is not None
        stored_sub = json.loads(profile.push_subscription)
        assert (
            stored_sub["endpoint"]
            == "https://fcm.googleapis.com/fcm/send/test-token-123"
        )
    finally:
        db.close()


def test_subscribe_push_as_citizen_denied():
    # Register citizen
    res = client.post(
        "/auth/register",
        json={
            "name": "Push Citizen",
            "phone": "9998887772",
            "password": "secure123",
            "role": "citizen",
        },
    )
    assert res.status_code == 201
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sub_data = {
        "subscription": {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-token-456",
            "keys": {"p256dh": "key", "auth": "auth"},
        }
    }
    sub_res = client.post("/push/subscribe", json=sub_data, headers=headers)
    assert sub_res.status_code == 403


def test_send_push_notification_service():
    sub_info = {
        "endpoint": "https://updates.push.services.mozilla.com/wpush/v2/test-endpoint",
        "keys": {"p256dh": "test-p256dh", "auth": "test-auth"},
    }

    # Test with string JSON
    result = send_push_notification(
        subscription_raw=json.dumps(sub_info),
        title="Samarth -- Test Offer",
        body="Test job alert body",
        data={"url": "/worker/offers"},
    )
    assert result is True

    # Test with empty subscription
    assert send_push_notification(None, "Title", "Body") is False
