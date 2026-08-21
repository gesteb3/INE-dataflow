"""Endpoints para recepción y validación de archivos."""

from fastapi import APIRouter, File, UploadFile

from app.schemas.validation import ValidationResponse
from app.services.csv_validator import validate_csv


router = APIRouter()


@router.post("/uploads/validate", response_model=ValidationResponse, tags=["uploads"])
async def validate_upload(file: UploadFile = File(...)) -> ValidationResponse:
    """Valida un CSV y devuelve su resumen sin guardarlo todavía."""

    content = await file.read()
    return validate_csv(file.filename or "", content)
