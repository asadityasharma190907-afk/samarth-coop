import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from pywebpush import webpush

    PYWEBPUSH_AVAILABLE = True
except ImportError:
    PYWEBPUSH_AVAILABLE = False


def send_push_notification(
    subscription_raw: str | dict[str, Any] | None,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
) -> bool:
    """Sends a Web Push notification payload to a worker's subscription endpoint."""
    if not subscription_raw:
        return False

    if isinstance(subscription_raw, str):
        try:
            subscription_info = json.loads(subscription_raw)
        except Exception:
            logger.warning("Failed to parse push subscription JSON string")
            return False
    else:
        subscription_info = subscription_raw

    endpoint = (
        subscription_info.get("endpoint")
        if isinstance(subscription_info, dict)
        else None
    )
    if not endpoint:
        logger.warning("Push subscription missing endpoint URL")
        return False

    payload = {
        "title": title,
        "body": body,
        "icon": "/icons/icon-192.png",
        "data": data or {},
    }

    if not PYWEBPUSH_AVAILABLE:
        logger.info(f"[Mock Push Notification] Sent '{title}' to {endpoint}")
        return True

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL},
        )
        logger.info(f"Push notification delivered successfully to {endpoint}")
        return True
    except Exception as err:
        logger.error(f"Failed to deliver push notification: {err}")
        return False
