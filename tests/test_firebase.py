from datetime import datetime, timezone

import firebase


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
