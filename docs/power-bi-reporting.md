# Capa de reportes para Power BI

## Objetivo

Esta capa expone únicamente datos agregados y de solo lectura para que Power BI pueda consumir indicadores del MVP sin conectarse directamente a las tablas operativas de PostgreSQL.

## Endpoints disponibles

Con Docker Compose activo:

| Endpoint | Uso |
| --- | --- |
| `GET /api/v1/reports/summary` | Indicadores generales de lotes, filas válidas, rechazadas y errores. |
| `GET /api/v1/reports/by-department` | Registros válidos, distribución urbana/rural, edad, tamaño del hogar e ingresos por departamento. |
| `GET /api/v1/batches/{batch_id}/valid.csv` | Descarga operativa del archivo limpio con las filas válidas confirmadas. |

URLs locales:

```text
http://localhost:8001/api/v1/reports/summary?batch_id=<ID_DEL_LOTE_CONFIRMADO>
http://localhost:8001/api/v1/reports/by-department?batch_id=<ID_DEL_LOTE_CONFIRMADO>
```

## Qué consume Power BI

Power BI debe consumir principalmente los dos endpoints JSON de reportes. Estos ya devuelven las métricas agregadas que necesita el tablero y aceptan `batch_id` para que el análisis corresponda a un lote confirmado específico. El endpoint CSV limpio es una descarga para Excel, auditoría o intercambio de datos; no es la fuente principal del tablero.

Angular consume esos mismos reportes, además de `/api/v1/batches` para construir el filtro de lotes y mostrar automáticamente el último confirmado.

## Consumo inicial desde Power BI Desktop

1. Abrir **Obtener datos > Web**.
2. Seleccionar **Opciones avanzadas**.
3. Introducir uno de los endpoints anteriores.
4. En el MVP, enviar el token Bearer generado al iniciar sesión; los reportes están protegidos por autenticación.
5. Cargar el resultado JSON y convertirlo en tabla.

Ejemplo de consulta M para `by-department` durante la demostración local:

```powerquery
let
    Token = "PEGAR_AQUI_EL_TOKEN_DE_LOGIN",
    Source = Json.Document(
        Web.Contents(
            "http://localhost:8001/api/v1/reports/by-department?batch_id=<ID_DEL_LOTE_CONFIRMADO>",
            [Headers = [Authorization = "Bearer " & Token]]
        )
    ),
    Table = Table.FromRecords(Source)
in
    Table
```

No se debe publicar un token real dentro de un informe compartido. Para producción se necesitarían credenciales administradas, HTTPS, una API accesible desde Power BI Service y una política formal de protección de datos.

La conexión local solo funciona mientras la API esté ejecutándose en la computadora. Para publicar un informe en Power BI Service será necesario definir una infraestructura accesible, autenticación, red segura y una política de protección de datos.

## Indicadores iniciales sugeridos

- Lotes recibidos y confirmados.
- Filas procesadas, válidas y rechazadas.
- Total de errores de validación.
- Registros válidos por departamento.
- Distribución urbana y rural.
- Promedio de edad, tamaño del hogar e ingreso mensual.

Los datos actuales son sintéticos y sirven únicamente para la demostración académica.
