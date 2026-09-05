from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.dispatch import (
    compute_reliability_penalty,
    compute_weekly_earnings,
    haversine_km,
)

WAVE_RADII = [3.0, 5.0, 8.0, 12.0]
MIN_CANDIDATES = 4


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _is_worker_active(profile: WorkerProfile, now: datetime) -> bool:
    """Return True if worker has pinged recently or if last_active_at is NULL (grace period)."""
    if profile.last_active_at is None:
        return True
    delta = (_ensure_utc(now) - _ensure_utc(profile.last_active_at)).total_seconds()
    return delta <= 900  # active if pinged within 15 minutes


def _has_availability_bonus(profile: WorkerProfile, now: datetime) -> bool:
    """Return True if worker has sent a heartbeat within the last 5 minutes (300s)."""
    if profile.last_active_at is None:
        return False
    delta = (_ensure_utc(now) - _ensure_utc(profile.last_active_at)).total_seconds()
    return delta <= 300


def get_ranked_workers_adaptive(
    skill: str,
    lat: float,
    lng: float,
    db: Session,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    """Adaptive Radius Dispatch Engine (v2).

    Expands search waves (3km -> 5km -> 8km -> 12km) until MIN_CANDIDATES are found.
    Returns a list of worker dicts including effective_radius_km and wave_used.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    normalized_skill = skill.lower().strip()

    # Query all verified & available workers for skill
    query = (
        db.query(WorkerProfile, User.name, User.phone)
        .join(User, WorkerProfile.user_id == User.id)
        .filter(
            WorkerProfile.verification_status == "verified",
            WorkerProfile.availability == True,
        )
    )

    all_profiles = query.all()
    filtered_by_skill = [
        (p, name, phone)
        for p, name, phone in all_profiles
        if p.skill.lower().strip() == normalized_skill and _is_worker_active(p, now)
    ]

    selected_wave_idx = 0
    selected_radius = WAVE_RADII[0]
    candidates: list[tuple[WorkerProfile, str, str, float]] = []

    for wave_idx, radius in enumerate(WAVE_RADII):
        wave_candidates = []
        for profile, name, phone in filtered_by_skill:
            dist = haversine_km(lat, lng, float(profile.lat), float(profile.lng))
            if dist <= radius:
                wave_candidates.append((profile, name, phone, dist))

        if len(wave_candidates) > len(candidates):
            candidates = wave_candidates
            selected_wave_idx = wave_idx
            selected_radius = radius

        if len(candidates) >= MIN_CANDIDATES:
            break

    ranked_workers = []
    for profile, name, phone, dist in candidates:
        weekly_earnings = compute_weekly_earnings(profile.user_id, db)
        rating_is_default = profile.rating is None
        rating_val = float(profile.rating) if profile.rating is not None else 4.0
        reliability_penalty = compute_reliability_penalty(profile.user_id, db)

        has_bonus = _has_availability_bonus(profile, now)
        availability_bonus = 200.0 if has_bonus else 0.0

        radius_penalty = 300.0 * max(0.0, dist - 3.0)

        # Score_v2 formula
        score = (
            (5000.0 - float(weekly_earnings)) * 2.0
            + (1000.0 * rating_val)
            - (500.0 * dist)
            - float(reliability_penalty)
            + availability_bonus
            - radius_penalty
        )

        ranked_workers.append(
            {
                "worker_id": profile.user_id,
                "name": name,
                "phone": phone,
                "skill": profile.skill,
                "lat": profile.lat,
                "lng": profile.lng,
                "rating": profile.rating,
                "distance_km": round(dist, 2),
                "weekly_earnings": Decimal(str(weekly_earnings)),
                "dispatch_score": Decimal(str(round(score, 2))),
                "rating_is_default": rating_is_default,
                "reliability_penalty_applied": reliability_penalty > 0,
                "availability_bonus_applied": has_bonus,
                "effective_radius_km": selected_radius,
                "wave_used": selected_wave_idx + 1,
            }
        )

    # Sort candidates by dispatch_score descending
    ranked_workers.sort(key=lambda w: w["dispatch_score"], reverse=True)
    return ranked_workers
