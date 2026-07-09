"""
Security primitives: bcrypt password hashing and JWT access/refresh tokens.

Passwords are hashed one-way with bcrypt (never stored or logged in plaintext).
JWTs are signed with the HMAC secret from settings.JWT_SECRET.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    try:
        return _pwd_context.verify(plain_password, password_hash)
    except ValueError:
        return False


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str) -> str:
    return _create_token(
        user_id,
        "access",
        timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        user_id,
        "refresh",
        timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
    )


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    """
    Decode and validate a JWT.

    Raises jwt.PyJWTError (or subclass) on invalid signature/expiry, and
    ValueError if the token type does not match expected_type.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if expected_type is not None and payload.get("type") != expected_type:
        raise ValueError("Unexpected token type")
    return payload
