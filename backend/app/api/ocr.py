"""Recepción controlada de fotografías y PDFs de encuestas en papel."""

import psycopg
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.auth import require_roles
from app.schemas.auth import UserInfo
from app.schemas.ocr import OCRFileResult
from app.services.ocr import process_ocr_file


router = APIRouter()
MAX_FILES = 5
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


@router.post("/ocr/preview", response_model=list[OCRFileResult], tags=["ocr"])
async def preview_ocr(
    files: list[UploadFile] = File(...),
    user: UserInfo = Depends(require_roles("ADMIN", "OPERATOR")),
) -> list[OCRFileResult]:
    """Extrae texto y campos de hasta cinco imágenes o PDFs, sin publicar datos todavía."""

    if not files or len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Puedes subir entre 1 y {MAX_FILES} archivos por lote OCR")

    results: list[OCRFileResult] = []
    total_bytes = 0
    for file in files:
        file_name = file.filename or "archivo-sin-nombre"
        extension = "." + file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="OCR solo admite JPG, JPEG, PNG o PDF")
        content = await file.read()
        total_bytes += len(content)
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(status_code=413, detail=f"El archivo {file_name} supera el máximo de 10 MB")
        if total_bytes > MAX_TOTAL_BYTES:
            raise HTTPException(status_code=413, detail="El lote OCR supera el máximo acumulado de 25 MB")
        try:
            text, fields = process_ocr_file(file_name, content)
            results.append(OCRFileResult(file_name=file_name, status="PROCESSED", extracted_text=text, fields=fields))
        except (ImportError, OSError, ValueError, RuntimeError) as error:
            results.append(OCRFileResult(file_name=file_name, status="ERROR", extracted_text="", fields={}, message=f"No se pudo leer el archivo: {error}"))

    try:
        from app.repositories.audit import record_audit_event

        record_audit_event(user.username, "OCR_PREVIEW_PROCESSED", "OCR_BATCH", None, {"files": len(files), "total_bytes": total_bytes})
    except psycopg.Error:
        pass
    return results
