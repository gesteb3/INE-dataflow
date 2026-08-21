# Catálogo inicial de errores

Este catálogo define códigos estables para que la API, la base de datos, las pruebas y los reportes utilicen la misma clasificación. Los mensajes pueden mejorar sin cambiar el código.

| Código | Severidad | Descripción | Acción |
| --- | --- | --- | --- |
| `FILE-001` | ERROR | Extensión no soportada. | Rechazar el archivo. |
| `FILE-002` | ERROR | Archivo vacío o sin filas de datos. | Rechazar el archivo. |
| `FILE-003` | ERROR | Codificación distinta de UTF-8. | Rechazar el archivo. |
| `FILE-004` | ERROR | Falta una columna obligatoria. | Rechazar el archivo. |
| `FILE-005` | ERROR | Columna duplicada en el encabezado. | Rechazar el archivo. |
| `FILE-006` | WARNING | Columna no prevista para el MVP. | Procesar solo si no impide leer el archivo y registrar la advertencia. |
| `FILE-007` | ERROR | Cantidad de campos incorrecta en una fila. | Rechazar la fila. |
| `FILE-008` | ERROR | Separador no compatible o estructura CSV ilegible. | Rechazar el archivo. |
| `FIELD-001` | ERROR | Campo obligatorio vacío. | Rechazar la fila. |
| `FIELD-002` | ERROR | `record_id` tiene caracteres no permitidos. | Rechazar la fila. |
| `FIELD-003` | ERROR | `record_id` duplicado en el lote. | Rechazar la fila duplicada. |
| `FIELD-004` | ERROR | `survey_code` inválido. | Rechazar la fila. |
| `FIELD-005` | ERROR | Fecha inválida o con formato incorrecto. | Rechazar la fila. |
| `FIELD-006` | ERROR | Fecha de entrevista futura. | Rechazar la fila. |
| `FIELD-007` | ERROR | Código territorial inválido o vacío. | Rechazar la fila. |
| `FIELD-008` | ERROR | Valor no permitido para `urban_rural`. | Rechazar la fila. |
| `FIELD-009` | ERROR | Edad fuera de rango o no entera. | Rechazar la fila. |
| `FIELD-010` | ERROR | Valor no permitido para `respondent_sex`. | Rechazar la fila. |
| `FIELD-011` | ERROR | Tamaño del hogar fuera de rango o no entero. | Rechazar la fila. |
| `FIELD-012` | ERROR | Ingreso no numérico, negativo o con demasiados decimales. | Rechazar la fila. |
| `FIELD-013` | WARNING | Campo con espacios externos normalizados. | Procesar y conservar la advertencia. |
| `CROSS-001` | ERROR | Municipio no corresponde al departamento según catálogo. | Rechazar la fila. |
| `CROSS-002` | ERROR | Regla específica de la encuesta incumplida. | Rechazar la fila. |
| `SYSTEM-001` | ERROR | Error inesperado durante el procesamiento. | No perder la fila; registrar el lote y enviar a revisión técnica. |

## Estructura mínima de un error

Cada error deberá poder asociarse, como mínimo, con:

- Identificador del lote.
- Número de fila del archivo, considerando el encabezado como fila 1.
- `record_id`, si pudo leerse.
- Código de error.
- Nombre de la columna, cuando aplique.
- Valor recibido, con protección para datos sensibles.
- Mensaje legible.
- Fecha y hora de detección.
