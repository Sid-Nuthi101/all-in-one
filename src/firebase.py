from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

APPLE_PROVIDER = "apple"
USERS_COLLECTION = "users"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(timestamp: datetime) -> str:
    return timestamp.isoformat()


def upsert_user(
    firestore_client: Any,
    apple_user: Dict[str, Any],
    *,
    now_fn: Optional[Callable[[], datetime]] = None,
) -> Dict[str, Any]:
    if "apple_sub" not in apple_user:
        raise ValueError("apple_user must include apple_sub")

    apple_sub = apple_user["apple_sub"]
    now = (now_fn or _utc_now)()
    existing_doc = (
        firestore_client.collection(USERS_COLLECTION).document(apple_sub).get()
    )
    existing = existing_doc.to_dict() if existing_doc else None

    payload: Dict[str, Any] = {"last_login_at": _isoformat(now)}

    if not existing or "created_at" not in existing:
        payload["created_at"] = _isoformat(now)

    providers = existing.get("providers") if isinstance(existing, dict) else None
    if providers:
        if APPLE_PROVIDER not in providers:
            payload["providers"] = list(providers) + [APPLE_PROVIDER]
    else:
        payload["providers"] = [APPLE_PROVIDER]

    email = apple_user.get("email")
    if email:
        payload["email"] = email

    name = apple_user.get("name")
    if isinstance(name, dict):
        cleaned_name = {k: v for k, v in name.items() if v}
        if cleaned_name:
            payload["name"] = cleaned_name

    doc_ref = firestore_client.collection(USERS_COLLECTION).document(apple_sub)
    doc_ref.set(payload, merge=True)

    result: Dict[str, Any] = {"apple_sub": apple_sub}
    if isinstance(existing, dict):
        result.update(existing)
    result.update(payload)

    return result
