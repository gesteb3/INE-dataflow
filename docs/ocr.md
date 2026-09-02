# OCR de encuestas en papel

El módulo OCR recibe fotografías (`.jpg`, `.jpeg`, `.png`) o documentos PDF de la plantilla estandarizada ubicada en `data/templates/encuesta_hogares_ocr_ine.docx`.

## Límites del MVP

- Máximo 5 archivos por lote.
- Máximo 10 MB por archivo.
- Máximo 25 MB acumulados por lote.
- La lectura procesa el texto y los campos principales, pero no publica datos automáticamente.
- La persona operadora debe revisar el resultado antes de convertirlo a CSV y enviarlo al flujo normal de validación.

## Recomendaciones para la demo

1. Abrir la plantilla en Word.
2. Imprimirla o guardarla como PDF.
3. Completarla con letra de molde, tinta oscura y sin tachones.
4. Tomar una fotografía nítida, completa y sin inclinación.
5. Entrar a `OCR en papel`, seleccionar el archivo y pulsar `Procesar con OCR`.
6. Revisar los campos detectados. El resultado queda como previsualización para revisión humana.

El endpoint es `POST /api/v1/ocr/preview` y requiere un token Bearer de un usuario `ADMIN` u `OPERATOR`.
