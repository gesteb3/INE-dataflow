"""Persistencia de eventos de auditoría."""

from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb
from psycopg.rows import dict_row

from app.db import database_url


def record_audit_event(
    username: str | None,
    action: str,
    resource_type: str,
    resource_id: UUID | str | None = None,
    details: dict | None = None,
) -> None:
    with psycopg.connect(database_url()) as connection:
        connection.execute(
            """
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details)
            SELECT id, %s, %s, %s, %s
            FROM app_users
            WHERE username = %s
            """,
            (action, resource_type, str(resource_id) if resource_id else None, Jsonb(details or {}), username),
        )


def list_audit_events(limit: int = 100) -> list[dict]:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT a.action, a.resource_type, a.resource_id,
                       u.username, a.details, a.created_at
                FROM audit_logs a
                LEFT JOIN app_users u ON u.id = a.user_id
                ORDER BY a.created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()
