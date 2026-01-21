import base64
import json

import auth


def _make_jwt(payload):
    header = {"alg": "none", "typ": "JWT"}
    def encode(obj):
        raw = json.dumps(obj).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
    return ".".join([encode(header), encode(payload), ""])


def test_decode_jwt_without_verification():
    token = _make_jwt({"sub": "user-123", "email": "user@example.com"})
    decoded = auth.decode_jwt_without_verification(token, audience="client", issuer="issuer")
    assert decoded["sub"] == "user-123"
