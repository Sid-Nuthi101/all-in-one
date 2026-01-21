import login


def test_generate_pkce_pair():
    pair = login.generate_pkce_pair()
    assert "code_verifier" in pair
    assert "code_challenge" in pair
    assert len(pair["code_verifier"]) >= 43


def test_normalize_apple_user_requires_sub():
    try:
        login.normalize_apple_user({})
    except ValueError as exc:
        assert "sub" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing sub")


def test_login_with_apple_flow_persists_user(firestore_client, test_apple_sub):
    def fake_exchange(**kwargs):
        return {"id_token": "token-123"}

    def fake_decoder(id_token, audience, issuer):
        assert id_token == "token-123"
        assert audience == "client-id"
        assert issuer == "https://appleid.apple.com"
        return {"sub": test_apple_sub, "email": "user@example.com"}

    doc_ref = firestore_client.collection(login.firebase.USERS_COLLECTION).document(
        test_apple_sub
    )
    doc_ref.delete()

    result = login.login_with_apple(
        code="auth-code",
        client_id="client-id",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        firebase_client=firestore_client,
        token_exchange=fake_exchange,
        jwt_decoder=fake_decoder,
    )

    stored = doc_ref.get().to_dict()

    assert result["apple_sub"] == test_apple_sub
    assert stored["email"] == "user@example.com"
    assert login.firebase.APPLE_PROVIDER in stored["providers"]

    doc_ref.delete()


def test_create_apple_auth_request_includes_url_and_pkce():
    request = login.create_apple_auth_request(
        client_id="client-id",
        redirect_uri="https://example.com/callback",
        state="state-123",
    )

    assert request["authorization_url"].startswith(login.APPLE_AUTH_URL)
    assert request["code_verifier"]
    assert request["state"] == "state-123"


def test_ensure_user_logged_in_uses_existing_session(
    firestore_client, test_apple_sub
):
    doc_ref = firestore_client.collection(login.firebase.USERS_COLLECTION).document(
        test_apple_sub
    )
    doc_ref.set({"providers": [login.firebase.APPLE_PROVIDER]}, merge=True)

    class MemorySession:
        def __init__(self):
            self._session = {"apple_sub": test_apple_sub}

        def get(self):
            return self._session

        def set(self, session):
            self._session = session

    def prompt_sign_in(_request):
        raise AssertionError("prompt_sign_in should not be called")

    result = login.ensure_user_logged_in(
        firebase_client=firestore_client,
        session_store=MemorySession(),
        client_id="client-id",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        state="state-456",
        prompt_sign_in=prompt_sign_in,
    )

    assert result["apple_sub"] == test_apple_sub

    doc_ref.delete()


def test_ensure_user_logged_in_prompts_when_missing_session(
    firestore_client, test_apple_sub
):
    doc_ref = firestore_client.collection(login.firebase.USERS_COLLECTION).document(
        test_apple_sub
    )
    doc_ref.delete()

    class MemorySession:
        def __init__(self):
            self._session = {}

        def get(self):
            return self._session

        def set(self, session):
            self._session = session

    def fake_exchange(**kwargs):
        assert "code_verifier" in kwargs
        return {"id_token": "token-abc"}

    def fake_decoder(id_token, audience, issuer):
        assert id_token == "token-abc"
        assert audience == "client-id"
        assert issuer == "https://appleid.apple.com"
        return {"sub": test_apple_sub, "email": "user@example.com"}

    def prompt_sign_in(request):
        assert request["authorization_url"].startswith(login.APPLE_AUTH_URL)
        return {"code": "auth-code"}

    session_store = MemorySession()
    result = login.ensure_user_logged_in(
        firebase_client=firestore_client,
        session_store=session_store,
        client_id="client-id",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        state="state-789",
        prompt_sign_in=prompt_sign_in,
        token_exchange=fake_exchange,
        jwt_decoder=fake_decoder,
    )

    assert result["apple_sub"] == test_apple_sub
    assert session_store.get()["apple_sub"] == test_apple_sub

    doc_ref.delete()
