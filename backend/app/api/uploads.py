"""Endpoints para recepción y validación de archivos."""

from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.auth import require_roles
from app.repositories.audit import record_audit_event
from app.repositories.batches import (
    BatchAlreadyConfirmedError,
    BatchNotConfirmableError,
    BatchNotFoundError,
    confirm_batch,
    persist_validation_result,
)
from app.schemas.validation import ConfirmationResponse, ValidationResponse
from app.services.csv_validator import validate_csv_result
from app.schemas.auth import UserInfo


router = APIRouter()


@router.post("/uploads/validate", response_model=ValidationResponse, tags=["uploads"])
async def validate_upload(
    file: UploadFile = File(...),
    user: UserInfo = Depends(require_roles("ADMIN", "OPERATOR")),
) -> ValidationResponse:
    """Valida un CSV y guarda el lote en staging para revisión."""

    content = await file.read()
    result = validate_csv_result(file.filename or "", content)
    try:
        persist_validation_result(result.response, result.valid_records)
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo guardar el resultado en PostgreSQL") from error
    try:
        record_audit_event(user.username, "UPLOAD_VALIDATED", "SURVEY_BATCH", result.response.batch_id, {"file_name": result.response.file_name})
    except psycopg.Error:
        pass
    return result.response


@router.post(
    "/uploads/{batch_id}/confirm",
    response_model=ConfirmationResponse,
    tags=["uploads"],
)
def confirm_upload(
    batch_id: UUID,
    user: UserInfo = Depends(require_roles("ADMIN", "OPERATOR")),
) -> ConfirmationResponse:
    """Confirma un lote revisado y publica sus filas válidas."""

    try:
        response = confirm_batch(batch_id)
        try:
            record_audit_event(user.username, "BATCH_CONFIRMED", "SURVEY_BATCH", batch_id)
        except psycopg.Error:
            pass
        return response
    except BatchNotFoundError as error:
        raise HTTPException(status_code=404, detail="Lote no encontrado") from error
    except BatchAlreadyConfirmedError as error:
        raise HTTPException(status_code=409, detail="El lote ya fue confirmado") from error
    except BatchNotConfirmableError as error:
        raise HTTPException(status_code=409, detail="El lote rechazado no se puede confirmar") from error
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo confirmar el lote en PostgreSQL") from error
