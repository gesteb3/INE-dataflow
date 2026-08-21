# Contrato de datos CSV

## Propósito

Este documento define el formato de entrada para el MVP de INE DataFlow. Es un contrato académico de referencia para una encuesta de hogares; no representa todavía el esquema oficial de una encuesta específica del Instituto Nacional de Estadística. Antes de implementar el procesamiento deberá validarse contra el cuestionario, diccionario de datos y catálogos oficiales que correspondan.

## Convenciones del archivo

| Elemento | Regla del MVP |
| --- | --- |
| Extensión | `.csv` |
| Codificación | UTF-8, preferiblemente con BOM ausente |
| Separador | Coma (`,`) |
| Encabezado | Obligatorio; los nombres deben coincidir exactamente |
| Fin de línea | LF o CRLF |
| Comillas | Se permiten comillas dobles para valores que contengan comas o saltos de línea |
| Valores vacíos | Se representan como campo vacío; no se usará `N/A` como valor válido |
| Fechas | ISO 8601: `YYYY-MM-DD` |
| Decimales | Punto como separador decimal, por ejemplo `1250.50` |
| Espacios | Se eliminarán espacios al inicio y al final antes de validar |

Se recomienda nombrar los archivos con el patrón `encuesta_<codigo>_<fecha>.csv`, por ejemplo `encuesta_ENHOGAR_20260821.csv`. El nombre del archivo no sustituye la validación del contenido.

## Esquema de entrada

El orden de las columnas debe ser el siguiente. Los nombres son sensibles a mayúsculas y minúsculas.

| Columna | Tipo lógico | Obligatoria | Reglas |
| --- | --- | --- | --- |
| `record_id` | Texto | Sí | Identificador único dentro del archivo; de 1 a 64 caracteres; permite letras, números, guion y guion bajo. |
| `survey_code` | Texto | Sí | Código de encuesta; de 3 a 30 caracteres en mayúsculas, números, guion o guion bajo. |
| `interview_date` | Fecha | Sí | Formato `YYYY-MM-DD`; no puede ser una fecha futura. |
| `department_code` | Texto | Sí | Código territorial no vacío, de hasta 10 caracteres. Su pertenencia al catálogo oficial se validará cuando exista el catálogo de referencia. |
| `municipality_code` | Texto | Sí | Código territorial no vacío, de hasta 10 caracteres. Debe corresponder al departamento cuando se disponga del catálogo. |
| `urban_rural` | Enumeración | Sí | Solo `U` (urbana) o `R` (rural). |
| `respondent_age` | Entero | Sí | Rango de 0 a 120 años. La edad mínima específica podrá cambiar según la encuesta. |
| `respondent_sex` | Enumeración | Sí | `F`, `M`, `X` o `NR` (no responde). |
| `household_size` | Entero | Sí | Rango de 1 a 50 personas. |
| `monthly_income_gtq` | Decimal | No | Ingreso mensual en quetzales; si se informa, debe ser mayor o igual a cero y tener como máximo dos decimales. |

## Ejemplo válido

```csv
record_id,survey_code,interview_date,department_code,municipality_code,urban_rural,respondent_age,respondent_sex,household_size,monthly_income_gtq
HOGAR-0001,ENHOGAR,2026-08-20,01,0101,U,34,F,4,4250.00
HOGAR-0002,ENHOGAR,2026-08-20,07,0704,R,52,M,2,1800.50
```

## Metadatos generados por el sistema

Los siguientes datos no forman parte del CSV de entrada. Serán generados por el pipeline y almacenados junto con el resultado:

- Identificador del lote de carga.
- Nombre y fecha de recepción del archivo.
- Fecha y hora de procesamiento.
- Estado del registro: válido o rechazado.
- Cantidad de advertencias y errores.
- Código, columna y fila de cada error.

No se deben incluir nombres, números de DPI, teléfonos, direcciones exactas ni otros datos personales directos en este contrato académico. Si una encuesta real los requiere, deberán definirse controles de privacidad y acceso antes de incorporarlos.

## Decisiones pendientes

- Confirmar la encuesta objetivo y su diccionario oficial.
- Sustituir las reglas territoriales provisionales por catálogos oficiales.
- Confirmar si el identificador debe ser único globalmente o solo dentro de cada lote.
- Definir la política de retención y anonimización de los archivos originales.
