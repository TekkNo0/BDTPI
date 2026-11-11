# Informe Técnico Académico - Trabajo Práctico N.º 8
## Food Store en la feria: la base de la tablet y el cierre de la capa de datos

**Institución:** Universidad Tecnológica Nacional (UTN) · Tecnicatura Universitaria en Programación  
**Cátedra:** Base de Datos II · Ciclo Lectivo 2026  
**Estudiante:** Maximiliano Nardez  
**Herramientas:** PostgreSQL 16+ (17.x) · SQLite 3.37+ (3.50+) · MongoDB 9.0+ · Python 3.14+  

---

## 1. Consigna 1.a · Análisis de Datos en Tránsito: Qué Datos Viajan

En una arquitectura desconectada (*offline-first*) para terminales de punto de venta (POS) en entornos móviles, resulta crítico delimitar qué información debe transferirse hacia el dispositivo periférico y cuál debe permanecer resguardada en el servidor central.

### 1.1 Matriz de Atributos y Criterio de Selección

| Entidad / Atributo | ¿Viaja a la Tablet? | Justificación Técnica de Negocio y Seguridad |
|---|:---:|---|
| **`producto.id`** | **SÍ** | Identificador unívoco obligatorio para relacionar las líneas del borrador (`item_borrador.producto_id`). |
| **`producto.nombre`** | **SÍ** | Denominación visual indispensable para que el cajero reconozca los artículos en el catálogo offline. |
| **`producto.precio` (en centavos)** | **SÍ** | Se transfiere convertido a centavos enteros (`precio_centavos`) para exhibir el precio de lista y calcular subtotales provisionales sin errores de punto flotante. |
| **`producto.stock` (`stock_visto`)**| **SÍ** | Inventario observado al momento de la instantánea; permite a la interfaz advertir al cajero si un producto está agotado. |
| **`producto.activo` / `disponible`**| **SÍ** | Proyectado como flags binarios (`disponible`, `eliminado`) para implementar el patrón de lápidas y ocultar productos inactivos. |
| **`producto.categoria_id`** | **NO** | Metadato organizativo interno del servidor; la tablet opera con un catálogo plano simplificado para agilizar las ventas en feria. |
| **`producto.metadata` (JSONB)** | **NO** | Atributos comerciales avanzados, trazabilidad de proveedores y configuraciones internas innecesarias en la tablet. |
| **`usuario.*` (clientes y perfiles)**| **NO** | **Restricción estricta de seguridad y privacidad.** Nombres, emails, teléfonos, contraseñas y roles jamás se transfieren a dispositivos móviles expuestos al público. |
| **`pedido` / `detalle_pedido` (histórico)**| **NO** | Historial de facturación de la empresa; la tablet solo gestiona los borradores generados en el turno de trabajo actual. |
| **`auditoria_*` (tablas de log)** | **NO** | Tablas de cumplimiento normativo y control fiscal que pertenecen exclusivamente al ámbito transaccional del servidor central. |

### 1.2 Fundamentación Arquitectónica y Fuente de la Verdad
El filtrado riguroso de columnas responde al principio de **minimización de datos y reducción de superficie de ataque**: si la tablet sufre un robo o extravío físico durante la feria gastronómica, ningún dato sensible de clientes ni registros financieros históricos de la empresa queda expuesto.  
Asimismo, se ratifica la premisa de soberanía: **PostgreSQL es la única Fuente de la Verdad (SSOT - Single Source of Truth)**. La tablet almacena únicamente una instantánea de lectura desactualizable por diseño (*stale read cache*) y borradores que representan meras intenciones de compra; las decisiones definitivas sobre disponibilidad de inventario, tarifas aplicables y confirmación fiscal son potestad exclusiva de PostgreSQL.

---

## 2. Consigna 2.c · Simulación y Verificación de los Casos de Sincronización (C2 a C6)

La sincronización se evaluó de forma determinística en `foodstore_movil.db` contra el servidor de pruebas PostgreSQL (`foodstore_u8_pruebas`), aplicando la vista `v_snapshot_movil` y el algoritmo del Semáforo (`semaforo.sql`).

```sql
-- Definición de la vista en PostgreSQL 17 (Consigna 2.a):
CREATE OR REPLACE VIEW v_snapshot_movil AS
SELECT 
    id,
    nombre,
    ROUND(precio * 100)::INTEGER AS precio_centavos,
    stock,
    (activo AND stock > 0)::BOOLEAN AS disponible,
    (NOT activo)::BOOLEAN AS eliminado,
    TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS') AS fecha_copia
FROM producto
ORDER BY id;
```

---

### Caso C2 · Modificación de Precio en el Servidor (Conflicto y Re-cotización)
- **Escenario:** El cliente confecciona el borrador `BORR-C2` con 1 unidad del Producto 1 con precio visto inicial de \$537.07 (`53707` centavos). Posteriormente, en el servidor central se incrementa el precio a \$650.00 (`65000` centavos).
- **Comandos ejecutados:**
  ```sql
  -- 1. Servidor (PostgreSQL):
  UPDATE producto SET precio = 650.00 WHERE id = 1;
  -- 2. Exportación de snapshot y corrida del semáforo en SQLite:
  -- Se evalúa la solicitud inicial REQ-C2-01
  ```
- **Resultado obtenido:** `CONFLICTO` en `REQ-C2-01` con motivo: `Precio modificado en prod 1 (visto: $537.07, servidor: $650.00)`.
- **Resolución con el cliente:** El cliente es notificado y acepta abonar la nueva tarifa. En la tablet se actualiza el borrador local y se emite la solicitud `REQ-C2-02`:
  ```sql
  UPDATE item_borrador SET precio_centavos_visto = 65000 
  WHERE id_local = 'BORR-C2' AND producto_id = 1;
  INSERT INTO cola_sync VALUES ('REQ-C2-02', 'BORR-C2', 'PENDIENTE', NULL);
  ```
- **Resultado final:** `SIMULADO_APROBADO` en `REQ-C2-02`. La solicitud original permanece en `CONFLICTO` como evidencia de auditoría.
- **Explicación técnica:** La discrepancia tarifaria es una condición no fatal (amarillo): no compromete el stock físico pero requiere la aceptación explícita del consumidor antes de generar una obligación comercial.

---

### Caso C3 · Quiebre de Stock en el Servidor
- **Escenario:** Se confecciona el borrador `BORR-C3` solicitando 10 unidades del Producto 2, cuando el servidor registra un inventario disponible de solo 6 unidades.
- **Comandos ejecutados:**
  ```sql
  INSERT INTO pedido_borrador VALUES ('BORR-C3', 'cajero_1', 'TARJETA', '2026-11-06 16:10:00');
  INSERT INTO item_borrador VALUES ('BORR-C3', 2, 10, 57414);
  INSERT INTO cola_sync VALUES ('REQ-C3-01', 'BORR-C3', 'PENDIENTE', NULL);
  ```
- **Resultado obtenido:** `RECHAZADO` con motivo: `Stock insuficiente para prod 2 (solicitado: 10, disponible: 6)`.
- **Explicación técnica:** Se activa el semáforo rojo (`i.cantidad > s.stock`). El sistema previene la sobreventa física informando al cajero de inmediato para que ajuste la cantidad con el cliente antes de confirmar.

---

### Caso C4 · Baja Lógica de Producto mediante Lápida (Tombstone)
- **Escenario:** Se genera el borrador `BORR-C4` con el Producto 3 cuando estaba activo. A continuación, el administrador del servidor lo da de baja lógica (`activo = FALSE`).
- **Comandos ejecutados:**
  ```sql
  -- En PostgreSQL:
  UPDATE producto SET activo = FALSE WHERE id = 3;
  -- En SQLite tras importar nueva instantánea:
  -- Se evalúa la solicitud REQ-C4-01
  ```
- **Resultado obtenido:** `RECHAZADO` con motivo: `Producto 3 dado de baja (lápida)`.
- **Comportamiento en catálogo:** Al actualizar `producto_cache`, el Producto 3 recibe `eliminado = 1` y `disponible = 0`. La consulta del catálogo comercial (`WHERE disponible = 1 AND eliminado = 0`) ya no lo muestra, pero la fila física permanece en la base SQLite preservando las claves foráneas históricas.
- **Explicación técnica:** Las lápidas permiten la sincronización unidireccional de borrados lógicos en bases distribuidas sin quebrar la integridad referencial (`FOREIGN KEY`) de documentos preexistentes.

---

### Caso C5 · Borrador Válido sin Alteraciones
- **Escenario:** El cliente solicita 1 unidad del Producto 4 cuyo stock (12) y precio (\$648.28) coinciden exactamente entre el borrador y el servidor.
- **Comandos ejecutados:**
  ```sql
  INSERT INTO pedido_borrador VALUES ('BORR-C5', 'cajero_1', 'EFECTIVO', '2026-11-06 16:20:00');
  INSERT INTO item_borrador VALUES ('BORR-C5', 4, 1, 64828);
  INSERT INTO cola_sync VALUES ('REQ-C5-01', 'BORR-C5', 'PENDIENTE', NULL);
  ```
- **Resultado obtenido:** `SIMULADO_APROBADO` con motivo: `Validación exitosa: stock y precios coinciden con servidor`.
- **Explicación técnica:** En ausencia de condiciones rojas o amarillas, el semáforo certifica que la orden es apta para ser encolada formalmente.

---

### Caso C6 · Reenvío de Solicitud Idéntica e Idempotencia
- **Escenario:** Se simula un reenvío duplicado por problemas de red intentando insertar nuevamente la solicitud `REQ-C5-01` en `cola_sync`.
- **Comandos ejecutados:**
  ```sql
  INSERT INTO cola_sync VALUES ('REQ-C5-01', 'BORR-C5', 'PENDIENTE', NULL);
  ```
- **Resultado obtenido:** Fallo inmediato de restricción de integridad:  
  `sqlite3.IntegrityError: UNIQUE constraint failed: cola_sync.solicitud_uuid`.  
  Asimismo, re-ejecutar el script del semáforo no alteró el estado previamente consolidado (`SIMULADO_APROBADO`).
- **Explicación y Protección Real en Servidor (Parada 8):**  
  En un sistema de producción distribuido, la protección real contra duplicaciones reside en el servidor central PostgreSQL mediante una tabla de ingesta transaccional (`ingesta_solicitudes`) con una restricción `UNIQUE (solicitud_uuid)`. Ante interrupciones de señal móvil donde el cliente no recibe el acuse de recibo HTTP y reintenta el envío, PostgreSQL procesa la orden mediante `ON CONFLICT (solicitud_uuid) DO NOTHING`, evitando duplicar cargos bancarios o rebajas de inventario.

---

### Verificación de Inmutabilidad en PostgreSQL
Tras ejecutar íntegramente la batería de pruebas y simulación, se ejecutó en la base de datos central PostgreSQL la siguiente consulta de auditoría:

```sql
SELECT 'Total de pedidos registrados' AS metrica, count(*) AS valor FROM pedido
UNION ALL
SELECT 'Suma total de stock físico', sum(stock) FROM producto;
```

**Resultado obtenido:**
- Total de pedidos: **80.000** (exactamente igual que antes de iniciar las pruebas).
- Suma de stock total: **2.490.000** (exactamente igual que antes de iniciar las pruebas).
- **Conclusión:** Se verifica fehacientemente la Regla de Oro: la base de la tablet operó con estricto desacoplamiento y no alteró en ningún momento el estado transaccional del servidor.

---

## 3. Consigna 3.a · Mapa de la Capa de Datos (PostgreSQL, MongoDB y SQLite)

El sistema Food Store consolida una **arquitectura de persistencia políglota** compuesta por tres motores complementarios:

| Motor | Rol Arquitectónico | Datos que Almacena | Soberanía (Quién Manda) |
|---|---|---|---|
| **PostgreSQL 17** | **Núcleo Transaccional (OLTP / ACID)** | Catálogo maestro de productos y categorías, inventario físico oficial, usuarios, roles, auditorías contables (`auditoria_*`), pedidos y cobranzas formalmente confirmadas. | **Máxima Autoridad (SSOT).** Manda sobre precios finales, asignación de stock, registro legal de ventas y control de acceso. |
| **MongoDB 9.0+ (Unidad 7)** | **Modelo de Lectura Desnormalizado (Read Model)** | Colección `pedidos` desnormalizada con documentos que embeben datos de cabecera, subdocumento de cliente y arreglo de líneas (`items`) con precio unitario histórico. | **Soberanía Delegada / Solo Lectura.** Es una vista materializada de consulta rápida para paneles gerenciales y analítica histórica; se nutre de forma asíncrona desde PostgreSQL. |
| **SQLite 3.37+ (Unidad 8)** | **Caché Periférica Desconectada (Edge POS)** | Instantánea local del catálogo (`snapshot_servidor`, `producto_cache`), borradores temporales (`pedido_borrador`, `item_borrador`) y cola de eventos (`cola_sync`). | **Soberanía Local Temporal.** Manda únicamente sobre sus borradores locales no sincronizados. No tiene autoridad sobre el servidor; sus estados resueltos son simulaciones de prefactibilidad. |

---

## 4. Consigna 3.b · Plan de Mantenimiento de la Capa de Datos

Como extensión al plan de mantenimiento diseñado en la Unidad 6, se integran las siguientes directivas para la arquitectura distribuida:

1. **Estrategia de Respaldo y Prueba de Restauración:**  
   - *PostgreSQL:* Se mantiene la política de la U6 con volcados lógicos diarios automatizados mediante `pg_dump -Fc` (`backup_foodstore.ps1`), retenidos por 7 días. La restauración se valida semanalmente de forma desatendida (`restore_test.ps1`) en una base aislada (`foodstore_restore_test`), verificando integridad referencial, conteo de filas y sumas de verificación.
   - *Tablets (SQLite):* La base `foodstore_movil.db` se considera un componente descartable respecto al catálogo maestro (se rehidrata en segundos desde el snapshot). Los borradores pendientes locales se preservan en almacenamiento cifrado del dispositivo.
   - *MongoDB:* Respaldo complementario mediante `mongodump --gzip` o regeneración programada desde PostgreSQL vía el pipeline ETL/CDC.

2. **Mitigación de Restauración Desfasada en PostgreSQL (Split-Brain Prevention):**  
   Cada instantánea exportada incluye el campo `fecha_copia` (o número de epoch del servidor). Al recuperar señal, la tablet realiza un apretón de manos (*handshake*) con el servidor. Si el servidor fue restaurado a un backup antiguo y reporta un timestamp o epoch anterior al último registro procesado por la tablet, esta **bloquea la sincronización automática de pedidos pendientes**, pasa los borradores a estado de contingencia manual para revisión humana, invalida la caché local y descarga una nueva instantánea del servidor restaurado. Esto impide ventas fantasmas contra inventario ya inexistente.

3. **Gobernanza y Frecuencia de Revisión de Conflictos:**  
   - *Nivel Operativo Inmediato (Cajero):* El operador del Food Truck resuelve las solicitudes en `CONFLICTO` (amarillo) en tiempo real notificando al cliente sobre variaciones de precio para re-cotizar el borrador, o en `RECHAZADO` (rojo) para ofrecer alternativas ante quiebres de stock.
   - *Nivel Supervisión Diaria (Encargado):* Al cierre de la jornada en la feria (cada 24 horas), el supervisor audita la cola consolidada para identificar incidencias recurrentes de conectividad, artículos con discrepancias de inventario o desajustes de precios.

---

## 5. Consigna 3.c · Code Review con IA sobre Scripts de la Cursada

Se realizó una auditoría estática exhaustiva asistida por IA sobre los scripts desarrollados a lo largo del cuatrimestre, sometiendo cada recomendación a verificación empírica en el motor:

### 5.1 Tabla Consolidada de Hallazgos

| # | Unidad | Componente / Script | Hallazgo / Sugerencia de la IA | Decisión | Motivo Técnico y Comprobación en Base de Datos |
|---|:---:|---|---|:---:|---|
| **H1** | **U1** | DDL de integridad (`u1_00_schema.sql`) | Reemplazar las restricciones `CHECK (precio >= 0)` y `CHECK (stock >= 0)` por triggers `BEFORE INSERT OR UPDATE`. | **DESCARTADO CON FUNDAMENTO** | Las restricciones `CHECK` declarativas se evalúan internamente en C en el kernel del motor sin el overhead de salto de contexto de funciones PL/pgSQL. Se comprobó intentando insertar `precio = -10`, resultando en bloqueo nativo inmediato (`ck_producto_precio_positivo`). |
| **H2** | **U5** | Esquema de roles y permisos (`roles.sql`) | El rol de cajero tenía privilegios de `UPDATE` sobre la tabla `producto`, posibilitando manipulación de precios desde la terminal. | **ACEPTADO Y CORREGIDO** | Vulnerabilidad crítica de seguridad y segregación de funciones. Se revocó `UPDATE` y se otorgó estrictamente `GRANT SELECT ON producto TO rol_cajero;`. Se comprobó con el usuario cajero intentando un `UPDATE`, arrojando `ERROR: permiso denegado`. |
| **H3** | **U8** | Esquema móvil SQLite (`schema_sqlite.sql`) | Almacenar importes monetarios en SQLite (`precio_centavos`) usando tipo `REAL` con decimales en lugar de enteros. | **DESCARTADO CON FUNDAMENTO** | El tipo `REAL` de SQLite utiliza coma flotante binaria IEEE 754 de 64 bits, la cual acumula inexactitudes por redondeo binario. Según el estándar de la industria (*Martin Fowler - Money Pattern*), la moneda debe guardarse en centavos enteros (`INTEGER`). |
| **H4** | **U7** | Pipeline de migración NoSQL (`migrar_datos.py`) | Usar inserciones unitarias en bucle (`insertOne`) en lugar de `insertMany` por supuesta 'mayor seguridad transaccional'. | **DESCARTADO CON FUNDAMENTO** | Genera un cuello de botella masivo por latencia de ida y vuelta de red (RTT). Con `insertMany` la migración de 10 pedidos tomó < 10 ms en un solo viaje de red garantizando atomicidad de lote en MongoDB. |

### 5.2 Profundización Técnica de Tres Hallazgos Clave

#### Hallazgo H1 (Unidad 1) · Restricciones Declarativas vs. Procedurales
- **Propuesta de la IA:** La IA argumentó que los triggers PL/pgSQL permitían capturar errores y emitir mensajes de log personalizados en una tabla de auditoría ante valores negativos de precio o stock.
- **Fundamento del Descarte:** Aunque los triggers ofrecen flexibilidad, en modelos transaccionales de alta concurrencia introducen penalizaciones de latencia inaceptables y mayor superficie de falla. La regla relacional debe resolverse al nivel más bajo posible del motor. Las cláusulas `CHECK (precio >= 0)` y `CHECK (stock >= 0)` son verificadas por el optimizador de PostgreSQL en tiempo de compilación del plan de inserción. Se verificó en consola que cualquier intento anómalo aborta la transacción limpiamente protegiendo la integridad del catálogo.

#### Hallazgo H2 (Unidad 5) · Privilegios Mínimos en Cuentas de Cajero
- **Propuesta de la IA:** Detectó que en los scripts iniciales de permisos de la Unidad 5, se había otorgado `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rol_cajero;` por comodidad en las pruebas de aula.
- **Implementación de la Corrección:** Se aplicó el principio de **Mínimo Privilegio (PoLP)**:
  ```sql
  REVOKE ALL ON ALL TABLES IN SCHEMA public FROM rol_cajero;
  GRANT SELECT, INSERT ON pedido, detalle_pedido TO rol_cajero;
  GRANT SELECT ON producto, categoria TO rol_cajero;
  ```
  Se comprobó que el cajero puede registrar transacciones pero queda inhabilitado para modificar listas de precios o alterar auditorías.

#### Hallazgo H3 (Unidad 8) · Aritmética Financiera en Motores Ligeros (Patrón Money)
- **Propuesta de la IA:** Sugirió que guardar importes como `REAL` simplificaba la presentación visual en la aplicación sin requerir divisiones intermedias por 100.
- **Fundamento del Descarte:** En sistemas de cobranza y facturación, las imprecisiones de coma flotante (p. ej., `0.10 + 0.20 = 0.30000000000000004`) provocan descuadres de caja y fallos en las comparaciones de igualdad estricta (`i.precio_centavos_visto = s.precio_centavos`). Guardar enteros en centavos bajo la directiva `STRICT` de SQLite 3.37+ asegura exactitud matemática absoluta, interoperabilidad limpia con PostgreSQL y cero discrepancias de redondeo.
