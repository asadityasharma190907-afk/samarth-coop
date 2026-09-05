import io
from uuid import uuid4

from conftest import TestingSessionLocal
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import create_access_token, hash_password

client = TestClient(app)


def setup_test_environment():
    db = TestingSessionLocal()
    try:
        # Create citizen
        citizen = User(
            id=uuid4(),
            phone=f"99{str(uuid4().int)[:8]}",
            password_hash=hash_password("password123"),
            name="Citizen Test",
            role="citizen",
        )
        # Create assigned worker
        worker = User(
            id=uuid4(),
            phone=f"98{str(uuid4().int)[:8]}",
            password_hash=hash_password("password123"),
            name="Worker Test",
            role="worker",
        )
        # Create other worker
        other_worker = User(
            id=uuid4(),
            phone=f"97{str(uuid4().int)[:8]}",
            password_hash=hash_password("password123"),
            name="Other Worker",
            role="worker",
        )
        db.add_all([citizen, worker, other_worker])
        db.commit()
        db.refresh(citizen)
        db.refresh(worker)
        db.refresh(other_worker)

        worker_profile = WorkerProfile(
            user_id=worker.id,
            skill="electrician",
            lat=26.9124,
            lng=75.7873,
            verification_status="verified",
            gender="male",
        )
        other_profile = WorkerProfile(
            user_id=other_worker.id,
            skill="electrician",
            lat=26.9124,
            lng=75.7873,
            verification_status="verified",
            gender="male",
        )
        db.add_all([worker_profile, other_profile])
        db.commit()

        booking = Booking(
            id=uuid4(),
            citizen_id=citizen.id,
            worker_id=worker.id,
            skill="electrician",
            lat=26.9124,
            lng=75.7873,
            job_price=500.0,
            platform_fee=25.0,
            status="assigned",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        worker_token = create_access_token(
            data={"user_id": str(worker.id), "role": "worker"}
        )
        other_worker_token = create_access_token(
            data={"user_id": str(other_worker.id), "role": "worker"}
        )
        citizen_token = create_access_token(
            data={"user_id": str(citizen.id), "role": "citizen"}
        )

        return {
            "citizen_id": citizen.id,
            "citizen_token": citizen_token,
            "worker_id": worker.id,
            "worker_token": worker_token,
            "other_worker_id": other_worker.id,
            "other_worker_token": other_worker_token,
            "booking_id": booking.id,
        }
    finally:
        db.close()


def test_upload_before_and_after_photo_success():
    data = setup_test_environment()
    booking_id = data["booking_id"]
    worker_token = data["worker_token"]

    # 1. Upload before photo as assigned worker
    image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    files = {"file": ("before.png", io.BytesIO(image_content), "image/png")}

    response = client.post(
        f"/bookings/{booking_id}/photos/before",
        files=files,
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["photo_type"] == "before"
    assert "before_photo_url" in res_data
    assert res_data["before_photo_url"].startswith("/uploads/before_")

    # 2. Upload after photo as assigned worker
    files_after = {"file": ("after.png", io.BytesIO(image_content), "image/png")}
    response_after = client.post(
        f"/bookings/{booking_id}/photos/after",
        files=files_after,
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert response_after.status_code == status.HTTP_200_OK
    res_data_after = response_after.json()
    assert res_data_after["photo_type"] == "after"
    assert res_data_after["after_photo_url"].startswith("/uploads/after_")
    assert res_data_after["before_photo_url"] == res_data["before_photo_url"]

    # 3. Verify GET /bookings/{id} returns both photo URLs
    get_res = client.get(
        f"/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert get_res.status_code == status.HTTP_200_OK
    booking_data = get_res.json()
    assert booking_data["before_photo_url"] == res_data["before_photo_url"]
    assert booking_data["after_photo_url"] == res_data_after["after_photo_url"]


def test_upload_photo_forbidden_for_other_worker():
    data = setup_test_environment()
    booking_id = data["booking_id"]
    other_worker_token = data["other_worker_token"]

    image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    files = {"file": ("before.png", io.BytesIO(image_content), "image/png")}

    response = client.post(
        f"/bookings/{booking_id}/photos/before",
        files=files,
        headers={"Authorization": f"Bearer {other_worker_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_upload_photo_invalid_mime_type():
    data = setup_test_environment()
    booking_id = data["booking_id"]
    worker_token = data["worker_token"]

    files = {"file": ("test.txt", io.BytesIO(b"hello world text"), "text/plain")}
    response = client.post(
        f"/bookings/{booking_id}/photos/before",
        files=files,
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid file type" in response.json()["detail"]


def test_upload_photo_not_found():
    data = setup_test_environment()
    worker_token = data["worker_token"]
    fake_id = uuid4()

    image_content = b"\x89PNG\r\n\x1a\n"
    files = {"file": ("before.png", io.BytesIO(image_content), "image/png")}

    response = client.post(
        f"/bookings/{fake_id}/photos/before",
        files=files,
        headers={"Authorization": f"Bearer {worker_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
