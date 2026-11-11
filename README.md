# Proyecto Integrador «Food Store» · Base de Datos II
## Segunda Entrega del Trabajo Práctico Integrador (TPI) · Capa de Datos Completa (Unidades 4 a 8)

**Institución:** Universidad Tecnológica Nacional (UTN) · Tecnicatura Universitaria en Programación  
**Asignatura:** Base de Datos II · Ciclo Lectivo 2026  
**Integrantes del Grupo:**
* **Máximo Monardez**
* **Thiago Oviedo**
* **Matías Ruiz**

**Motores de Referencia:** PostgreSQL 16+ (PostgreSQL 17.x) · MongoDB 9.0+ · SQLite 3.37+ (3.50+)  
**Repositorio Oficial:** [`https://github.com/TekkNo0/BDTPI`](https://github.com/TekkNo0/BDTPI)  
**Rama de Entrega:** `unidades-7-8`

---

## 📋 Información y Criterio de Entrega

El presente repositorio consolida la **Segunda Entrega Parcial del Trabajo Práctico Integrador (TPI)** para el proyecto **«Food Store»**, dando cumplimiento riguroso a la totalidad de las actividades prácticas con IA definidas para las **Unidades 4 a 8**:

1. **Unidad 4 · Normalización avanzada y redundancia:** Refactorización a Forma Normal de Boyce-Codd (FNBC) en control de lotes, migración reversible sin pérdida dentro de transacciones y desnormalización controlada con triggers de consistencia inmediata (`EXPLAIN ANALYZE`).
2. **Unidad 5 · Administración y seguridad:** Matriz de roles según el principio de mínimo privilegio, auditoría nativa de accesos y DDL, simulacro de intrusión reconstruido por logs con contención y anonimización criptográfica (`usuario_anon`).
3. **Unidad 6 · Mantenimiento y recuperación:** Respaldo lógico automatizado (`pg_dump -Fc`), mantenimiento rutinario seguro sin `VACUUM FULL`, simulacro de desastre contrarreloj (RTO = 10.49 s, RPO = 0 s) e informe post-incidente.
4. **Unidad 7 · NoSQL y almacenamiento documental:** Modelado documental en MongoDB 9.0+, pipeline ETL en Python (`migrar_datos.py`), 4 consultas analíticas en `mongosh` y comparación empírica vs. PostgreSQL.
5. **Unidad 8 · Bases móviles e integración:** Base SQLite `foodstore_movil.db` en tablet punto de venta (*offline-first*), snapshot autoritativo, algoritmo de arbitraje del Semáforo (`semaforo.sql`), simulación determinista de resolución de conflictos C2 a C6 y Code Review de toda la cursada asistido por IA.

---

## 🏛️ Arquitectura Políglota de «Food Store»

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

---

## 📂 Estructura Completa del Repositorio

```text
BDTPI/
├── unidad_04_normalizacion/       # [Unidad 4] Normalización avanzada y redundancia
│   ├── sql/
│   │   ├── tp_fnbc_control_lote.sql              # FNBC (lote/deposito) + migración reversible
│   │   └── tp_desnormalizacion_top_categorias.sql# Desnormalización controlada + triggers
│   ├── evidencias/                               # Salidas crudas y planes EXPLAIN ANALYZE
│   ├── informe_TPU4_FNBC_Desnormalizacion.md     # Informe técnico específico de U4
│   └── README.md
│
├── unidad_05_seguridad/           # [Unidad 5] Administración y seguridad
│   ├── sql/
│   │   ├── roles.sql                             # DDL de roles, grants y mínimo privilegio
│   │   ├── auditoria_config.sql                  # Configuración de logging / auditoría
│   │   ├── auditoria_test.sql                    # Pruebas de verificación de auditoría
│   │   ├── simulacro_incidente.sql               # Simulación de intrusión y escalamiento
│   │   ├── usuario_anon.sql                      # Sanitización y ofuscación de datos
│   │   └── 00_funciones_bootstrap.sql            # Funciones de autenticación y bootstrap
│   ├── docs/                                     # Informes de auditoría, incidente y specs Kiro
│   ├── BITACORA.md                               # Bitácora de asistencia con IA
│   └── README.md
│
├── unidad_06_mantenimiento/       # [Unidad 6] Mantenimiento y recuperación ante desastres
│   ├── scripts/
│   │   ├── backup_foodstore.ps1 / .sh            # Respaldo lógico programado (pg_dump -Fc)
│   │   └── restore_test.ps1 / .sh                # Simulacro de restauración contrarreloj
│   ├── sql/
│   │   ├── health_check.sql                      # 4 controles de monitoreo y diagnóstico
│   │   ├── maintenance.sql                       # Mantenimiento seguro (índices, bloat, stats)
│   │   └── validaciones_minimas.sql              # Verificación de integridad referencial
│   ├── backups/                                  # Respaldo .dump de prueba (3.4 MB)
│   ├── docs/ & logs/                             # Evidencias de consola y bitácora de ejecución
│   ├── SPEC_U6.md                                # Plan formal de mantenimiento
│   ├── informe_u6.pdf / .md / .html              # Informe post-incidente (RTO / RPO)
│   ├── BITACORA.md                               # Bitácora de asistencia de IA
│   └── README.md
│
├── unidad_07_nosql/               # [Unidad 7] NoSQL y almacenamiento documental
│   ├── scripts/
│   │   ├── migrar_datos.py                       # Pipeline ETL de migración PostgreSQL -> MongoDB
│   │   ├── generate_js.py                        # Generador de scripts de carga
│   │   └── generate_pdf.py                       # Compilador de informe formal de U7
│   ├── mongo/
│   │   ├── consultas_mongodb.js                  # 4 consultas analíticas en mongosh
│   │   └── pedidos_migrados.json                 # Dataset representativo de pedidos embebidos
│   ├── postgres/
│   │   └── consultas_postgresql.sql              # Consultas analíticas equivalentes en SQL
│   ├── docs/                                     # Salidas reales de mongosh y psql
│   ├── BITACORA.md                               # Bitácora de asistencia de IA
│   ├── informe_u7.pdf / .md                      # Informe técnico comparativo documental vs. relacional
│   └── README.md
│
├── unidad_08_movil_sync/          # [Unidad 8] Bases móviles e integración
│   ├── movil/
│   │   ├── foodstore_movil.db                    # Base de datos SQLite real de la tablet POS
│   │   ├── schema_sqlite.sql                     # DDL SQLite con directiva STRICT y Money Pattern
│   │   ├── semaforo.sql                          # Algoritmo de arbitraje del Semáforo
│   │   ├── simulador.py                          # Simulador determinista de sincronización (C2 a C6)
│   │   ├── pruebas_sqlite.sql                    # Script de verificación y assertions en SQLite
│   │   └── servidor_snapshot.csv                 # Snapshot autoritativo exportado desde PostgreSQL
│   ├── docs/
│   │   ├── kiro/                                 # Kiro Specs (design.md, requirements.md, tasks.md)
│   │   ├── bitacora_ia.md                        # Bitácora de IA y Code Review de toda la cursada
│   │   ├── DUIA.md                               # Declaración de Uso de IA
│   │   └── informe.pdf / .md                     # Informe técnico de la Unidad 8
│   └── README.md
│
├── docs/                          # [Entregable Integrador Principal]
│   ├── INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.pdf # Informe consolidado formal en PDF (A4)
│   ├── INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.md  # Fuente Markdown completa del informe
│   ├── DUIA_INTEGRADORA.md                       # Declaración de Uso de IA consolidada
│   └── generate_pdf.py                           # Script ReportLab que compila el PDF integrador
│
├── .gitignore
└── README.md                                     # Este archivo
```

---

## 📄 Informe Técnico Integrador (Entregable Principal)

El informe consolidado exigido por la cátedra para la Segunda Entrega se encuentra disponible en:
* 📄 **Versión PDF diagramada (A4, lista para defensa):** [`docs/INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.pdf`](docs/INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.pdf)
* 📝 **Versión Markdown:** [`docs/INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.md`](docs/INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.md)
* 🛡️ **Declaración de Uso de IA (DUIA):** [`docs/DUIA_INTEGRADORA.md`](docs/DUIA_INTEGRADORA.md)

### Resumen de Hallazgos del Code Review con IA (U1 a U8)

| # | Unidad | Componente | Sugerencia de la IA | Decisión Humana | Fundamentación Técnica |
|---|:---:|---|---|:---:|---|
| **H1** | U1 | Catálogo DDL | Reemplazar `CHECK` por triggers PL/pgSQL. | **DESCARTADO** | `CHECK` corre en C nativo en el kernel sin sobrecosto de contexto. |
| **H2** | U5 | Permisos de caja | `GRANT ALL` sobre tablas a rol cajero. | **ACEPTADO** | Se aplicó mínimo privilegio estricto: solo `SELECT, INSERT`, revocando `UPDATE`. |
| **H3** | U8 | SQLite Móvil | Guardar precios como `REAL` con decimales. | **DESCARTADO** | Evita errores de coma flotante binaria IEEE 754. Se usó *Money Pattern* en centavos enteros (`INTEGER`). |
| **H4** | U7 | Carga MongoDB | Bucle `insertOne` por documento. | **DESCARTADO** | Cuello de botella por RTT. Se usó `insertMany` migrando el lote en < 10 ms. |

---

## 🚀 Guía de Reproducción y Verificación

### 1. Pruebas de la Unidad 4 (FNBC y Desnormalización)
```powershell
# Ejecutar migración reversible a FNBC
psql -U postgres -d foodstore_u4 -f unidad_04_normalizacion/sql/tp_fnbc_control_lote.sql

# Probar desnormalización con triggers y verificar con EXPLAIN ANALYZE
psql -U postgres -d foodstore_u4 -f unidad_04_normalizacion/sql/tp_desnormalizacion_top_categorias.sql
```

### 2. Pruebas de la Unidad 5 (Seguridad y Auditoría)
```powershell
# Aplicar esquema de roles y auditoría
psql -U postgres -d foodstore_u5 -f unidad_05_seguridad/sql/00_funciones_bootstrap.sql
psql -U postgres -d foodstore_u5 -f unidad_05_seguridad/sql/roles.sql
psql -U postgres -d foodstore_u5 -f unidad_05_seguridad/sql/auditoria_config.sql

# Ejecutar simulacro de acceso indebido
psql -U postgres -d foodstore_u5 -f unidad_05_seguridad/sql/simulacro_incidente.sql
```

### 3. Pruebas de la Unidad 6 (Mantenimiento y Respaldo)
```powershell
# Ejecutar respaldo automatizado
.\unidad_06_mantenimiento\scripts\backup_foodstore.ps1

# Ejecutar simulacro de desastre contrarreloj
.\unidad_06_mantenimiento\scripts\restore_test.ps1
```

### 4. Pruebas de la Unidad 7 (NoSQL / MongoDB)
```powershell
# Ejecutar pipeline de migración a MongoDB
python unidad_07_nosql/scripts/migrar_datos.py

# Ejecutar consultas documentales en mongosh
mongosh --file unidad_07_nosql/mongo/consultas_mongodb.js

# Ejecutar consultas equivalentes en PostgreSQL
psql -U postgres -d foodstore_u7 -f unidad_07_nosql/postgres/consultas_postgresql.sql
```

### 5. Pruebas de la Unidad 8 (SQLite y Sincronización Móvil)
```powershell
# Ejecutar el simulador de sincronización determinista (casos C2 a C6)
python unidad_08_movil_sync/movil/simulador.py

# Verificar queries del semáforo directamente en SQLite
sqlite3 unidad_08_movil_sync/movil/foodstore_movil.db < unidad_08_movil_sync/movil/pruebas_sqlite.sql
```

### 6. Regenerar el PDF del Informe Integrador
```powershell
python docs/generate_pdf.py
```
