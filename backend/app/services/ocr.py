"""OCR básico para formularios estandarizados de INE DataFlow."""

import re
from io import BytesIO


FIELD_PATTERNS = {
    "survey_code": r"c[oó]digo\s+de\s+encuesta\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-_]{2,})",
    "interview_date": r"fecha\s*\(?a[ñn]o?\-?\s*mes\-?\s*d[ií]a\)?\s*[:\-]?\s*([0-9]{4}[\-/][0-9]{1,2}[\-/][0-9]{1,2})",
    "department_code": r"departamento\s*[:\-]?\s*([0-9]{1,2}|[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]{2,})",
    "municipality_code": r"municipio\s*[:\-]?\s*([0-9]{1,4}|[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]{2,})",
    "respondent_age": r"edad\s*\(?a[ñn]os?\)?\s*[:\-]?\s*([0-9]{1,3})",
    "household_size": r"personas\s+en\s+hogar\s*[:\-]?\s*([0-9]{1,2})",
    "monthly_income_gtq": r"ingreso\s+mensual\s*gtq\s*[:\-]?\s*([0-9][0-9,\. ]*)",
}


def _images_from_file(file_name: str, content: bytes):
    from PIL import Image

    if file_name.lower().endswith(".pdf"):
        import fitz

        pdf = fitz.open(stream=content, filetype="pdf")
        return [Image.open(BytesIO(page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).tobytes("png"))) for page in pdf]
    return [Image.open(BytesIO(content))]


def _read_text(file_name: str, content: bytes) -> str:
    import pytesseract

    texts = []
    for image in _images_from_file(file_name, content):
        image = image.convert("L")
        try:
            texts.append(pytesseract.image_to_string(image, lang="spa", config="--psm 6"))
        except pytesseract.TesseractError:
            texts.append(pytesseract.image_to_string(image, lang="eng", config="--psm 6"))
    return "\n".join(texts).strip()


def _clean_value(value: str) -> str | None:
    cleaned = re.sub(r"[_|]+", "", value).strip(" .:-")
    return cleaned or None


def extract_fields(text: str) -> dict[str, str | None]:
    fields: dict[str, str | None] = {}
    for name, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        fields[name] = _clean_value(match.group(1)) if match else None
    fields["urban_rural"] = "URBANA" if re.search(r"(?:x|☒)\s*urbana", text, re.IGNORECASE) else None
    fields["respondent_sex"] = None
    return fields


def process_ocr_file(file_name: str, content: bytes) -> tuple[str, dict[str, str | None]]:
    text = _read_text(file_name, content)
    return text, extract_fields(text)
