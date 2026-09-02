"""Persistencia de usuarios y acceso para autenticación."""

from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.db import database_url


def find_active_user(username: str) -> dict | None:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT username, full_name, role, password_hash
                FROM app_users
                WHERE LOWER(username) = LOWER(%s) AND is_active = TRUE
                """,
                (username,),
            )
            return cursor.fetchone()


def list_users() -> list[dict]:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, full_name, role, is_active, created_at
                FROM app_users
                ORDER BY is_active DESC, full_name, username
                """
            )
            return cursor.fetchall()


def find_user(user_id: UUID) -> dict | None:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, full_name, role, is_active, created_at
                FROM app_users
                WHERE id = %s
                """,
                (user_id,),
            )
            return cursor.fetchone()


def create_user(username: str, full_name: str, password_hash: str, role: str) -> dict:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO app_users (username, full_name, password_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id, username, full_name, role, is_active, created_at
                """,
                (username.lower(), full_name.strip(), password_hash, role),
            )
            return cursor.fetchone()


def update_user(user_id: UUID, full_name: str | None, role: str | None, is_active: bool | None) -> dict | None:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE app_users
                SET full_name = COALESCE(%s, full_name),
                    role = COALESCE(%s, role),
                    is_active = COALESCE(%s, is_active)
                WHERE id = %s
                RETURNING id, username, full_name, role, is_active, created_at
                """,
                (full_name.strip() if full_name is not None else None, role, is_active, user_id),
            )
            return cursor.fetchone()
