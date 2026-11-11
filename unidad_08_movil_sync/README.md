# Trabajo Práctico N.º 8: Food Store en la feria
## La base de la tablet y el cierre de la capa de datos
**Asignatura:** Base de Datos II · Tecnicatura Universitaria en Programación  
**Institución:** Universidad Tecnológica Nacional (UTN) · Ciclo Lectivo 2026  
**Alumno:** Maximiliano Nardez  
**Herramientas:** PostgreSQL 16+ (17.x) · SQLite 3.37+ (3.50+) · Python 3.12+ (3.14+) · Kiro Specs  

---

## 📖 De qué se trata el proyecto

El proyecto integrador **Food Store** sitúa su operativa en un Food Truck que comercializa productos en una feria gastronómica al aire libre sin cobertura de telefonía celular ni internet constante (*offline-first*).  
Para sostener la operación comercial continua:
1. Se estructura una base de datos local en SQLite dentro de la tablet del punto de venta (POS).
2. La tablet descarga previamente una foto o instantánea autoritativa del servidor (`v_snapshot_movil` desde PostgreSQL).
3. Los cajeros navegan el catálogo local y generan borradores de órdenes sin conexión.
4. Al recuperar conectividad, se corre el algoritmo del **Semáforo** (`semaforo.sql`) para simular y validar las solicitudes pendientes frente al estado real del servidor.
5. Se cierra la arquitectura global de datos integrando los tres motores de la cursada (PostgreSQL OLTP, MongoDB U7 para analítica/lecturas desnormalizadas y SQLite U8 para el edge móvil).

> **REGLA DE ORO:**  
> *"El móvil propone, el servidor dispone."*  
> La tablet solo consulta y arma borradores. Precio, stock y ventas los decide exclusivamente PostgreSQL. `SIMULADO_APROBADO` certifica viabilidad local, pero nunca constituye una venta confirmada ni modifica el servidor.

---

## 📂 Estructura del Entregable

```text
BDTP8/
├── README.md                  # Guía de reproducción, arquitectura y ensayo de defensa
├── movil/
│   ├── schema_sqlite.sql      # [Consigna 1.b] DDL estricto (STRICT) con foreign keys y centavos
│   ├── pruebas_sqlite.sql     # [Consigna 1.c] Transacciones (COMMIT/ROLLBACK), C1 y C7
│   ├── semaforo.sql           # [Consigna 2.b] Algoritmo del semáforo con CTEs y estados
│   ├── simulador.py           # [Consigna 2.b/2.c] Orquestador Python de simulación de casos C2 a C6
│   ├── servidor_snapshot.csv  # [Consigna 2.a] Instantánea real exportada desde PostgreSQL
│   └── foodstore_movil.db     # Base de datos SQLite generada y verificada
└── docs/
    ├── informe.pdf            # [Consignas 1.a, 2.c, 3.a, 3.b, 3.c] Informe formal (máximo 6 págs)
    ├── informe.md             # Documento fuente en Markdown del informe completo
    ├── generate_pdf.py        # Script ReportLab que compila el PDF formal de entrega
    ├── bitacora_ia.md         # [Consigna 4.b] Bitácora con prompts, contrastes y descartes
    ├── DUIA.md                # [Consigna 4.b] Declaración formal de Uso de IA de la cátedra
    └── kiro/                  # [Consigna 4.a] Especificaciones previas
        ├── requirements.md    # Requisitos funcionales en notación EARS vinculados a casos
        ├── design.md          # Especificación de arquitectura, estados y patrones
        └── tasks.md           # Plan de tareas de implementación y verificación
```

---

## 🚀 Guía de Reproducción Paso a Paso (Desde Cero)

### 1. Requisitos Previos
- **PostgreSQL 16+** (probado en PostgreSQL 17) corriendo en `localhost:5432`.
- Base de datos de pruebas creada: `foodstore_u8_pruebas` (clonada a partir de `foodstore` para respetar la Regla 1 de no alterar producción).
- **Python 3.12+** con los paquetes `psycopg2-binary` y `reportlab`.

### 2. Exportación de la Instantánea del Servidor (Consigna 2.a)
En PostgreSQL de pruebas, se define la vista `v_snapshot_movil` que normaliza precios a centavos y proyecta las lápidas:
```sql
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
Exportar a CSV mediante `psql`:
```powershell
\copy (SELECT * FROM v_snapshot_movil) TO 'movil/servidor_snapshot.csv' CSV HEADER
```

### 3. Creación del Esquema en SQLite (Consigna 1.b)
Crear la base de datos `movil/foodstore_movil.db` aplicando el script con tablas `STRICT` y claves foráneas activas:
```powershell
sqlite3 movil/foodstore_movil.db ".read movil/schema_sqlite.sql"
```

### 4. Ejecución de Pruebas Unitarias de SQLite (Consigna 1.c)
Ejecutar el script de pruebas que verifica la transacción con `COMMIT`, el descarte con `ROLLBACK`, la consulta offline de catálogo (Caso C1) y las restricciones de integridad estricta (Caso C7):
```powershell
sqlite3 movil/foodstore_movil.db ".read movil/pruebas_sqlite.sql"
```

### 5. Simulación Integral Automatizada del Semáforo y Casos C2 a C6 (Consigna 2.b y 2.c)
El script `movil/simulador.py` automatiza la importación de la instantánea, la inicialización de borradores, la mutación en el servidor y la resolución del semáforo:
```powershell
python movil/simulador.py
```
**Comprobaciones automáticas certificadas por el script:**
- **Caso C2:** Conflicto de precio detectado (`CONFLICTO`), re-cotización tras aceptación del cliente y aprobación final (`SIMULADO_APROBADO`).
- **Caso C3:** Rechazo por stock insuficiente en el servidor (`RECHAZADO`).
- **Caso C4:** Rechazo por baja lógica de producto (`RECHAZADO`). En `producto_cache` la fila persiste pero desaparece de la vista del catálogo comercial.
- **Caso C5:** Aprobación de borrador idéntico sin discrepancias (`SIMULADO_APROBADO`).
- **Caso C6:** Bloqueo de reenvío por violación de clave primaria en `solicitud_uuid` y comprobación de que re-simulaciones no alteran estados resueltos.
- **Inmutabilidad Central:** Verificación contra PostgreSQL mostrando que la cantidad de pedidos (80.000) y la sumatoria de stock permanecen **100% inalteradas**.

### 6. Compilación del Informe Académico en PDF
Para compilar el informe consolidado formal de hasta 6 páginas:
```powershell
python docs/generate_pdf.py
```

---

## 🎤 Guion para el Ensayo de Defensa Oral (10 Minutos)

Para la defensa presencial individual en la Semana 13, se estructuran los 10 minutos de exposición en tres bloques técnicos fundamentales:

### Bloque 1: El Mapa de la Capa de Datos y Soberanía (Minutos 0 a 3)
- **Concepto clave:** Arquitectura políglota de tres niveles.
  - **PostgreSQL 17:** Fuente Única de la Verdad (SSOT - Single Source of Truth). Rige sobre inventario físico, precios oficiales, cuentas de usuario y facturación fiscal bajo garantías ACID completas.
  - **MongoDB 9.0+ (U7):** Vista materializada de lectura desnormalizada. Almacena pedidos confirmados con embebido de líneas para consultas de alta concurrencia y analítica sin sobrecargar los índices de PostgreSQL.
  - **SQLite 3.37+ (U8):** Nodo periférico desacoplado (*edge*). Mantiene una caché de lectura del catálogo y administra borradores locales provisionales.
- **Principio rector:** *"El móvil propone, el servidor dispone."* La tablet no tiene facultades de escritura directa en el servidor; cada pedido offline es una simple propuesta sujeta a validación central.

### Bloque 2: Demostración en Vivo de un Caso de Sincronización (Minutos 3 a 7)
- **Caso a demostrar:** **Caso C2 (Conflicto tarifario) o Caso C6 (Idempotencia).**
  - Se exhibe la solicitud `REQ-C2-01` en estado `PENDIENTE` con el precio visto ($537.07).
  - Se muestra que el servidor actualizó el precio a $650.00.
  - Se ejecuta `semaforo.sql` demostrando que el semáforo cambia a `CONFLICTO` con el mensaje explicativo.
  - Se muestra la aceptación del cliente: se actualiza el borrador local y se emite la solicitud `REQ-C2-02`, la cual se resuelve como `SIMULADO_APROBADO`.
  - Se ejecuta la consulta en PostgreSQL demostrando que la tabla `pedido` sigue teniendo 80.000 filas y el stock no se tocó.

### Bloque 3: Defensa Técnica de un Hallazgo de la IA Descartado (Minutos 7 a 10)
- **Hallazgo defendido:** *Rechazo del uso de tipos `REAL` en SQLite y de triggers en lugar de restricciones `CHECK`.*
  - **Fundamento:** Explicar cómo la coma flotante binaria IEEE 754 genera imprecisiones acumulativas (p. ej. centavos perdidos) y por qué el patrón *Money* exige enteros en centavos (`precio_centavos INTEGER`).
  - **Rendimiento:** Explicar por qué las restricciones declarativas `CHECK` son evaluadas por el planificador interno de PostgreSQL sin el overhead de salto de contexto de un trigger PL/pgSQL.
