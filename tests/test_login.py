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


def test_exchange_code_for_tokens_uses_http_post():
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            captured["status_checked"] = True

        def json(self):
            return {"id_token": "token"}

    def fake_post(url, data, headers, timeout):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeResponse()

    result = login.exchange_code_for_tokens(
        code="auth-code",
        client_id="client-id",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        http_post=fake_post,
    )

    assert result == {"id_token": "token"}
    assert captured["status_checked"] is True
    assert captured["data"]["code"] == "auth-code"


def test_login_with_apple_flow(monkeypatch):
    def fake_exchange(**kwargs):
        return {"id_token": "token-123"}

    def fake_decoder(id_token, audience, issuer):
        assert id_token == "token-123"
        assert audience == "client-id"
        assert issuer == "https://appleid.apple.com"
        return {"sub": "apple-sub", "email": "user@example.com"}

    captured = {}

    def fake_upsert(client, apple_user, now_fn=None):
        captured["client"] = client
        captured["apple_user"] = apple_user
        captured["now_fn"] = now_fn
        return {"apple_sub": apple_user["apple_sub"]}

    monkeypatch.setattr(login.firebase, "upsert_user", fake_upsert)

    result = login.login_with_apple(
        code="auth-code",
        client_id="client-id",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        firebase_client="firebase-client",
        token_exchange=fake_exchange,
        jwt_decoder=fake_decoder,
    )

    assert result == {"apple_sub": "apple-sub"}
    assert captured["client"] == "firebase-client"
    assert captured["apple_user"]["email"] == "user@example.com"
