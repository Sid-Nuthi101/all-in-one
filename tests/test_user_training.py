from datetime import datetime, timezone

from agent_train import InMemoryMetadataStore, ModelMetadata, UserModelState
from user_training import FirstLoginTrainer


class _FailingOpenAIClient:
    def upload_training_file(self, jsonl: str) -> str:
        raise AssertionError("should not upload training data when model exists")

    def create_fine_tune_job(self, training_file_id: str, base_model: str) -> str:
        raise AssertionError("should not create a fine-tune job when model exists")

    def poll_fine_tune_job(self, job_id: str):
        raise AssertionError("should not poll a fine-tune job when model exists")


def test_first_login_trainer_skips_when_model_ready():
    store = InMemoryMetadataStore()
    created_at = datetime(2024, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
    metadata = ModelMetadata(
        user_id="user-1",
        version=1,
        base_model="gpt-4o-mini",
        status="succeeded",
        created_at=created_at,
        completed_at=created_at,
        openai_fine_tuned_model_id="ft-model",
    )
    store.create_model_metadata(metadata)
    store.set_user_state(
        UserModelState(
            user_id="user-1",
            active_model_id="ft-model",
            active_model_version=1,
            model_status="ready",
            model_updated_at=created_at,
        )
    )

    def fail_bridge_factory():
        raise AssertionError("message bridge should not be created when model exists")

    trainer = FirstLoginTrainer(
        openai_client=_FailingOpenAIClient(),
        metadata_store=store,
        message_bridge_factory=fail_bridge_factory,
    )

    outcome = trainer.train_if_untrained(user_id="user-1", limit=5000, now=created_at)

    assert outcome.was_trained is False
    assert outcome.metadata.openai_fine_tuned_model_id == "ft-model"


def test_first_login_trainer_skips_when_metadata_succeeded_without_state():
    store = InMemoryMetadataStore()
    created_at = datetime(2024, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
    metadata = ModelMetadata(
        user_id="user-2",
        version=1,
        base_model="gpt-4o-mini",
        status="succeeded",
        created_at=created_at,
        completed_at=created_at,
        openai_fine_tuned_model_id="ft-model-2",
    )
    store.create_model_metadata(metadata)

    def fail_bridge_factory():
        raise AssertionError("message bridge should not be created when model exists")

    trainer = FirstLoginTrainer(
        openai_client=_FailingOpenAIClient(),
        metadata_store=store,
        message_bridge_factory=fail_bridge_factory,
    )

    outcome = trainer.train_if_untrained(user_id="user-2", limit=5000, now=created_at)

    assert outcome.was_trained is False
    assert outcome.metadata.openai_fine_tuned_model_id == "ft-model-2"
