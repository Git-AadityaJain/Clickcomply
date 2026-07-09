"""
FastAPI auth dependencies.

`get_request_user` is the main dependency used by document/analysis routes:
- When settings.REQUIRE_AUTH is True it requires a valid Bearer token.
- When False it returns the user if a valid token is present, else None,
  preserving the open local-dev workflow.
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services.user_service import get_user_by_id

_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def _resolve_user(
    credentials: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if credentials is None or not credentials.credentials:
        return None
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except (jwt.PyJWTError, ValueError):
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        return None
    return user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Return the authenticated user if a valid token is present, else None."""
    return await _resolve_user(credentials, db)


async def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require a valid Bearer token; raise 401 otherwise."""
    user = await _resolve_user(credentials, db)
    if user is None:
        raise _UNAUTHORIZED
    return user


async def get_request_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Flag-aware user dependency for resource routes.

    REQUIRE_AUTH=true  -> behaves like require_user (401 without a valid token)
    REQUIRE_AUTH=false -> returns the user if present, else None (open mode)
    """
    user = await _resolve_user(credentials, db)
    if user is None and settings.REQUIRE_AUTH:
        raise _UNAUTHORIZED
    return user
