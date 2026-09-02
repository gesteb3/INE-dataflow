"""Modelos de autenticación y autorización."""

from typing import Literal

from pydantic import BaseModel, Field


Role = Literal["ADMIN", "OPERATOR", "ANALYST"]


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserInfo(BaseModel):
    username: str
    full_name: str
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
