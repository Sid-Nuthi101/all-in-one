from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

from agent_train import (
    FineTuningOrchestrator,
    MessageRecord,
    MetadataStore,
    ModelMetadata,
    OpenAIClient,
    TrainingConfig,
)
from messages import MessageBridge


@dataclass(frozen=True)
class TrainingOutcome:
    metadata: ModelMetadata
    was_trained: bool


@dataclass
class FirstLoginTrainer:
    openai_client: OpenAIClient
    metadata_store: MetadataStore
    message_bridge_factory: Callable[[], MessageBridge] = MessageBridge
    config: TrainingConfig = TrainingConfig(lookback_days=None)

    def train(
        self,
        user_id: str,
        limit: int = 5000,
        now: Optional[datetime] = None,
        on_training_start: Optional[Callable[[], None]] = None,
        on_training_complete: Optional[Callable[[], None]] = None,
    ) -> ModelMetadata:
        outcome = self.train_if_untrained(
            user_id=user_id,
            limit=limit,
            now=now,
            on_training_start=on_training_start,
            on_training_complete=on_training_complete,
        )
        return outcome.metadata

    def train_if_untrained(
        self,
        user_id: str,
        limit: int = 5000,
        now: Optional[datetime] = None,
        on_training_start: Optional[Callable[[], None]] = None,
        on_training_complete: Optional[Callable[[], None]] = None,
    ) -> TrainingOutcome:
        existing = self._get_existing_model(user_id)
        if existing is not None:
            return TrainingOutcome(metadata=existing, was_trained=False)

        bridge = self.message_bridge_factory()
        rows = bridge.last_messages_sent_by_user(limit=limit)

        records: list[MessageRecord] = []
        for message_rowid, date, text, chat_id, recipient_count in rows:
            timestamp = bridge.apple_time_to_dt(date)
            if timestamp is None:
                continue
            records.append(
                MessageRecord(
                    message_id=str(message_rowid),
                    timestamp=timestamp,
                    text=text,
                    conversation_id=chat_id,
                    recipient_count=recipient_count,
                )
            )

        orchestrator = FineTuningOrchestrator(
            openai_client=self.openai_client,
            metadata_store=self.metadata_store,
            config=self.config,
        )
        if on_training_start is not None:
            on_training_start()
        try:
            metadata = orchestrator.start_training(user_id=user_id, messages=records, now=now)
        finally:
            if on_training_complete is not None:
                on_training_complete()
        return TrainingOutcome(metadata=metadata, was_trained=True)

    def _get_existing_model(self, user_id: str) -> Optional[ModelMetadata]:
        state = self.metadata_store.get_user_state(user_id)
        latest = self.metadata_store.get_latest_model_metadata(user_id)
        if latest and latest.status == "succeeded" and latest.openai_fine_tuned_model_id:
            return latest
        if state.model_status == "ready" and state.active_model_id:
            return latest
        return None


def train_on_first_login(
    user_id: str,
    openai_client: OpenAIClient,
    metadata_store: MetadataStore,
    *,
    message_bridge_factory: Callable[[], MessageBridge] = MessageBridge,
    config: Optional[TrainingConfig] = None,
    limit: int = 5000,
    now: Optional[datetime] = None,
) -> ModelMetadata:
    trainer = FirstLoginTrainer(
        openai_client=openai_client,
        metadata_store=metadata_store,
        message_bridge_factory=message_bridge_factory,
        config=config or TrainingConfig(lookback_days=None),
    )
    return trainer.train(user_id=user_id, limit=limit, now=now)


def train_if_untrained(
    user_id: str,
    openai_client: OpenAIClient,
    metadata_store: MetadataStore,
    *,
    message_bridge_factory: Callable[[], MessageBridge] = MessageBridge,
    config: Optional[TrainingConfig] = None,
    limit: int = 5000,
    now: Optional[datetime] = None,
    on_training_start: Optional[Callable[[], None]] = None,
    on_training_complete: Optional[Callable[[], None]] = None,
) -> TrainingOutcome:
    trainer = FirstLoginTrainer(
        openai_client=openai_client,
        metadata_store=metadata_store,
        message_bridge_factory=message_bridge_factory,
        config=config or TrainingConfig(lookback_days=None),
    )
    return trainer.train_if_untrained(
        user_id=user_id,
        limit=limit,
        now=now,
        on_training_start=on_training_start,
        on_training_complete=on_training_complete,
    )
