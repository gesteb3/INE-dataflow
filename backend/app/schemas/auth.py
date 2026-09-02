"""Modelos de autenticación y autorización."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


Role = Literal["ADMIN", "OPERATOR", "ANALYST"]


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserInfo(BaseModel):
    username: str
    full_name: str
    role: Role


class UserAdmin(BaseModel):
    id: UUID
    username: str
    full_name: str
    role: Role
    is_active: bool
    created_at: datetime


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)
    role: Role = "OPERATOR"


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    role: Role | None = None
    is_active: bool | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
