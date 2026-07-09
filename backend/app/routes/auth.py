"""
Authentication routes: register, login, token refresh, current user, profile.
"""

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_user
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    ProfileUpdate,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_id,
    touch_last_login,
    update_profile,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _tokens_for(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        user = await create_user(
            db,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _tokens_for(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await authenticate_user(db, email=payload.email, password=payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    await touch_last_login(db, user)
    return _tokens_for(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        ) from exc

    user = await get_user_by_id(db, claims.get("sub", ""))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is no longer active.",
        )
    return _tokens_for(user)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(require_user)) -> UserOut:
    return UserOut.model_validate(current_user)


@router.patch("/profile", response_model=UserOut)
async def patch_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    user = await update_profile(
        db,
        current_user,
        full_name=payload.full_name,
        company_name=payload.company_name,
        phone=payload.phone,
    )
    logger.info(f"Profile updated for user {current_user.id}")
    return UserOut.model_validate(user)
