from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Sequence

from agent_train import ModelMetadata, UserModelState

APPLE_PROVIDER = "apple"
USERS_COLLECTION = "users"
USER_MODEL_STATE_COLLECTION = "user_model_states"
USER_MODEL_METADATA_COLLECTION = "user_model_metadata"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(timestamp: datetime) -> str:
    return timestamp.isoformat()


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return None


def _serialize_datetime(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return _isoformat(value)


def _serialize_training_range(
    value: Optional[Sequence[datetime]],
) -> Optional[Dict[str, Optional[str]]]:
    if not value:
        return None
    start, end = value
    return {"start": _serialize_datetime(start), "end": _serialize_datetime(end)}


def _parse_training_range(value: Any) -> Optional[tuple[datetime, datetime]]:
    if not isinstance(value, dict):
        return None
    start = _parse_datetime(value.get("start"))
    end = _parse_datetime(value.get("end"))
    if start and end:
        return (start, end)
    return None


def upsert_user(
    firestore_client: Any,
    apple_user: Dict[str, Any],
    *,
    now_fn: Optional[Callable[[], datetime]] = None,
    on_first_login: Optional[Callable[[str], None]] = None,
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
    is_first_login = not existing or "created_at" not in existing

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

    if is_first_login and on_first_login is not None:
        on_first_login(apple_sub)

    result: Dict[str, Any] = {"apple_sub": apple_sub}
    if isinstance(existing, dict):
        result.update(existing)
    result.update(payload)

    return result


class FirestoreMetadataStore:
    def __init__(self, firestore_client: Any) -> None:
        self._client = firestore_client

    def get_user_state(self, user_id: str) -> UserModelState:
        snapshot = (
            self._client.collection(USER_MODEL_STATE_COLLECTION).document(user_id).get()
        )
        data = snapshot.to_dict() if snapshot else None
        if not data:
            return UserModelState(user_id=user_id)
        return UserModelState(
            user_id=user_id,
            active_model_id=data.get("active_model_id"),
            active_model_version=data.get("active_model_version"),
            model_status=data.get("model_status", "none"),
            model_updated_at=_parse_datetime(data.get("model_updated_at")),
        )

    def set_user_state(self, state: UserModelState) -> None:
        payload = {
            "user_id": state.user_id,
            "active_model_id": state.active_model_id,
            "active_model_version": state.active_model_version,
            "model_status": state.model_status,
            "model_updated_at": _serialize_datetime(state.model_updated_at),
        }
        self._client.collection(USER_MODEL_STATE_COLLECTION).document(state.user_id).set(
            payload, merge=True
        )

    def create_model_metadata(self, metadata: ModelMetadata) -> None:
        self._upsert_model_metadata(metadata)

    def update_model_metadata(self, metadata: ModelMetadata) -> None:
        self._upsert_model_metadata(metadata)

    def get_latest_model_metadata(self, user_id: str) -> Optional[ModelMetadata]:
        query = (
            self._client.collection(USER_MODEL_METADATA_COLLECTION)
            .where("user_id", "==", user_id)
            .order_by("version", direction="DESCENDING")
            .limit(1)
        )
        docs = list(query.stream())
        if not docs:
            return None
        return self._deserialize_metadata(docs[0].to_dict() or {})

    def _upsert_model_metadata(self, metadata: ModelMetadata) -> None:
        doc_id = f"{metadata.user_id}-{metadata.version}"
        payload = {
            "user_id": metadata.user_id,
            "version": metadata.version,
            "base_model": metadata.base_model,
            "status": metadata.status,
            "created_at": _serialize_datetime(metadata.created_at),
            "openai_training_file_id": metadata.openai_training_file_id,
            "openai_job_id": metadata.openai_job_id,
            "openai_fine_tuned_model_id": metadata.openai_fine_tuned_model_id,
            "completed_at": _serialize_datetime(metadata.completed_at),
            "training_data_range": _serialize_training_range(metadata.training_data_range),
            "num_messages": metadata.num_messages,
            "token_estimate": metadata.token_estimate,
            "dataset_hash": metadata.dataset_hash,
            "failure_reason": metadata.failure_reason,
        }
        self._client.collection(USER_MODEL_METADATA_COLLECTION).document(doc_id).set(
            payload, merge=True
        )

    def _deserialize_metadata(self, data: Dict[str, Any]) -> ModelMetadata:
        return ModelMetadata(
            user_id=data.get("user_id", ""),
            version=int(data.get("version") or 0),
            base_model=data.get("base_model", ""),
            status=data.get("status", "unknown"),
            created_at=_parse_datetime(data.get("created_at")) or datetime.now(timezone.utc),
            openai_training_file_id=data.get("openai_training_file_id"),
            openai_job_id=data.get("openai_job_id"),
            openai_fine_tuned_model_id=data.get("openai_fine_tuned_model_id"),
            completed_at=_parse_datetime(data.get("completed_at")),
            training_data_range=_parse_training_range(data.get("training_data_range")),
            num_messages=int(data.get("num_messages") or 0),
            token_estimate=int(data.get("token_estimate") or 0),
            dataset_hash=data.get("dataset_hash"),
            failure_reason=data.get("failure_reason"),
        )
