"""
User service: account creation, lookup, authentication, and profile updates.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import logger
from app.core.security import hash_password, verify_password
from app.models.user import User, UserProfile


def _normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.email == _normalize_email(email))
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str | None = None,
) -> User:
    """Create a user + empty profile. Raises ValueError if email is taken."""
    normalized = _normalize_email(email)
    existing = await get_user_by_email(db, normalized)
    if existing is not None:
        raise ValueError("An account with this email already exists.")

    user = User(email=normalized, password_hash=hash_password(password))
    user.profile = UserProfile(full_name=full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    # Re-fetch with profile eagerly loaded for serialization.
    user = await get_user_by_id(db, user.id)
    logger.info(f"User registered: {normalized}")
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Return the user if credentials are valid and the account is active."""
    user = await get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def touch_last_login(db: AsyncSession, user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()


async def update_profile(
    db: AsyncSession,
    user: User,
    full_name: str | None,
    company_name: str | None,
    phone: str | None,
) -> User:
    """Patch profile fields. Only non-None values are applied."""
    profile = user.profile
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    if full_name is not None:
        profile.full_name = full_name
    if company_name is not None:
        profile.company_name = company_name
    if phone is not None:
        profile.phone = phone

    await db.commit()
    return await get_user_by_id(db, user.id)
