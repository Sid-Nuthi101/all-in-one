from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Sequence

from agent_train import (
    FineTuningOrchestrator,
    MessageRecord,
    MetadataStore,
    ModelMetadata,
    OpenAIClient,
    TrainingConfig,
)
from messages import MessageBridge


@dataclass
class FirstLoginTrainer:
    openai_client: OpenAIClient
    metadata_store: MetadataStore
    message_bridge_factory: Callable[[], MessageBridge] = MessageBridge
    config: TrainingConfig = TrainingConfig(lookback_days=None)

    def train(self, user_id: str, limit: int = 5000, now: Optional[datetime] = None) -> ModelMetadata:
        existing = self._get_existing_model(user_id)
        if existing is not None:
            return existing

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
        return orchestrator.start_training(user_id=user_id, messages=records, now=now)

    def _get_existing_model(self, user_id: str) -> Optional[ModelMetadata]:
        state = self.metadata_store.get_user_state(user_id)
        if state.model_status != "ready":
            return None
        latest = self.metadata_store.get_latest_model_metadata(user_id)
        if latest and latest.openai_fine_tuned_model_id:
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
