from datetime import datetime, timezone

import firebase


class FakeSnapshot:
    def __init__(self, data):
        self._data = data

    def to_dict(self):
        return self._data


class FakeDocRef:
    def __init__(self, data=None):
        self.data = data
        self.set_calls = []

    def get(self):
        return FakeSnapshot(self.data)

    def set(self, payload, merge=False):
        self.set_calls.append((payload, merge))
        if self.data is None:
            self.data = {}
        self.data.update(payload)


class FakeCollection:
    def __init__(self, doc_ref):
        self.doc_ref = doc_ref
        self.document_id = None

    def document(self, document_id):
        self.document_id = document_id
        return self.doc_ref


class FakeFirestore:
    def __init__(self, doc_ref):
        self.doc_ref = doc_ref
        self.collection_name = None

    def collection(self, name):
        self.collection_name = name
        return FakeCollection(self.doc_ref)


def test_upsert_user_sets_created_at_on_first_login():
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    doc_ref = FakeDocRef()
    firestore_client = FakeFirestore(doc_ref)

    result = firebase.upsert_user(
        firestore_client,
        {
            "apple_sub": "apple-123",
            "email": "user@example.com",
            "name": {"given": "First", "family": "Last"},
        },
        now_fn=lambda: fixed_time,
    )

    assert firestore_client.collection_name == firebase.USERS_COLLECTION
    assert doc_ref.set_calls
    payload, merge = doc_ref.set_calls[0]
    assert merge is True
    assert payload["created_at"] == fixed_time.isoformat()
    assert payload["last_login_at"] == fixed_time.isoformat()
    assert payload["providers"] == [firebase.APPLE_PROVIDER]
    assert payload["email"] == "user@example.com"
    assert payload["name"] == {"given": "First", "family": "Last"}
    assert result["apple_sub"] == "apple-123"


def test_upsert_user_does_not_overwrite_optional_fields():
    existing = {
        "created_at": "2023-12-01T00:00:00+00:00",
        "email": "existing@example.com",
        "name": {"given": "Existing"},
        "providers": [firebase.APPLE_PROVIDER],
    }
    fixed_time = datetime(2024, 2, 1, 8, 30, 0, tzinfo=timezone.utc)
    doc_ref = FakeDocRef(existing)
    firestore_client = FakeFirestore(doc_ref)

    result = firebase.upsert_user(
        firestore_client,
        {"apple_sub": "apple-456"},
        now_fn=lambda: fixed_time,
    )

    payload, _ = doc_ref.set_calls[0]
    assert "created_at" not in payload
    assert "email" not in payload
    assert "name" not in payload
    assert payload["last_login_at"] == fixed_time.isoformat()
    assert result["email"] == "existing@example.com"
    assert result["name"] == {"given": "Existing"}
