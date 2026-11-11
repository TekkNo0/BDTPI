# Proyecto Integrador «Food Store» · Base de Datos II
## Segunda Entrega del Trabajo Práctico Integrador (TPI)

**Institución:** Universidad Tecnológica Nacional (UTN) · Tecnicatura Universitaria en Programación  
**Asignatura:** Base de Datos II · Ciclo Lectivo 2026  
**Integrantes del Grupo:**
* **Máximo Monardez**
* **Thiago Oviedo**
* **Matías Ruiz**

**Motores de Referencia:** PostgreSQL 16+ (17.x) · MongoDB 9.0+ · SQLite 3.37+ (3.50+)  
**Repositorio Oficial:** [`https://github.com/TekkNo0/BDTPI`](https://github.com/TekkNo0/BDTPI)

---

> ### 📌 Nota sobre las Ramas del Repositorio (Estrategia de Entrega Cátedra)
> Siguiendo la directiva de cátedra de consolidar el trabajo en un repositorio único con rama de integración:
> * **Rama `main` (esta rama):** Contiene la consolidación de la capa relacional, seguridad y mantenimiento continuo (**Unidades 4, 5 y 6**).
> * **Rama `unidades-7-8`:** Incorpora la capa NoSQL documental en MongoDB (**Unidad 7**), la base móvil desconectada en SQLite con simulación de conflictos (**Unidad 8**) y el **Informe Técnico Integrador Final (PDF y Markdown)** que sintetiza toda la segunda entrega.
> 
> 👉 **[Ver rama `unidades-7-8` en GitHub](https://github.com/TekkNo0/BDTPI/tree/unidades-7-8)**

---

## 🏛️ Estructura del Repositorio en `main`

```text
BDTPI/
├── unidad_04_normalizacion/       # Unidad 4: Normalización avanzada y redundancia
│   ├── sql/
│   │   ├── tp_fnbc_control_lote.sql              # FNBC (lote/deposito) + migración reversible
│   │   └── tp_desnormalizacion_top_categorias.sql# Desnormalización controlada + triggers
│   ├── evidencias/                               # Salidas crudas y planes EXPLAIN ANALYZE
│   ├── informe_TPU4_FNBC_Desnormalizacion.md     # Informe técnico de la Unidad 4
│   └── README.md
│
├── unidad_05_seguridad/           # Unidad 5: Administración y seguridad
│   ├── sql/
│   │   ├── roles.sql                             # DDL de roles, grants y mínimo privilegio
│   │   ├── auditoria_config.sql                  # Configuración de logging / pgaudit
│   │   ├── auditoria_test.sql                    # Pruebas de auditoría
│   │   ├── simulacro_incidente.sql               # Simulación de intrusión y escalamiento
│   │   └── usuario_anon.sql                      # Sanitización y anonimización de datos
│   ├── docs/                                     # Informes de auditoría, incidente y specs Kiro
│   ├── BITACORA.md                               # Bitácora de asistencia con IA
│   └── README.md
│
├── unidad_06_mantenimiento/       # Unidad 6: Mantenimiento y recuperación ante desastres
│   ├── scripts/
│   │   ├── backup_foodstore.ps1 / .sh            # Respaldo lógico programado (pg_dump -Fc)
│   │   └── restore_test.ps1 / .sh                # Simulacro de restauración contrarreloj
│   ├── sql/
│   │   ├── health_check.sql                      # 4 controles de monitoreo y diagnóstico
│   │   └── maintenance.sql                       # Mantenimiento seguro (índices, bloat, stats)
│   ├── backups/                                  # Respaldo de prueba (.dump)
│   ├── docs/ & logs/                             # Salidas de terminal y logs de ejecución
│   ├── SPEC_U6.md                                # Plan de mantenimiento
│   ├── informe_u6.pdf / .md                      # Informe post-incidente (RTO / RPO)
│   ├── BITACORA.md                               # Bitácora de asistencia de IA
│   └── README.md
│
├── .gitignore
└── README.md                                     # Este archivo
```

---

## 🛠️ Resumen de Contenidos Desarrollados (Unidades 4 a 6)

### 1. Unidad 4 · Normalización Avanzada y Redundancia
* **Forma Normal de Boyce-Codd (FNBC):** Detección y corrección de anomalías en el esquema de control de lotes y almacén (`control_lote_almacen`), descomponiendo sin pérdida de información en `lote_deposito` y `almacenamiento_lote`.
* **Migración Reversible:** Procedimiento de migración ejecutado dentro de transacciones reversibles (`BEGIN; ... COMMIT; / ROLLBACK;`) con vista de compatibilidad hacia atrás.
* **Desnormalización Controlada:** Creación de la tabla agregada `venta_categoria_diaria` para optimizar consultas de reporting de alta frecuencia, respaldada por disparadores (`AFTER INSERT OR UPDATE OR DELETE`) que garantizan consistencia inmediata, demostrada mediante `EXPLAIN ANALYZE`.

### 2. Unidad 5 · Administración y Seguridad
* **Mínimo Privilegio (PoLP):** Diseño e implementación de matriz de roles segregados (`foodstore_admin`, `foodstore_operador`, `foodstore_auditor`, `rol_cajero`) con privilegios estrictos sobre tablas y secuencias.
* **Auditoría de Operaciones:** Configuración del motor para registrar operaciones DDL, DML críticas e inicios de sesión.
* **Simulacro de Acceso Indebido:** Ejecución de intento de acceso no autorizado y escalamiento de privilegios, reconstrucción forense a partir del log de auditoría y propuesta de contención.
* **Anonimización:** Creación de `usuario_anon` con hashes unidireccionales deterministas (SHA-256) y ofuscación de PII para entornos de prueba.

### 3. Unidad 6 · Mantenimiento y Recuperación
* **Respaldo Automatizado:** Script PowerShell / Bash para volcado comprimido de PostgreSQL (`pg_dump -Fc`) con rotación de retención de 7 días.
* **Mantenimiento Rutinario:** Monitoreo de bloat, fragmentación de índices, actualización periódica de estadísticas (`ANALYZE`) y limpieza sin bloqueos exclusivos (`VACUUM` concurrente sin `VACUUM FULL`).
* **Simulacro de Desastre Contrarreloj:** Restauración desatendida desde el último backup hacia una base limpia (`foodstore_restore_test`), midiendo RTO (Recovery Time Objective) de 10.49 s y RPO (Recovery Point Objective) = 0 s, documentado en el informe post-incidente.

---

Para revisar la integración políglota completa (MongoDB + SQLite) y el informe final, pasar a la rama **[`unidades-7-8`](https://github.com/TekkNo0/BDTPI/tree/unidades-7-8)**.
