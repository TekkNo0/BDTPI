# Bitácora de Uso de Inteligencia Artificial (TP8 - Unidad 8)

**Asignatura:** Base de Datos II - Tecnicatura Universitaria en Programación (UTN)  
**Proyecto:** Food Store en la feria: la base de la tablet y el cierre de la capa de datos  
**Alumno:** Maximiliano Nardez  
**Herramientas de IA:** Asistente de IA (Kiro / OpenCode / Antigravity)  
**Motores evaluados:** PostgreSQL 16+ (Servidor central) · SQLite 3.37+ (Tablet móvil)  

---

## 1. Registro Consolidado de Interacciones con la IA

| # | Qué se le pidió a la IA (Prompt) | Propuesta de la IA | Decisión y Validación Humana Aplicada | Justificación Técnica |
|---|---|---|---|---|
| **1** | *"Generá el DDL para SQLite en la tablet para almacenar el catálogo de productos y los borradores de pedidos offline."* | Propuso una tabla `producto_cache` usando tipos estándar flexibles de SQLite con columna `precio REAL` para admitir decimales, y no incluir la cláusula `STRICT`. | **DESCARTADO CON FUNDAMENTO.** Se rechazó el uso de `REAL` y la ausencia de tipado estricto. | El tipo `REAL` utiliza coma flotante binaria IEEE 754, lo cual introduce errores de redondeo financiero inadmisibles en un punto de venta (POS). Se forzó el uso del modo `STRICT` (SQLite 3.37+) y almacenamiento monetario en centavos enteros (`precio_centavos INTEGER CHECK (precio_centavos >= 0)`). |
| **2** | *"Escribí la lógica de sincronización para que la tablet actualice el stock y confirme ventas directamente en PostgreSQL cuando recupere señal."* | La IA propuso un script donde la tablet ejecutaba `UPDATE producto SET stock = stock - cantidad` y `INSERT INTO pedido` directamente en PostgreSQL con estado `CONFIRMADO`. | **DESCARTADO TAJANTEMENTE.** Viola de raíz la Regla de Oro del TP: *"El móvil propone, el servidor dispone"*. | La tablet jamás modifica stock ni precio en el servidor ni confirma ventas. `SIMULADO_APROBADO` es una simulación de viabilidad local. En la arquitectura real, la tablet únicamente envía una solicitud (`solicitud_uuid`) a una cola de ingesta, y es PostgreSQL quien transacciona y convalida bajo aislamiento ACID. |
| **3** | *"Diseñá la consulta SQL del Semáforo en SQLite para comparar las solicitudes PENDIENTE contra la instantánea del servidor (`snapshot_servidor`)."* | Propuso un bloque con CTEs (`WITH evaluacion_items ...`) clasificando en ROJO (`RECHAZADO`), AMARILLO (`CONFLICTO`) y VERDE (`SIMULADO_APROBADO`), pero evaluaba todas las filas sin filtrar por estado. | **ACEPTADO Y CORREGIDO.** Se adoptó la estructura matricial con `SUM(CASE ...)` y `GROUP_CONCAT`, pero se incorporó obligatoriamente el filtro `WHERE c.estado = 'PENDIENTE'`. | Sin el filtro de estado, al reejecutar el script o simular nuevas órdenes, las solicitudes históricas ya aprobadas o rechazadas se reevaluarían contra el nuevo snapshot, violando el principio de inmutabilidad histórica y la idempotencia de la cola de sincronización. |
| **4** | *"¿Cómo manejar la eliminación de productos en el servidor para que la tablet se entere sin romper los pedidos viejos?"* | Sugirió borrar físicamente (`DELETE FROM producto_cache`) las filas que ya no vienen en el snapshot del servidor. | **DESCARTADO CON FUNDAMENTO.** Rompe la integridad referencial de los borradores locales. | Si se eliminan físicamente los productos del catálogo local, cualquier borrador previo que contenga dicho producto violará la restricción `FOREIGN KEY (producto_id) REFERENCES producto_cache(id)`. Se implementó el patrón de **Lápidas (Tombstones)** con `eliminado = 1` y `disponible = 0`: el producto desaparece de la vista comercial de venta, pero su registro persiste para soporte referencial. |

---

## 2. Reflexión sobre el Proceso de Co-Programación con IA

1. **Supervisión de Reglas de Negocio:** Las herramientas de IA tienden por defecto a simplificar flujos generando arquitecturas bidireccionales directas (donde el cliente escribe en el servidor). La intervención humana fue crucial para hacer valer la premisa asimétrica de *"el móvil propone, el servidor dispone"*.
2. **Tipado y Rigor Numérico:** En SQLite, los modelos de lenguaje suelen ignorar las capacidades modernas del motor (`STRICT`, enteros en centavos, `PRAGMA foreign_keys = ON`). La especificación previa en Kiro garantizó que el código generado se apegara a los estándares de la industria y las directivas de la cátedra.
3. **Verificación Empírica:** Ningún bloque de código sugerido fue adoptado sin contrastación previa mediante ejecución real en consola contra PostgreSQL 17 y SQLite 3.50+, comprobando la inalterabilidad de los 80.000 pedidos y el stock central.
