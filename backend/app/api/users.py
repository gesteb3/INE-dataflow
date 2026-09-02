"""Administración de usuarios y permisos básicos."""

from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import require_roles
from app.repositories.audit import record_audit_event
from app.repositories.users import create_user, find_user, list_users, update_user
from app.schemas.auth import UserAdmin, UserCreateRequest, UserInfo, UserUpdateRequest
from app.services.auth import hash_password


router = APIRouter()


@router.get("/users", response_model=list[UserAdmin], tags=["users"])
def get_users(_admin: UserInfo = Depends(require_roles("ADMIN"))) -> list[UserAdmin]:
    try:
        return [UserAdmin(**user) for user in list_users()]
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar los usuarios") from error


@router.post("/users", response_model=UserAdmin, status_code=status.HTTP_201_CREATED, tags=["users"])
def add_user(payload: UserCreateRequest, admin: UserInfo = Depends(require_roles("ADMIN"))) -> UserAdmin:
    try:
        user = create_user(payload.username, payload.full_name, hash_password(payload.password), payload.role)
    except psycopg.errors.UniqueViolation as error:
        raise HTTPException(status_code=409, detail="El usuario ya existe") from error
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo crear el usuario") from error
    try:
        record_audit_event(admin.username, "USER_CREATED", "APP_USER", user["id"], {"username": user["username"], "role": user["role"]})
    except psycopg.Error:
        pass
    return UserAdmin(**user)


@router.patch("/users/{user_id}", response_model=UserAdmin, tags=["users"])
def edit_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    admin: UserInfo = Depends(require_roles("ADMIN")),
) -> UserAdmin:
    if payload.full_name is None and payload.role is None and payload.is_active is None:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un cambio")
    try:
        existing = find_user(user_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if existing["username"].lower() == admin.username.lower() and (
            payload.is_active is False or payload.role not in (None, "ADMIN")
        ):
            raise HTTPException(status_code=400, detail="No puedes desactivar o quitarte el rol ADMIN")
        user = update_user(user_id, payload.full_name, payload.role, payload.is_active)
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo actualizar el usuario") from error
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    try:
        record_audit_event(admin.username, "USER_UPDATED", "APP_USER", user["id"], {"username": user["username"], "role": user["role"], "is_active": user["is_active"]})
    except psycopg.Error:
        pass
    return UserAdmin(**user)
