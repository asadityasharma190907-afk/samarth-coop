from datetime import datetime, timedelta, timezone

import pytest
from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.seed import seed_data
from app.services.dispatch_v2 import get_ranked_workers_adaptive

client = TestClient(app)

_LAT = 26.9124
_LNG = 75.7873


@pytest.fixture(autouse=True)
def setup_db_monkeypatch(monkeypatch):
    monkeypatch.setattr("app.seed.SessionLocal", TestingSessionLocal)
    yield


def _create_worker(
    db,
    name: str,
    phone: str,
    skill: str,
    lat: float,
    lng: float,
    last_active_at: datetime | None = None,
):
    user = User(name=name, phone=phone, password_hash="fakehash", role="worker")
    db.add(user)
    db.flush()

    profile = WorkerProfile(
        user_id=user.id,
        skill=skill,
        lat=lat,
        lng=lng,
        verification_status="verified",
        availability=True,
        last_active_at=last_active_at,
    )
    db.add(profile)
    db.commit()
    return user, profile


def test_seed_workers_ranking_preserved():
    """Verify that seed data ranks Suresh > Priya > Anil > Meena with dispatch_v2."""
    seed_data()
    db = TestingSessionLocal()
    try:
        workers = get_ranked_workers_adaptive("electrician", _LAT, _LNG, db)
        names = [w["name"] for w in workers]
        assert names == ["Suresh Kumar", "Priya Gupta", "Anil Yadav", "Meena Verma"]
        assert workers[0]["wave_used"] == 2  # 5km radius covers all 4
        assert workers[0]["effective_radius_km"] == 5.0
    finally:
        db.close()


def test_adaptive_dispatch_sparse_area_wave_expansion():
    """In a sparse area (only 1 worker at 7km), Wave 3 (8km) finds them."""
    db = TestingSessionLocal()
    try:
        # Worker at ~7.2 km away from Jaipur center (26.9124, 75.7873 -> 26.97, 75.82)
        _create_worker(db, "Sparse Plumber", "9998887771", "plumber", 26.97, 75.82)

        workers = get_ranked_workers_adaptive("plumber", _LAT, _LNG, db)
        assert len(workers) == 1
        assert workers[0]["name"] == "Sparse Plumber"
        assert workers[0]["wave_used"] == 3
        assert workers[0]["effective_radius_km"] == 8.0
    finally:
        db.close()


def test_adaptive_dispatch_dense_area_wave_1_stops():
    """In a dense area (4 workers within 2km), Wave 1 (3km) stops immediately."""
    db = TestingSessionLocal()
    try:
        for i in range(4):
            _create_worker(
                db,
                f"Dense Painter {i}",
                f"999111222{i}",
                "painter",
                _LAT + (i * 0.005),  # ~0.5km step
                _LNG + (i * 0.005),
            )

        workers = get_ranked_workers_adaptive("painter", _LAT, _LNG, db)
        assert len(workers) == 4
        assert workers[0]["wave_used"] == 1
        assert workers[0]["effective_radius_km"] == 3.0
    finally:
        db.close()


def test_availability_bonus_boosting_rank():
    """Worker who pinged within 5 min gets +200 bonus and ranks higher."""
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    try:
        # Worker A: no ping, same distance
        _create_worker(
            db, "Worker Quiet", "9990001111", "cleaner", _LAT + 0.01, _LNG + 0.01
        )
        # Worker B: pinged 2 minutes ago
        _create_worker(
            db,
            "Worker Active",
            "9990002222",
            "cleaner",
            _LAT + 0.01,
            _LNG + 0.01,
            last_active_at=now - timedelta(minutes=2),
        )

        workers = get_ranked_workers_adaptive("cleaner", _LAT, _LNG, db, now=now)
        assert len(workers) == 2
        assert workers[0]["name"] == "Worker Active"
        assert workers[0]["availability_bonus_applied"] is True
        assert workers[1]["name"] == "Worker Quiet"
        assert workers[1]["availability_bonus_applied"] is False
    finally:
        db.close()


def test_worker_ping_endpoint_success():
    seed_data()
    # Login Suresh Kumar (worker)
    res = client.post(
        "/auth/login", json={"phone": "9111111111", "password": "password123"}
    )
    assert res.status_code == 200
    token = res.json()["access_token"]

    ping_res = client.post(
        "/workers/me/ping", headers={"Authorization": f"Bearer {token}"}
    )
    assert ping_res.status_code == 200, ping_res.text
    data = ping_res.json()
    assert "last_active_at" in data
    assert data["availability_bonus_eligible"] is True


def test_worker_ping_forbidden_for_citizen():
    seed_data()
    # Login Ravi Sharma (citizen)
    res = client.post(
        "/auth/login", json={"phone": "9555555555", "password": "password123"}
    )
    assert res.status_code == 200
    token = res.json()["access_token"]

    ping_res = client.post(
        "/workers/me/ping", headers={"Authorization": f"Bearer {token}"}
    )
    assert ping_res.status_code == 403


def test_worker_ping_unauthenticated():
    ping_res = client.post("/workers/me/ping")
    assert ping_res.status_code == 401
