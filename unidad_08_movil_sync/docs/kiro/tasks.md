# Plan de Tareas de Implementación (Tasks Spec) - Módulo Móvil Food Store
**Proyecto:** Food Store en la feria: la base de la tablet y el cierre de la capa de datos  
**Herramienta de Especificación:** Kiro Specs  
**Materia:** Base de Datos II - Tecnicatura Universitaria en Programación (UTN)  

---

## Tareas de Desarrollo y Verificación

- [x] **TASK-01: Definición del Esquema Móvil SQLite (Consigna 1.b)**
  - Crear `movil/schema_sqlite.sql` iniciando con `PRAGMA foreign_keys = ON;`.
  - Implementar tablas estrictas (`STRICT`): `snapshot_servidor`, `producto_cache`, `pedido_borrador`, `item_borrador`, `cola_sync`.
  - Configurar restricciones declarativas: `CHECK` de precios >= 0, enteros en centavos, estados permitidos y claves foráneas en cascada.
  - *Estado:* Completado y verificado.

- [x] **TASK-02: Scripts de Pruebas Unitarias de SQLite (Consigna 1.c)**
  - Crear `movil/pruebas_sqlite.sql`.
  - Diseñar caso de transacción atómica con `BEGIN ... COMMIT` y transacción revertida con `ROLLBACK`.
  - Validar Caso C1: consulta de catálogo disponible offline (`WHERE disponible = 1 AND eliminado = 0 AND stock_visto > 0`).
  - Validar Caso C7: intentos de inserción con cantidad = 0 y producto inexistente, comprobando fallo de integridad y ausencia de filas espurias.
  - *Estado:* Completado y verificado.

- [x] **TASK-03: Extracción de Instantánea desde PostgreSQL (Consigna 2.a)**
  - Crear la vista `v_snapshot_movil` en la base de pruebas de PostgreSQL (`foodstore_u8_pruebas`).
  - Normalizar campos: conversión de `precio` a `precio_centavos` (enteros), proyección de booleanos `disponible` y `eliminado` ('t' / 'f'), y timestamp `fecha_copia`.
  - Exportar el resultado a `movil/servidor_snapshot.csv`.
  - Desarrollar la rutina de importación a `snapshot_servidor` y carga hacia `producto_cache`.
  - *Estado:* Completado y verificado.

- [x] **TASK-04: Implementación del Motor de Semáforo (Consigna 2.b)**
  - Escribir `movil/semaforo.sql` utilizando CTEs y funciones de agregación condicional (`SUM(CASE ...)` y `GROUP_CONCAT`).
  - Codificar la regla de prioridad: ROJO (`RECHAZADO`) prevalece sobre AMARILLO (`CONFLICTO`), y ausencia de ambos genera VERDE (`SIMULADO_APROBADO`).
  - Restringir la actualización exclusivamente a registros con `estado = 'PENDIENTE'` para garantizar idempotencia.
  - *Estado:* Completado y verificado.

- [x] **TASK-05: Simulación y Verificación de Casos C2 a C6 (Consigna 2.c)**
  - Desarrollar `movil/simulador.py` para orquestar los escenarios de prueba.
  - Ejecutar Caso C2: Conflicto tarifario por suba de precio en servidor, re-cotización y aprobación simulada.
  - Ejecutar Caso C3: Rechazo por stock insuficiente en el servidor.
  - Ejecutar Caso C4: Rechazo por baja lógica (lápida) y validación de persistencia no visible en catálogo.
  - Ejecutar Caso C5: Aprobación simulada de borrador limpio sin discrepancias.
  - Ejecutar Caso C6: Bloqueo de duplicado por clave primaria y verificación de no-reevaluación.
  - Ejecutar consulta de control en PostgreSQL certificando que stock y pedidos permanecen 100% inalterados.
  - *Estado:* Completado y verificado.

- [x] **TASK-06: Síntesis de Arquitectura y Mantenimiento (Consignas 3.a y 3.b)**
  - Elaborar el mapa de responsabilidades y soberanía de los tres motores (PostgreSQL, MongoDB U7, SQLite U8).
  - Redactar adenda al plan de mantenimiento de U6: políticas de respaldo, mitigación de restauración desfasada (split-brain) y gobierno de revisión de incidentes de sincronización.
  - *Estado:* Completado y documentado.

- [x] **TASK-07: Auditoría y Code Review con IA (Consigna 3.c)**
  - Ejecutar revisión sobre los scripts históricos de la cursada (U1 a U7).
  - Seleccionar y profundizar 3 hallazgos de al menos 2 unidades distintas con verificación en base de datos.
  - Fundamentar técnicamente el descarte de al menos un hallazgo de la IA.
  - *Estado:* Completado y documentado.

- [x] **TASK-08: Consolidación Documental y Generación de PDF (Consignas 4.b, 4.c y Entregables)**
  - Redactar `docs/bitacora_ia.md` y `docs/DUIA.md`.
  - Redactar `README.md` con instructivo de reproducción y guion de defensa de 10 minutos.
  - Desarrollar script ReportLab `docs/generate_pdf.py` y compilar `docs/informe.pdf` (máximo 6 páginas) conteniendo 1.a, 2.c, 3.a, 3.b y 3.c.
  - *Estado:* Completado y verificado.
