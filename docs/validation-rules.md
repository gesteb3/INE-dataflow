# Reglas de validación de calidad

## Resultado de una carga

Cada archivo recibido debe producir un resumen con:

- Total de filas de datos leídas.
- Filas válidas.
- Filas rechazadas por errores.
- Filas con advertencias.
- Errores agrupados por código y columna.

Un registro es **válido** cuando no tiene errores de severidad `ERROR`. Las advertencias no lo rechazan, pero deben conservarse para auditoría. El archivo no debe procesarse silenciosamente si tiene errores estructurales que impidan interpretar sus filas.

## Validaciones por nivel

### Archivo

| ID | Regla | Severidad |
| --- | --- | --- |
| V-FILE-001 | La extensión debe ser `.csv`. | ERROR |
| V-FILE-002 | El archivo no debe estar vacío y debe contener encabezado y al menos una fila de datos. | ERROR |
| V-FILE-003 | El archivo debe estar codificado en UTF-8. | ERROR |
| V-FILE-004 | El encabezado debe contener todas las columnas obligatorias, sin duplicados y con los nombres exactos. | ERROR |
| V-FILE-005 | El archivo no debe contener columnas inesperadas en el MVP. | WARNING |
| V-FILE-006 | Cada fila debe tener la misma cantidad de campos que el encabezado. | ERROR |
| V-FILE-007 | El separador esperado es coma. Si no se puede detectar correctamente, se rechaza el archivo. | ERROR |

### Campo

| ID | Regla | Severidad |
| --- | --- | --- |
| V-FIELD-001 | Los campos obligatorios no pueden estar vacíos después de quitar espacios externos. | ERROR |
| V-FIELD-002 | `record_id` debe cumplir el patrón `[A-Za-z0-9_-]+` y no repetirse dentro del lote. | ERROR |
| V-FIELD-003 | `survey_code` debe usar entre 3 y 30 caracteres permitidos. | ERROR |
| V-FIELD-004 | `interview_date` debe tener formato `YYYY-MM-DD` y ser una fecha real. | ERROR |
| V-FIELD-005 | `interview_date` no puede ser posterior a la fecha de procesamiento. | ERROR |
| V-FIELD-006 | `department_code` y `municipality_code` deben ser valores no vacíos de máximo 10 caracteres. | ERROR |
| V-FIELD-007 | `urban_rural` solo puede ser `U` o `R`. | ERROR |
| V-FIELD-008 | `respondent_age` debe ser entero entre 0 y 120. | ERROR |
| V-FIELD-009 | `respondent_sex` solo puede ser `F`, `M`, `X` o `NR`. | ERROR |
| V-FIELD-010 | `household_size` debe ser entero entre 1 y 50. | ERROR |
| V-FIELD-011 | `monthly_income_gtq`, si está presente, debe ser numérico, no negativo y tener como máximo dos decimales. | ERROR |
| V-FIELD-012 | Los campos con espacios externos serán normalizados y generarán advertencia. | WARNING |

### Consistencia entre campos

| ID | Regla | Severidad |
| --- | --- | --- |
| V-CROSS-001 | `municipality_code` debe pertenecer a `department_code` cuando el catálogo territorial esté disponible. | ERROR |
| V-CROSS-002 | Un `record_id` duplicado dentro del mismo lote se rechaza para evitar doble conteo. | ERROR |
| V-CROSS-003 | Si el diseño de la encuesta define una edad mínima para el informante, esa regla reemplazará el rango genérico de este documento. | ERROR |

## Política de procesamiento

1. Validar primero la estructura del archivo.
2. Si la estructura es válida, procesar las filas de forma independiente.
3. Conservar los registros sin errores como registros válidos.
4. Conservar cada registro con errores en el resultado de errores, junto con fila, columna, valor recibido y código de error.
5. No detener todo el lote por un error de una sola fila, salvo que el error sea estructural o comprometa la interpretación del archivo.
6. No registrar valores sensibles completos en logs técnicos.

## Alcance fuera de esta fase

La normalización de nombres, imputación estadística, detección avanzada de valores atípicos, reglas de confidencialidad y validación contra catálogos oficiales se definirán cuando exista información real de la encuesta.
