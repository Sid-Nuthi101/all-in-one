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
