# Diseño funcional y flujo del MVP

## Contexto del proyecto

INE DataFlow es un proyecto académico para evaluar y mejorar la operación de datos del Instituto Nacional de Estadística de Guatemala. El diseño responde a las debilidades identificadas en la evaluación inicial:

- digitación, extracción y limpieza manual de grandes volúmenes;
- riesgo de errores humanos y filtración de información sensible;
- infraestructura y automatización todavía insuficientes;
- necesidad de trazabilidad para auditar cambios y resultados.

El objetivo del MVP es demostrar un flujo controlado y repetible para recibir encuestas, validar su calidad y preparar los resultados para análisis.

## Decisión principal: revisión humana antes de confirmar

El sistema no guardará automáticamente los registros válidos en el almacenamiento definitivo. Primero procesará el lote y mostrará un resumen para que un operador revise el resultado. Esta decisión es apropiada para el contexto porque reduce el riesgo de publicar datos erróneos y demuestra control operativo.

Los errores se conservarán en una bandeja de revisión con fila, columna, código y mensaje. No se eliminarán las filas rechazadas ni se mezclará información inválida con los registros aprobados.

## Flujo funcional

```text
Operador
   |
   v
1. Seleccionar archivo CSV
   |
   v
2. Validar archivo y encabezado
   |-- error estructural --> rechazo del lote con explicación
   v
3. Procesar filas y aplicar reglas
   |
   v
4. Mostrar resumen y vista previa
   |-- válidos
   |-- errores
   |-- advertencias
   v
5. Operador revisa y confirma
   |-- cancelar --> lote queda pendiente
   v
6. Guardar registros válidos y errores por separado
   |
   v
7. Consultar historial y métricas para Power BI
```

## Pantallas previstas para Angular

| Pantalla | Propósito |
| --- | --- |
| Inicio | Mostrar estado del sistema, última carga y métricas básicas. |
| Nueva carga | Seleccionar el CSV, mostrar nombre, tamaño y validaciones preliminares. |
| Resultado de validación | Mostrar totales, porcentaje de calidad, advertencias y errores. |
| Detalle de errores | Filtrar por código, fila y columna; permitir descargar un reporte de errores. |
| Historial de cargas | Consultar lotes, fechas, estado y usuario operador cuando exista autenticación. |

## Estilo visual

La interfaz usará una línea institucional sobria inspirada en el contexto del INE:

- azul oscuro para navegación y encabezados;
- azul medio para acciones principales;
- blanco y gris claro para fondos y tarjetas;
- verde para resultados válidos;
- ámbar para advertencias;
- rojo para errores;
- tipografía legible, alto contraste y tablas fáciles de escanear.

Los colores son una propuesta académica; se podrán sustituir por el manual de marca oficial si se proporciona.

## Seguridad y control para el MVP

- No usar datos personales reales en el repositorio.
- Mantener credenciales en variables de entorno y fuera de Git.
- Separar registros válidos, errores y metadatos de auditoría.
- Registrar lote, fecha de procesamiento y resultado de cada carga.
- Evitar exponer valores sensibles completos en logs y mensajes de error.
- Dejar autenticación y autorización como siguiente control, antes de un despliegue real.

## Métricas para demostrar mejora

El MVP deberá poder calcular, como mínimo:

- total de filas procesadas;
- porcentaje de registros válidos;
- porcentaje de registros rechazados;
- errores por categoría;
- tiempo de procesamiento por lote;
- cargas procesadas y fallidas.

Estas métricas serán la base para un futuro dashboard de Power BI y para medir la reducción de errores y tiempos durante los seis meses planteados en la evaluación.

## Estado de implementación

El flujo de carga, validación, staging y confirmación ya está implementado en el backend. La siguiente fase podrá construir la interfaz Angular para que el operador ejecute este proceso sin usar directamente Swagger. El acceso a PostgreSQL y la publicación en Power BI seguirán controlados por los estados del lote.
