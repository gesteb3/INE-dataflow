"""Endpoints de inicio de sesión y sesión activa."""

import psycopg
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.repositories.users import find_active_user
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.services.auth import create_access_token, decode_access_token, verify_password
from app.repositories.audit import record_audit_event


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> UserInfo:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Se requiere autenticación")
    try:
        return decode_access_token(credentials.credentials)
    except Exception as error:  # jwt.InvalidTokenError puede variar entre versiones
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o vencido") from error


def require_roles(*roles: str):
    def dependency(user: UserInfo = Depends(current_user)) -> UserInfo:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para esta acción")
        return user

    return dependency


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: LoginRequest) -> TokenResponse:
    try:
        user = find_active_user(payload.username)
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el usuario") from error
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    info = UserInfo(username=user["username"], full_name=user["full_name"], role=user["role"])
    try:
        record_audit_event(info.username, "LOGIN_SUCCESS", "USER", info.username)
    except psycopg.Error:
        pass
    return TokenResponse(access_token=create_access_token(info), user=info)


@router.get("/auth/me", response_model=UserInfo, tags=["auth"])
def me(user: UserInfo = Depends(current_user)) -> UserInfo:
    return user
