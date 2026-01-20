from __future__ import annotations

import base64
import hashlib
import os
from typing import Any, Callable, Dict, Optional, Sequence
from urllib.parse import urlencode

import firebase

APPLE_AUTH_URL = "https://appleid.apple.com/auth/authorize"
APPLE_TOKEN_URL = "https://appleid.apple.com/auth/token"


def generate_pkce_pair(length: int = 64) -> Dict[str, str]:
    if length < 43 or length > 128:
        raise ValueError("PKCE code_verifier length must be between 43 and 128")

    verifier_bytes = os.urandom(length)
    code_verifier = base64.urlsafe_b64encode(verifier_bytes).decode("utf-8").rstrip("=")
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return {"code_verifier": code_verifier, "code_challenge": code_challenge}


def build_authorization_url(
    *,
    client_id: str,
    redirect_uri: str,
    state: str,
    code_challenge: str,
    scope: Sequence[str] = ("name", "email"),
) -> str:
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "response_mode": "query",
            "scope": " ".join(scope),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"{APPLE_AUTH_URL}?{query}"


def exchange_code_for_tokens(
    *,
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    token_url: str = APPLE_TOKEN_URL,
    code_verifier: Optional[str] = None,
    http_post: Optional[Callable[..., Any]] = None,
) -> Dict[str, Any]:
    if http_post is None:
        import requests

        http_post = requests.post

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }
    if code_verifier:
        payload["code_verifier"] = code_verifier

    response = http_post(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def verify_and_decode_id_token(
    id_token: str,
    *,
    audience: str,
    issuer: str = "https://appleid.apple.com",
    jwt_decoder: Optional[Callable[..., Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    if jwt_decoder is None:
        raise ValueError("jwt_decoder must be provided for token verification")

    claims = jwt_decoder(id_token, audience=audience, issuer=issuer)
    if not isinstance(claims, dict):
        raise ValueError("Decoded token claims must be a dictionary")
    return claims


def normalize_apple_user(
    claims: Dict[str, Any],
    *,
    name: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    apple_sub = claims.get("sub")
    if not apple_sub:
        raise ValueError("Apple token missing sub claim")

    normalized: Dict[str, Any] = {"apple_sub": apple_sub}

    email = claims.get("email")
    if email:
        normalized["email"] = email

    name_source = name if name is not None else claims.get("name")
    if isinstance(name_source, dict):
        cleaned_name = {k: v for k, v in name_source.items() if v}
        if cleaned_name:
            normalized["name"] = cleaned_name

    return normalized


def login_with_apple(
    *,
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    firebase_client: Any,
    name: Optional[Dict[str, str]] = None,
    code_verifier: Optional[str] = None,
    now_fn: Optional[Callable[[], Any]] = None,
    token_exchange: Optional[Callable[..., Dict[str, Any]]] = None,
    jwt_decoder: Optional[Callable[..., Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    exchange_fn = token_exchange or exchange_code_for_tokens
    token_response = exchange_fn(
        code=code,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
    )
    id_token = token_response.get("id_token")
    if not id_token:
        raise ValueError("Apple token response missing id_token")

    claims = verify_and_decode_id_token(
        id_token, audience=client_id, jwt_decoder=jwt_decoder
    )
    apple_user = normalize_apple_user(claims, name=name)
    return firebase.upsert_user(firebase_client, apple_user, now_fn=now_fn)
