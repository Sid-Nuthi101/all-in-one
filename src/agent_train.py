from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Protocol, Sequence, Tuple


SYSTEM_PROMPT = (
    "You are an assistant that writes messages exactly like the user. "
    "Match tone, brevity, slang, punctuation, and emoji usage."
)
USER_PROMPT = "Write a message in the user’s style that says the following."


@dataclass(frozen=True)
class MessageRecord:
    message_id: str
    timestamp: datetime
    text: str
    conversation_id: Optional[str] = None
    recipient_count: Optional[int] = None


@dataclass(frozen=True)
class TrainingConfig:
    base_model: str = "gpt-4o-mini"
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = USER_PROMPT
    holdout_ratio: float = 0.1
    min_messages: int = 500
    min_tokens: int = 10_000
    short_message_threshold: int = 3
    redact_pii: bool = True
    lookback_days: Optional[int] = 90


@dataclass(frozen=True)
class TrainingDataset:
    train_lines: Tuple[str, ...]
    holdout: Tuple[MessageRecord, ...]
    token_estimate: int
    dataset_hash: str

    def to_jsonl(self) -> str:
        return "\n".join(self.train_lines)


@dataclass
class ModelMetadata:
    user_id: str
    version: int
    base_model: str
    status: str
    created_at: datetime
    openai_training_file_id: Optional[str] = None
    openai_job_id: Optional[str] = None
    openai_fine_tuned_model_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    training_data_range: Optional[Tuple[datetime, datetime]] = None
    num_messages: int = 0
    token_estimate: int = 0
    dataset_hash: Optional[str] = None
    failure_reason: Optional[str] = None


@dataclass
class UserModelState:
    user_id: str
    active_model_id: Optional[str] = None
    active_model_version: Optional[int] = None
    model_status: str = "none"
    model_updated_at: Optional[datetime] = None


class OpenAIClient(Protocol):
    def upload_training_file(self, jsonl: str) -> str:
        raise NotImplementedError

    def create_fine_tune_job(self, training_file_id: str, base_model: str) -> str:
        raise NotImplementedError

    def poll_fine_tune_job(self, job_id: str) -> Tuple[str, Optional[str]]:
        raise NotImplementedError


class MetadataStore(Protocol):
    def get_user_state(self, user_id: str) -> UserModelState:
        raise NotImplementedError

    def set_user_state(self, state: UserModelState) -> None:
        raise NotImplementedError

    def create_model_metadata(self, metadata: ModelMetadata) -> None:
        raise NotImplementedError

    def update_model_metadata(self, metadata: ModelMetadata) -> None:
        raise NotImplementedError

    def get_latest_model_metadata(self, user_id: str) -> Optional[ModelMetadata]:
        raise NotImplementedError


class InMemoryMetadataStore:
    def __init__(self) -> None:
        self._user_state: dict[str, UserModelState] = {}
        self._models: dict[Tuple[str, int], ModelMetadata] = {}

    def get_user_state(self, user_id: str) -> UserModelState:
        return self._user_state.get(user_id, UserModelState(user_id=user_id))

    def set_user_state(self, state: UserModelState) -> None:
        self._user_state[state.user_id] = state

    def create_model_metadata(self, metadata: ModelMetadata) -> None:
        self._models[(metadata.user_id, metadata.version)] = metadata

    def update_model_metadata(self, metadata: ModelMetadata) -> None:
        self._models[(metadata.user_id, metadata.version)] = metadata

    def get_latest_model_metadata(self, user_id: str) -> Optional[ModelMetadata]:
        versions = [version for (uid, version) in self._models if uid == user_id]
        if not versions:
            return None
        latest_version = max(versions)
        return self._models.get((user_id, latest_version))


def filter_recent_messages(
    messages: Iterable[MessageRecord],
    now: Optional[datetime] = None,
    lookback_days: Optional[int] = 90,
) -> List[MessageRecord]:
    now = now or datetime.now()
    if lookback_days is None:
        return list(messages)
    cutoff = now - timedelta(days=lookback_days)
    return [msg for msg in messages if msg.timestamp >= cutoff]


def filter_sent_messages(messages: Iterable[MessageRecord]) -> List[MessageRecord]:
    return [msg for msg in messages if msg.text is not None]


def estimate_tokens(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _is_url_only(text: str) -> bool:
    stripped = re.sub(r"https?://\S+", "", text, flags=re.IGNORECASE).strip()
    return stripped == ""


def _is_emoji_only(text: str) -> bool:
    return re.search(r"[A-Za-z0-9]", text) is None and text.strip() != ""


def _redact_pii(text: str) -> str:
    phone_pattern = re.compile(r"\b\+?\d[\d\-\(\) ]{7,}\d\b")
    email_pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    address_pattern = re.compile(
        r"\b\d{1,5}\s+[A-Za-z0-9 .'-]{2,}\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr)\b",
        re.IGNORECASE,
    )

    text = phone_pattern.sub("[REDACTED_PHONE]", text)
    text = email_pattern.sub("[REDACTED_EMAIL]", text)
    text = address_pattern.sub("[REDACTED_ADDRESS]", text)
    return text


def clean_messages(messages: Iterable[MessageRecord], config: TrainingConfig) -> List[MessageRecord]:
    cleaned: List[MessageRecord] = []
    seen: set[str] = set()

    for msg in messages:
        text = (msg.text or "").strip()
        if not text:
            continue
        if len(text) < config.short_message_threshold:
            continue
        if _is_url_only(text):
            continue
        if _is_emoji_only(text):
            continue

        normalized = re.sub(r"\s+", " ", text).lower()
        if normalized in seen:
            continue
        seen.add(normalized)

        if config.redact_pii:
            text = _redact_pii(text)

        cleaned.append(
            MessageRecord(
                message_id=msg.message_id,
                timestamp=msg.timestamp,
                text=text,
                conversation_id=msg.conversation_id,
                recipient_count=msg.recipient_count,
            )
        )

    return cleaned


def split_train_holdout(
    messages: Sequence[MessageRecord],
    holdout_ratio: float,
) -> Tuple[List[MessageRecord], List[MessageRecord]]:
    if not messages:
        return [], []

    sorted_msgs = sorted(messages, key=lambda m: m.timestamp)
    split_index = max(1, int(len(sorted_msgs) * (1 - holdout_ratio)))
    train = sorted_msgs[:split_index]
    holdout = sorted_msgs[split_index:]
    return train, holdout


def build_dataset(
    messages: Sequence[MessageRecord],
    config: TrainingConfig,
) -> TrainingDataset:
    train, holdout = split_train_holdout(messages, config.holdout_ratio)
    lines: List[str] = []
    token_estimate = 0

    for msg in train:
        payload = {
            "messages": [
                {"role": "system", "content": config.system_prompt},
                {"role": "user", "content": config.user_prompt},
                {"role": "assistant", "content": msg.text},
            ]
        }
        lines.append(json.dumps(payload, ensure_ascii=False))
        token_estimate += estimate_tokens(msg.text)

    dataset_hash = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    return TrainingDataset(
        train_lines=tuple(lines),
        holdout=tuple(holdout),
        token_estimate=token_estimate,
        dataset_hash=dataset_hash,
    )


def should_train(
    now: datetime,
    last_trained_at: Optional[datetime],
    previous_message_count: Optional[int],
    new_message_count: int,
) -> bool:
    if last_trained_at is None:
        return True

    if now - last_trained_at < timedelta(days=7):
        return False

    if previous_message_count is None:
        return True

    return new_message_count >= int(previous_message_count * 1.2)


def select_model_for_user(state: UserModelState, base_model: str) -> str:
    if state.model_status == "ready" and state.active_model_id:
        return state.active_model_id
    return base_model


def build_inference_messages(system_prompt: str, user_text: str) -> List[dict]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]


class FineTuningOrchestrator:
    def __init__(
        self,
        openai_client: OpenAIClient,
        metadata_store: MetadataStore,
        config: TrainingConfig,
    ) -> None:
        self._openai_client = openai_client
        self._metadata_store = metadata_store
        self._config = config

    def start_training(
        self,
        user_id: str,
        messages: Sequence[MessageRecord],
        now: Optional[datetime] = None,
    ) -> ModelMetadata:
        now = now or datetime.now()
        filtered = filter_recent_messages(
            messages,
            now=now,
            lookback_days=self._config.lookback_days,
        )
        cleaned = clean_messages(filtered, self._config)
        token_estimate = sum(estimate_tokens(msg.text) for msg in cleaned)

        latest_metadata = self._metadata_store.get_latest_model_metadata(user_id)
        last_trained_at = latest_metadata.completed_at if latest_metadata else None
        previous_count = latest_metadata.num_messages if latest_metadata else None

        if not should_train(now, last_trained_at, previous_count, len(cleaned)):
            return self._create_skipped_metadata(user_id, now, len(cleaned), token_estimate)

        if len(cleaned) < self._config.min_messages or token_estimate < self._config.min_tokens:
            return self._create_failed_metadata(
                user_id,
                now,
                len(cleaned),
                token_estimate,
                "failed_insufficient_data",
            )

        training_data = build_dataset(cleaned, self._config)
        model_metadata = self._create_new_metadata(
            user_id,
            now,
            len(cleaned),
            training_data.token_estimate,
            training_data.dataset_hash,
            cleaned,
        )

        training_file_id = self._openai_client.upload_training_file(training_data.to_jsonl())
        job_id = self._openai_client.create_fine_tune_job(training_file_id, self._config.base_model)
        status, fine_tuned_model_id = self._openai_client.poll_fine_tune_job(job_id)

        model_metadata.openai_training_file_id = training_file_id
        model_metadata.openai_job_id = job_id
        model_metadata.status = status
        model_metadata.openai_fine_tuned_model_id = fine_tuned_model_id
        model_metadata.completed_at = now if status == "succeeded" else None
        self._metadata_store.update_model_metadata(model_metadata)

        if status == "succeeded" and fine_tuned_model_id:
            self._metadata_store.set_user_state(
                UserModelState(
                    user_id=user_id,
                    active_model_id=fine_tuned_model_id,
                    active_model_version=model_metadata.version,
                    model_status="ready",
                    model_updated_at=now,
                )
            )

        return model_metadata

    def _create_new_metadata(
        self,
        user_id: str,
        now: datetime,
        num_messages: int,
        token_estimate: int,
        dataset_hash: str,
        messages: Sequence[MessageRecord],
    ) -> ModelMetadata:
        latest = self._metadata_store.get_latest_model_metadata(user_id)
        version = (latest.version + 1) if latest else 1
        metadata = ModelMetadata(
            user_id=user_id,
            version=version,
            base_model=self._config.base_model,
            status="queued",
            created_at=now,
            training_data_range=(messages[0].timestamp, messages[-1].timestamp),
            num_messages=num_messages,
            token_estimate=token_estimate,
            dataset_hash=dataset_hash,
        )
        self._metadata_store.create_model_metadata(metadata)
        return metadata

    def _create_failed_metadata(
        self,
        user_id: str,
        now: datetime,
        num_messages: int,
        token_estimate: int,
        reason: str,
    ) -> ModelMetadata:
        latest = self._metadata_store.get_latest_model_metadata(user_id)
        version = (latest.version + 1) if latest else 1
        metadata = ModelMetadata(
            user_id=user_id,
            version=version,
            base_model=self._config.base_model,
            status="failed",
            created_at=now,
            completed_at=now,
            num_messages=num_messages,
            token_estimate=token_estimate,
            failure_reason=reason,
        )
        self._metadata_store.create_model_metadata(metadata)
        return metadata

    def _create_skipped_metadata(
        self,
        user_id: str,
        now: datetime,
        num_messages: int,
        token_estimate: int,
    ) -> ModelMetadata:
        latest = self._metadata_store.get_latest_model_metadata(user_id)
        version = (latest.version + 1) if latest else 1
        metadata = ModelMetadata(
            user_id=user_id,
            version=version,
            base_model=self._config.base_model,
            status="skipped",
            created_at=now,
            completed_at=now,
            num_messages=num_messages,
            token_estimate=token_estimate,
        )
        self._metadata_store.create_model_metadata(metadata)
        return metadata
