"""
Auth-related Pydantic schemas: registration, login, tokens, and profile.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ProfileOut(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    phone: str | None = None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None
    profile: ProfileOut | None = None

    model_config = {"from_attributes": True}
