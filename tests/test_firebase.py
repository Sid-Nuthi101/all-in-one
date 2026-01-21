from datetime import datetime, timezone

import firebase
from agent_train import ModelMetadata, UserModelState


def test_upsert_user_sets_created_at_on_first_login(
    firestore_client, test_apple_sub
):
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    doc_ref = firestore_client.collection(firebase.USERS_COLLECTION).document(
        test_apple_sub
    )
    doc_ref.delete()

    result = firebase.upsert_user(
        firestore_client,
        {
            "apple_sub": test_apple_sub,
            "email": "user@example.com",
            "name": {"given": "First", "family": "Last"},
        },
        now_fn=lambda: fixed_time,
    )

    snapshot = doc_ref.get()
    stored = snapshot.to_dict()
    
    assert stored["created_at"] == fixed_time.isoformat()
    assert stored["last_login_at"] == fixed_time.isoformat()
    assert stored["providers"] == [firebase.APPLE_PROVIDER]
    assert stored["email"] == "user@example.com"
    assert stored["name"] == {"given": "First", "family": "Last"}
    assert result["apple_sub"] == test_apple_sub

    doc_ref.delete()


def test_upsert_user_does_not_overwrite_optional_fields(
    firestore_client, test_apple_sub
):
    fixed_time = datetime(2024, 2, 1, 8, 30, 0, tzinfo=timezone.utc)
    doc_ref = firestore_client.collection(firebase.USERS_COLLECTION).document(
        test_apple_sub
    )
    doc_ref.set(
        {
            "created_at": "2023-12-01T00:00:00+00:00",
            "email": "existing@example.com",
            "name": {"given": "Existing"},
            "providers": [firebase.APPLE_PROVIDER],
        },
        merge=True,
    )

    result = firebase.upsert_user(
        firestore_client,
        {"apple_sub": test_apple_sub},
        now_fn=lambda: fixed_time,
    )

    stored = doc_ref.get().to_dict()
    assert stored["created_at"] == "2023-12-01T00:00:00+00:00"
    assert stored["email"] == "existing@example.com"
    assert stored["name"] == {"given": "Existing"}
    assert stored["last_login_at"] == fixed_time.isoformat()
    assert result["email"] == "existing@example.com"
    assert result["name"] == {"given": "Existing"}

    doc_ref.delete()


def test_firestore_metadata_store_roundtrip(
    firestore_client, test_apple_sub
):
    store = firebase.FirestoreMetadataStore(firestore_client)
    state_ref = firestore_client.collection(
        firebase.USER_MODEL_STATE_COLLECTION
    ).document(test_apple_sub)
    state_ref.delete()

    metadata_query = firestore_client.collection(
        firebase.USER_MODEL_METADATA_COLLECTION
    ).where("user_id", "==", test_apple_sub)
    for doc in metadata_query.stream():
        doc.reference.delete()

    created_at = datetime(2024, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
    metadata = ModelMetadata(
        user_id=test_apple_sub,
        version=1,
        base_model="gpt-4o-mini",
        status="succeeded",
        created_at=created_at,
        completed_at=created_at,
        openai_training_file_id="file-123",
        openai_job_id="job-123",
        openai_fine_tuned_model_id="ft-abc",
        training_data_range=(created_at, created_at),
        num_messages=5000,
        token_estimate=20000,
        dataset_hash="hash-123",
    )
    store.create_model_metadata(metadata)

    state = UserModelState(
        user_id=test_apple_sub,
        active_model_id="ft-abc",
        active_model_version=1,
        model_status="ready",
        model_updated_at=created_at,
    )
    store.set_user_state(state)

    fetched_state = store.get_user_state(test_apple_sub)
    assert fetched_state.active_model_id == "ft-abc"
    assert fetched_state.active_model_version == 1
    assert fetched_state.model_status == "ready"

    fetched_metadata = store.get_latest_model_metadata(test_apple_sub)
    assert fetched_metadata is not None
    assert fetched_metadata.openai_fine_tuned_model_id == "ft-abc"
    assert fetched_metadata.training_data_range == (created_at, created_at)

    state_ref.delete()
    for doc in metadata_query.stream():
        doc.reference.delete()
