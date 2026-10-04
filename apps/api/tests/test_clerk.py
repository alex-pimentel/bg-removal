from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt
from jose.utils import long_to_base64

from src.core.config import settings

ISSUER = "https://clerk.example.com"
AUDIENCE = "agenteresolve"
KID = "test-key"


def _keypair() -> tuple[rsa.RSAPrivateKey, dict]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    numbers = private_key.public_key().public_numbers()
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": KID,
        "n": long_to_base64(numbers.n).decode(),
        "e": long_to_base64(numbers.e).decode(),
    }
    return private_key, jwk


def _token(private_key: rsa.RSAPrivateKey, **overrides) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": "user_123",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    claims.update(overrides)
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": KID})


@pytest.fixture(autouse=True)
def _clerk_settings(monkeypatch):
    monkeypatch.setattr(settings, "CLERK_ISSUER", ISSUER)
    monkeypatch.setattr(settings, "CLERK_AUDIENCE", AUDIENCE)
    monkeypatch.setattr(settings, "CLERK_JWKS_URL", "https://clerk.example.com/.well-known/jwks.json")


@pytest.fixture
def keypair(mocker):
    private_key, jwk = _keypair()
    mocker.patch(
        "src.core.clerk._fetch_jwks",
        return_value={"keys": [jwk]},
    )
    return private_key


def test_valid_token_returns_claims(keypair):
    from src.core.clerk import verify_token

    claims = verify_token(_token(keypair))

    assert claims["sub"] == "user_123"


def test_invalid_signature_rejected(keypair):
    from src.core.clerk import verify_token

    other_key, _ = _keypair()
    bad = _token(other_key)

    with pytest.raises(ValueError):
        verify_token(bad)


def test_wrong_issuer_rejected(keypair):
    from src.core.clerk import verify_token

    with pytest.raises(ValueError):
        verify_token(_token(keypair, iss="https://evil.example.com"))


def test_wrong_audience_rejected(keypair):
    from src.core.clerk import verify_token

    with pytest.raises(ValueError):
        verify_token(_token(keypair, aud="someone-else"))


def test_expired_token_rejected(keypair):
    from src.core.clerk import verify_token

    past = datetime.now(UTC) - timedelta(hours=1)
    with pytest.raises(ValueError):
        verify_token(_token(keypair, exp=past, iat=past - timedelta(minutes=5)))


def test_unconfigured_raises(keypair, monkeypatch):
    from src.core import clerk

    monkeypatch.setattr(settings, "CLERK_JWKS_URL", "")
    with pytest.raises(ValueError):
        clerk.verify_token(_token(keypair))


def test_returns_none_for_missing_header(monkeypatch):
    from src.core.clerk import optional_user

    assert optional_user(None) is None
    assert optional_user("") is None


def test_optional_user_verifies_bearer(keypair):
    from src.core.clerk import optional_user

    claims = optional_user(f"Bearer {_token(keypair)}")
    assert claims is not None
    assert claims["sub"] == "user_123"


def test_optional_user_rejects_bad_bearer(keypair):
    from src.core.clerk import optional_user

    other_key, _ = _keypair()
    with pytest.raises(ValueError):
        optional_user(f"Bearer {_token(other_key)}")


def test_jwks_cached(mocker):
    from src.core import clerk

    calls = {"n": 0}

    def fake_get(url: str):
        calls["n"] += 1
        response = mocker.MagicMock()
        response.json.return_value = {"keys": []}
        response.raise_for_status.return_value = None
        return response

    mocker.patch("src.core.clerk.httpx.get", side_effect=fake_get)
    clerk._jwks_cache = None

    clerk._fetch_jwks()
    clerk._fetch_jwks()

    assert calls["n"] == 1
    assert clerk._jwks_cache is not None
    assert clerk._jwks_cache[1] > time.time()
