"""Acceso de solo lectura a usuarios para autenticación."""

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
