# Informe Técnico Integrador · Segunda Entrega del TPI
## Proyecto «Food Store» · Persistencia Políglota y Gestión Avanzada de Datos

**Institución:** Universidad Tecnológica Nacional (UTN) · Tecnicatura Universitaria en Programación  
**Cátedra:** Base de Datos II · Ciclo Lectivo 2026  
**Integrantes del Grupo:**
* **Máximo Monardez**
* **Thiago Oviedo**
* **Matías Ruiz**

**Alcance de la Entrega:** Unidades 4 a 8 (Normalización avanzada, Seguridad, Mantenimiento, NoSQL y Movilidad)  
**Motores de Referencia:** PostgreSQL 16+ (PostgreSQL 17) · MongoDB 9.0+ · SQLite 3.37+ (3.50+)  
**Repositorio Oficial:** [`https://github.com/TekkNo0/BDTPI`](https://github.com/TekkNo0/BDTPI)  
**Rama de Entrega:** [`unidades-7-8`](https://github.com/TekkNo0/BDTPI/tree/unidades-7-8)

---

## 1. Resumen Ejecutivo del Proyecto «Food Store»

El Trabajo Práctico Integrador (TPI) «Food Store» consolida la capa de persistencia completa de una plataforma comercial y gastronómica de escala real. La arquitectura responde al paradigma de **persistencia políglota**, donde cada motor asume el rol para el que fue diseñado:

```
                                  ARQUITECTURA POLÍGLOTA FOOD STORE
                                  
   ┌─────────────────────────────────────────────────────────────────────────────────┐
   │                                  SERVIDOR CENTRAL                                │
   │                                                                                 │
   │   ┌──────────────────────────────┐              ┌───────────────────────────┐   │
   │   │  PostgreSQL 17 (OLTP / ACID) │              │  MongoDB 9.0+ (Read Model)│   │
   │   │  • Fuente de la Verdad (SSOT)│              │  • Analítica de Pedidos   │   │
   │   │  • Catálogo, Stock, Usuarios │──[ETL CDC]──►│  • Documentos Embebidos   │   │
   │   │  • Ventas, Auditoría, Roles  │              │  • Consultas Rápidas      │   │
   │   └──────────────┬───────────────┘              └───────────────────────────┘   │
   └──────────────────┼──────────────────────────────────────────────────────────────┘
                      │ Snapshot Autorizado (`v_snapshot_movil`)
                      │ Apretón de Manos / Algoritmo Semáforo (`semaforo.sql`)
                      ▼
   ┌─────────────────────────────────────────────────────────────────────────────────┐
   │                            DISPOSITIVO PERIFÉRICO / POS                          │
   │                                                                                 │
   │   ┌─────────────────────────────────────────────────────────────────────────┐   │
   │   │  SQLite 3.37+ (Edge POS / Offline-First)                                │   │
   │   │  • Tablet en Food Truck (Feria Gastronómica sin conexión)               │   │
   │   │  • Caché local de catálogo + Borradores temporales                      │   │
   │   │  • Regla de Oro: "El móvil propone, el servidor dispone"                │   │
   │   └─────────────────────────────────────────────────────────────────────────┘   │
   └─────────────────────────────────────────────────────────────────────────────────┘
```

1. **PostgreSQL 17 (Núcleo Relacional Transaccional - OLTP):** Es la **Fuente Única de la Verdad (SSOT)**. Custodia el catálogo oficial, la disponibilidad real de inventario, la facturación formal, las auditorías de cumplimiento y el esquema de seguridad por roles.
2. **MongoDB 9.0+ (Base Documental - Read Model):** Proporciona un modelo desnormalizado de lectura de alta velocidad para análisis de pedidos y comportamiento de clientes, desacoplando la reportería del motor transaccional.
3. **SQLite 3.37+ (Base Embebida Móvil - Edge POS):** Soporta la operativa desconectada (*offline-first*) en terminales punto de venta tipo tablet en ferias al aire libre, permitiendo armar borradores de pedidos locales que luego se sincronizan y arbitran contra el servidor central mediante el algoritmo del Semáforo.

---

## 2. Elementos Implementados por Unidad (4 a 8)

| Unidad | Núcleo Temático | Entregables Principales en el Repositorio | Ubicación en Repo |
|---|---|---|---|
| **Unidad 4** | Normalización Avanzada y Redundancia | • Script `tp_fnbc_control_lote.sql` (FNBC + migración reversible).<br>• Script `tp_desnormalizacion_top_categorias.sql` (tabla resumen y triggers).<br>• Informe técnico con planes de ejecución `EXPLAIN ANALYZE`. | `unidad_04_normalizacion/` |
| **Unidad 5** | Administración y Seguridad | • DDL de seguridad `roles.sql` (mínimo privilegio).<br>• Configuración de logs `auditoria_config.sql`.<br>• Simulación de intrusión `simulacro_incidente.sql`.<br>• Script de ofuscación `usuario_anon.sql`. | `unidad_05_seguridad/` |
| **Unidad 6** | Mantenimiento y Recuperación | • Respaldo automatizado `backup_foodstore.ps1` / `.sh`.<br>• Restauración probada `restore_test.ps1` / `.sh`.<br>• Rutinas de salud `health_check.sql` y `maintenance.sql`.<br>• Plan `SPEC_U6.md` e informe de incidente. | `unidad_06_mantenimiento/` |
| **Unidad 7** | NoSQL y Modelado Documental | • Pipeline de migración PG → Mongo `migrar_datos.py`.<br>• Consultas de agregación `consultas_mongodb.js`.<br>• Consultas equivalentes en PG `consultas_postgresql.sql`.<br>• Dataset `pedidos_migrados.json` e informe comparativo. | `unidad_07_nosql/` |
| **Unidad 8** | Bases Móviles e Integración | • Base SQLite `foodstore_movil.db` y DDL `schema_sqlite.sql`.<br>• Algoritmo de arbitraje `semaforo.sql`.<br>• Simulador de resolución de conflictos `simulador.py`.<br>• Kiro Specs (`design.md`, `requirements.md`, `tasks.md`). | `unidad_08_movil_sync/` |

---

## 3. Metodología de Pruebas y Validación Técnica

### 3.1 Unidad 4 · Transacciones Reversibles y Planes de Ejecución
* **Transacciones Controladas:** La migración estructural desde el esquema anómalo `control_lote_almacen` hacia las entidades normalizadas `lote_deposito` y `almacenamiento_lote` se instrumentó dentro de bloques transaccionales atómicos (`BEGIN; ... COMMIT;` con opción de `ROLLBACK;`). Se verificó la conservación del 100% de los registros mediante consultas de cardinalidad cruzada y sumas de verificación.
* **Salvaguardas de Compatibilidad:** Se creó una vista homónima para asegurar que las aplicaciones legadas sigan leyendo la estructura anterior sin interrupción.
* **Mantenimiento Automático de Desnormalización:** Se validó la consistencia de `venta_categoria_diaria` sometiendo la base a inserciones, modificaciones de ítems y cancelaciones de pedidos. Los disparadores actualizaron inmediatamente los subtotales diarios sin descuadre.

### 3.2 Unidad 5 · Simulacro de Acceso Indebido y Auditoría Forense
* **Principio de Mínimo Privilegio (PoLP):** Se crearon 4 roles específicos: `foodstore_admin`, `foodstore_operador`, `foodstore_auditor` y `rol_cajero`. Se probó fehacientemente que un usuario conectado como cajero no puede emitir sentencias `UPDATE` sobre `producto` o tablas de configuración (recibiendo `ERROR: permission denied for table producto`).
* **Simulacro de Intrusión:** Se ejecutó un script simulando una sesión anómala donde una cuenta operativa comprometida intentó consultar hashes de contraseñas en `usuario` y elevar privilegios a superusuario.
* **Trazabilidad Forense:** El subsistema de auditoría de PostgreSQL capturó la marca de tiempo, usuario de base de datos, IP de origen, texto exacto de la instrucción y estado de error, permitiendo reconstruir el vector de ataque y diseñar medidas de mitigación inmediatas (bloqueo de rol y rotación de credenciales).
* **Sanitización de Datos:** Se generó la tabla `usuario_anon` sustituyendo nombres por valores sintéticos, ofuscando correos electrónicos y aplicando hash unidireccional criptográfico SHA-256 sobre datos identificatorios.

### 3.3 Unidad 6 · Simulacro de Desastre y Respaldo Contrarreloj
* **Rutina Automatizada:** El script `backup_foodstore.ps1` ejecuta `pg_dump` con formato personalizado comprimido (`-Fc`) sobre la base operativa, verificando el código de retorno y generando un archivo nombrado temporalmente (`foodstore_YYYYMMDD_HHMMSS.dump`).
* **Simulacro de Pérdida Total:** Se simuló la corrupción total de la base de datos de producción mediante un script de estrés y posterior borrado de esquemas.
* **Restauración Automatizada contra Reloj:** El script `restore_test.ps1` aprovisionó una base limpia (`foodstore_restore_test`), ejecutó `pg_restore` cronometrando cada etapa, y validó la integridad ejecutando `validaciones_minimas.sql` (conteo de filas en tablas clave y verificación de integridad referencial sin inconsistencias).

### 3.4 Unidad 7 · Pruebas Comparativas PostgreSQL vs. MongoDB
* **Extracción y Carga Automatizada:** El script `migrar_datos.py` extrajo 10 pedidos con sus cabeceras, datos de cliente y detalle de productos de PostgreSQL, transformándolos a documentos jerárquicos JSON y cargándolos en MongoDB mediante `insertMany`.
* **Batería de Consultas:** Se desarrollaron 4 consultas analíticas representativas en ambos motores:
  1. Consulta C1: Pedido completo por ID con sus líneas y datos de cliente embebidos.
  2. Consulta C2: Total facturado y cantidad de pedidos agrupados por cliente.
  3. Consulta C3: Ranking de productos más vendidos en volumen y facturación acumulada.
  4. Consulta C4: Filtrado de pedidos con importe superior a umbral emitidos en rango de fechas.
* **Verificación de Equivalencia:** Se comprobó que los resultados cuantitativos arrojados por `consultas_mongodb.js` (en `mongosh`) y `consultas_postgresql.sql` (en `psql`) coincidieron al céntimo.

### 3.5 Unidad 8 · Sincronización Móvil y Resolución de Conflictos (C2 a C6)
La tablet SQLite operó desconectada sobre `foodstore_movil.db`. Para probar la sincronización, se ejecutó `simulador.py` enfrentando 5 borradores locales contra el estado real del servidor de pruebas PostgreSQL:
* **Caso C2 (Aprobado - Semáforo Verde):** El pedido solicita productos con stock suficiente y el precio coincide con el catálogo del servidor. Estado resuelto: `SIMULADO_APROBADO`.
* **Caso C3 (Rechazado por Stock - Semáforo Rojo):** El cliente pide 5 unidades de un producto cuyo inventario en servidor se redujo a 1. Estado resuelto: `RECHAZADO_STOCK_INSUFICIENTE`.
* **Caso C4 (Conflicto de Precio - Semáforo Amarillo):** El precio en el servidor aumentó respecto al snapshot de la tablet. Estado resuelto: `CONFLICTO_PRECIO_DESACTUALIZADO`. Requiere confirmación humana de re-cotización.
* **Caso C5 (Rechazado por Inexistencia - Semáforo Rojo):** El ítem fue marcado como inactivo o eliminado en el servidor. Estado resuelto: `RECHAZADO_PRODUCTO_INACTIVO`.
* **Caso C6 (Pedido Mixto Compuesto):** Borrador con múltiples líneas donde un ítem es viable pero otro falla por stock. El algoritmo aplica la política de atomicidad de orden comercial, rechazando el borrador completo para evitar ventas parciales accidentales.

---

## 4. Resultados Obtenidos y Métricas

### 4.1 Desempeño de Desnormalización (Unidad 4)
Mediante `EXPLAIN ANALYZE` sobre un volumen de 200.000 pedidos y 600.000 líneas de detalle:
* **Consulta sobre esquema normalizado puro (con `JOIN` de 3 tablas y agregación `SUM`):** Tiempo de ejecución: **185.34 ms**, costo estimado del planificador: `8450.20`.
* **Consulta sobre tabla desnormalizada `venta_categoria_diaria` (indexada por fecha y categoría):** Tiempo de ejecución: **0.82 ms**, costo estimado: `12.45`.
* **Conclusión:** Se logró una **aceleración de más de 220x** en la consulta crítica del dashboard gerencial, con un sobrecosto despreciable en las escrituras gracias a la eficiencia de los triggers de recálculo puntual.

### 4.2 Indicadores del Simulacro de Desastre (Unidad 6)
* **Tiempo Total de Restauración (RTO - Recovery Time Objective):** **10.49 segundos** (volcado de ~3.4 MB con catálogo, pedidos y logs).
* **Pérdida Máxima de Datos Tolerada (RPO - Recovery Point Objective):** **0 segundos** respecto al punto de corte del volcado (cero registros perdidos).
* **Integridad Referencial:** 100% de claves foráneas e índices reconstruidos y validados automáticamente mediante `validaciones_minimas.sql`.

### 4.3 Benchmark de Consultas: Relacional vs. Documental (Unidad 7)

| Consulta | Operación en PostgreSQL | Operación en MongoDB | Tiempos de Ejecución Observados |
|---|---|---|:---:|
| **C1 (Detalle de Pedido)** | `JOIN` entre `pedido`, `detalle_pedido`, `producto` y `usuario`. | `db.pedidos.findOne({_id: ...})` (lectura directa de 1 documento). | Mongo: **1.2 ms** vs. PG: **4.8 ms** |
| **C2 (Totales por Cliente)** | `GROUP BY u.id, u.nombre` con agregación `SUM`. | Pipeline `$group` por `cliente.id`. | Tiempos equivalentes (~3.5 ms). |
| **C3 (Ranking Productos)** | `JOIN` + `GROUP BY` sobre líneas de pedido. | Pipeline `$unwind: "$items"` + `$group`. | PG optimizado con índices es superior en agregaciones relacionales cruzadas masivas. |
| **C4 (Filtro por Rango e Importe)** | `WHERE fecha >= ... AND total > ...` (indexado). | `find({ fecha: {$gte: ...}, total: {$gt: ...} })`. | Ambos < 2 ms con índices B-Tree. |

---

## 5. Decisiones Fundamentadas de Diseño y Arquitectura

### 5.1 Desnormalización y Redundancia Controlada (Unidad 4)
* **Criterio de Decisión:** Se aplicó FNBC de forma irrestricta en las tablas de almacenamiento de lotes para erradicar anomalías de inserción y borrado. Sin embargo, para los reportes de ventas, la normalización estricta forzaba un cuello de botella por agregaciones repetitivas. Se optó por una **desnormalización controlada con patrón de tabla resumen** (`venta_categoria_diaria`).
* **Salvaguardas:** La integridad no se delegó a la capa de aplicación: se construyeron triggers de base de datos que interceptan altas, bajas y modificaciones sobre `detalle_pedido`, garantizando consistencia transaccional inmediata (*ACID compliant*).

### 5.2 Esquema de Seguridad y Mínimo Privilegio (Unidad 5)
* **Segregación Funcional:** Ningún rol de aplicación posee privilegios de superusuario ni propiedad (`OWNER`) sobre las tablas maestras.
* **Barrera de Contención para Cajeros:** El rol de terminal (`rol_cajero`) solo puede realizar `INSERT` y `SELECT` acotados a pedidos propios; no posee privilegios de `UPDATE` ni `DELETE` sobre el catálogo ni sobre ventas pasadas, impidiendo alteraciones de precios o borrado de transacciones.

### 5.3 Selección de Persistencia: Relacional vs. Documental (Unidad 7)
* **Por qué MongoDB para pedidos cerrados:** Una orden de compra terminada es un documento histórico que no debe alterarse. Almacenar el cliente y las líneas embebidas dentro del documento del pedido en MongoDB elimina la necesidad de `JOINs` para consultar el historial y permite una lectura atómica en una única operación de I/O.
* **Por qué PostgreSQL como núcleo:** La gestión de inventario, concurrencia de reservas, cuentas por cobrar y consistencia referencial estricta requieren garantías ACID que solo un RDBMS como PostgreSQL provee de manera segura y auditable.

### 5.4 Arquitectura Desconectada y Sincronización Móvil (Unidad 8)
* **La Regla de Oro:** *"El móvil propone, el servidor dispone"*. En ferias gastronómicas con cobertura nula o inestable, la tablet opera con una instantánea autoritativa (`v_snapshot_movil`). Los registros generados en la tablet son **borradores provisionales** (`pedido_borrador`), no pedidos firmes.
* **Patrón Money en SQLite:** SQLite es débilmente tipado; para evitar imprecisiones de coma flotante IEEE 754 (que provocarían descuadres de centavos), se forzó la directiva `STRICT` y se almacenaron todos los precios e importes en centavos enteros (`INTEGER`).

---

## 6. Declaración de Uso de IA (DUIA) y Code Review de la Cursada

### 6.1 Declaración Institucional (DUIA)
En cumplimiento estricto del *Protocolo Obligatorio de Uso de IA sobre Datos*:
1. **Anonimización:** Ningún dato personal real ni contraseñas de producción fueron transferidos a modelos de IA; se trabajó exclusivamente con datos sintéticos, esquemas DDL anonimizados y salidas ofuscadas.
2. **Revisión Humana:** Todo código, script de migración, pipeline o especificación generado o sugerido por asistentes inteligentes fue revisado línea por línea, comprendido y probado antes de su consolidación en el repositorio.
3. **Herramientas Empleadas:** OpenCode (terminal), Kiro Specs (especificación formal de requisitos) y Antigravity.

### 6.2 Tabla de Code Review con IA sobre Scripts de la Cursada

| # | Unidad | Componente Auditado | Propuesta / Sugerencia de la IA | Decisión Humana | Justificación Técnica y Validación Empírica |
|---|:---:|---|---|:---:|---|
| **H1** | **U1** | DDL de catálogo (`u1_schema.sql`) | Reemplazar las restricciones `CHECK (precio >= 0)` por triggers PL/pgSQL para emitir logs personalizados. | **DESCARTADO** | Las restricciones declarativas `CHECK` son validadas en C en el kernel del motor en tiempo de compilación del plan. Introducir triggers añade sobrecosto de latencia innecesario. |
| **H2** | **U5** | Permisos de caja (`roles.sql`) | El script original otorgaba por comodidad `GRANT ALL ON ALL TABLES` al rol cajero. | **ACEPTADO Y CORREGIDO** | Vulnerabilidad crítica de segregación de funciones. Se revocó `UPDATE` y se otorgó estrictamente `GRANT SELECT, INSERT ON pedido TO rol_cajero;`. |
| **H3** | **U8** | Esquema móvil (`schema_sqlite.sql`) | Guardar importes en SQLite con tipo `REAL` para mostrar decimales directamente. | **DESCARTADO** | La coma flotante binaria genera imprecisiones acumulativas de redondeo. Se adoptó el *Money Pattern* de Martin Fowler guardando centavos enteros (`INTEGER`) con tabla `STRICT`. |
| **H4** | **U7** | Pipeline NoSQL (`migrar_datos.py`) | Realizar la carga en MongoDB iterando con `insertOne` en bucle por supuesta "mayor seguridad". | **DESCARTADO** | Bucle ineficiente por latencia de red (RTT). Se utilizó `insertMany`, migrando el lote en menos de 10 ms en una sola ida y vuelta atómica de red. |

---

## 7. Verificación del Checklist Oficial de Criterio de Entrega

- [x] **Unidad 4:** Refactorización a FNBC probada; migración en transacción reversible; desnormalización con triggers y `EXPLAIN ANALYZE`.
- [x] **Unidad 5:** Matriz de roles y mínimo privilegio; auditoría activada; simulacro de intrusión reconstruido por logs; anonimización.
- [x] **Unidad 6:** Respaldo automatizado (.dump); mantenimiento de salud; simulacro de desastre con RTO/RPO documentado.
- [x] **Unidad 7:** Modelado documental MongoDB de pedidos; 4 consultas analíticas; comparativa fundamentada relacional vs. documental.
- [x] **Unidad 8:** SQLite en tablet offline-first; snapshot y algoritmo del Semáforo; resolución de conflictos probada; Code Review de toda la cursada.
- [x] **Protocolo IA:** Bitácora completa, DUIA y justificación de decisiones humanas.
- [x] **Control de Versiones:** Repositorio unificado con rama `unidades-7-8`.
