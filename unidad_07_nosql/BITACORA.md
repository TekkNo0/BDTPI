# BITÁCORA — Uso de Inteligencia Artificial en el TP Unidad 7 (Food Store)

**Alumno:** Maximiliano Nardez  
**Materia:** Base de Datos II — Unidad 7: NoSQL y nuevas formas de almacenamiento  
**Proyecto:** Food Store  
**Motores:** PostgreSQL 17 (Relacional) y MongoDB 9.0+ / mongosh 2.14+ (Documental NoSQL)  
**Herramienta de IA utilizada:** Asistente de IA (Antigravity / Gemini)  
**Control de versiones:** Git — Repositorio: `https://github.com/TekkNo0/TPU7`  

---

## 1. Tabla Consolidada de Uso de IA (Formato obligatorio de 3 columnas)

A continuación se resume la interacción técnica mantenida con la herramienta de IA a lo largo de las distintas etapas del trabajo práctico, detallando las propuestas del modelo y las intervenciones, ajustes y correcciones humanas aplicadas:

| Prompt enviado a la IA | Respuesta relevante recibida (resumida) | Validación o corrección humana aplicada |
|---|---|---|
| **[Parte 1 — Diseño del Modelo Documental]:** *"Proponé el esquema de la colección documental `pedidos` en MongoDB a partir de las tablas `pedido`, `detalle_pedido`, `usuario` y `producto` de PostgreSQL. ¿Conviene embeber o referenciar?"* | Sugirió desnormalizar e incrustar las líneas de pedido (`items`) y un subdocumento `cliente`, pero propuso generar un `_id` con `ObjectId()` automático y referenciar `producto_id` sin guardar el nombre ni el precio histórico en la línea. | **CORREGIDO POR EL EQUIPO:** Se rechazó omitir el precio histórico. Si el precio cambia en el catálogo, el pedido se desvirtuaría. Se forzó la inclusión de `precio_unitario` histórico y `producto_nombre` embebido. Además, se forzó `_id: pedido_id` (entero original de PostgreSQL) para conservar trazabilidad biyectiva y evitar mapeos artificiales. |
| **[Parte 1 — Reglas de Integridad]:** *"Identificá dos reglas de integridad relacionales críticas que deben subsistir al migrar a MongoDB y justificá qué datos deben embeberse."* | Señaló la consistencia del total y sugirió validar con un script previo en la aplicación; justificó embeber únicamente para ganar velocidad de lectura. | **COMPLEMENTADO TÉCNICAMENTE:** Se profundizó la justificación con la documentación oficial de MongoDB: (1) Localidad de datos en disco (WiredTiger) que reduce I/O en lecturas de pedidos completos; (2) Atomicidad ACID a nivel de documento único que permite confirmar el pedido y sus 10 líneas en un solo paso transaccional sin bloqueos distribuidos. |
| **[Parte 2 — Consultas en MongoDB]:** *"Generá las 4 consultas de la Consigna 4 para mongosh: listar todos con id/estado, filtrar por CONFIRMADO, buscar por producto en arreglo de items y buscar por total > 15000."* | Proveyó las sintaxis con `db.pedidos.find()`, pero para buscar el producto en el arreglo propuso usar `$elemMatch` innecesariamente complejo: `db.pedidos.find({ items: { $elemMatch: { producto_id: 8 } } })`. | **OPTIMIZADO TÉCNICAMENTE:** Para coincidencia de un único campo dentro de un array de subdocumentos en MongoDB, la sintaxis directa con dot notation (`{ "items.producto_id": 8 }`) es más legible, estándar e idiomática. Además, se adaptó el script para ejecución no interactiva con `db.getSiblingDB("foodstore")` evitando fallos con la sentencia interactiva `use foodstore`. |
| **[Parte 2 — Consultas en PostgreSQL y Comparación]:** *"Escribí las consultas equivalentes en PostgreSQL para filtrar por estado CONFIRMADO y por producto_id = 8, y explicá por qué difieren las cantidades obtenidas."* | Generó `SELECT * FROM pedido WHERE estado = 'CONFIRMADO'` y advirtió que PostgreSQL devolvería miles de filas mientras que MongoDB devolvería solo 5, atribuyéndolo a 'incompatibilidad de motores'. | **CORRECCIÓN CONCEPTUAL HUMANA:** Se corrigió el diagnóstico de la IA. La diferencia no es una incompatibilidad del motor ni del modelo, sino una **divergencia de alcance**: la tabla PostgreSQL tiene 80.000 pedidos y a MongoDB se migró un subconjunto de 10 pedidos. Se implementaron ambas variantes (acotada al subconjunto `id BETWEEN 1 AND 10` y global), demostrando que en el mismo universo de datos la coincidencia de cardinalidad e identificadores es del 100%. |
| **[Parte 3 — Evaluación de Tecnología e IA]:** *"Compara PostgreSQL y MongoDB para el almacenamiento y consulta de pedidos en Food Store, considerando acceso frecuente a pedidos completos e integridad de precios."* | Afirmó que "MongoDB no soporta transacciones ACID ni integridad referencial para pedidos" y que "PostgreSQL siempre es lento por culpa de los múltiples JOINs". | **REFUTADO Y CONTRASTADO CON DOC OFICIAL:** Se desmintieron ambas afirmaciones: (1) MongoDB soporta transacciones ACID a nivel de documento único nativamente y Multi-Document Transactions desde la versión 4.0; (2) En PostgreSQL 17, los JOINs por PK/FK se resuelven en memoria vía Index Scan en < 1 ms, y pueden devolverse como JSON jerárquico directo con `jsonb_build_object()`. |

---

## 2. Desarrollo Detallado por Partes

### Parte 1 · Modelo Documental y Migración
- **Aporte de la IA:** La IA aportó una estructura preliminar en JSON que ayudó a visualizar la jerarquía de anidamiento.
- **Validación humana:** Se garantizó que la estructura conserve las claves de origen (`_id: pedido_id`, `usuario_id`, `producto_id`, `detalle_id`), respetando rigurosamente los importes originales de PostgreSQL. Se implementó un script de migración en Python (`migrar_datos.py`) y su correspondiente script nativo en JavaScript (`consultas_mongodb.js`) con `insertMany()`.

### Parte 2 · Consultas y Verificación
- **Aporte de la IA:** Proporcionó ejemplos de operadores de consulta en MongoDB (`$gt`, proyecciones) y sintaxis de agregación.
- **Validación humana:** Se ejecutaron ambas baterías de consultas en consolas reales (`mongosh` 2.14.1 contra MongoDB 9.0.4 y `psql` contra PostgreSQL 17). Se construyó la tabla comparativa de verificación exigida por la cátedra, corroborando la coincidencia exacta de identificadores `[1, 2, 3, 4, 5]` para estado `CONFIRMADO` y `[1]` para producto `8`.

### Parte 3 · Evaluación Tecnológica y Fact-Checking
- **Aporte de la IA:** Generó el marco argumentativo inicial para la comparación relacional vs NoSQL.
- **Validación humana:** Se realizó un riguroso *fact-checking* contrastando las afirmaciones de la IA contra la documentación oficial de MongoDB (sección *Data Modeling - Embedding* y *Atomicity and Transactions*) y de PostgreSQL (optimizador de consultas y tipos JSONB). Se redactó la conclusión final técnica con un estricto límite de 200 palabras (198 palabras) fundamentando la adopción de una arquitectura híbrida o políglota.
