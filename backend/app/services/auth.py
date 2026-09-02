"""Utilidades de autenticación para el MVP."""

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from app.schemas.auth import UserInfo


JWT_ALGORITHM = "HS256"
PBKDF2_ITERATIONS = 310000


def jwt_secret() -> str:
    return os.getenv("INE_DATAFLOW_JWT_SECRET", "local-only-change-this-secret")


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            base64.b64decode(salt),
            int(iterations),
            dklen=32,
        )
        return hmac.compare_digest(base64.b64encode(derived).decode(), expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user: UserInfo) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.getenv("INE_DATAFLOW_ACCESS_TOKEN_MINUTES", "60"))
    )
    return jwt.encode(
        {"sub": user.username, "role": user.role, "full_name": user.full_name, "exp": expires},
        jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> UserInfo:
    payload = jwt.decode(token, jwt_secret(), algorithms=[JWT_ALGORITHM])
    return UserInfo(
        username=str(payload["sub"]),
        full_name=str(payload["full_name"]),
        role=payload["role"],
    )
