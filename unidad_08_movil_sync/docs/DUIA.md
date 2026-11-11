# Declaración de Uso de Inteligencia Artificial (DUIA)

**Institución:** Universidad Tecnológica Nacional (UTN)  
**Carrera:** Tecnicatura Universitaria en Programación  
**Cátedra:** Base de Datos II - Ciclo Lectivo 2026  
**Trabajo Práctico:** N.º 8 - Food Store en la feria: la base de la tablet y el cierre de la capa de datos  
**Estudiante:** Maximiliano Nardez  

---

## 1. Compromiso Ético y Académico

Por medio de la presente Declaración de Uso de Inteligencia Artificial (DUIA), declaro que el presente trabajo práctico ha sido desarrollado utilizando herramientas de Inteligencia Artificial generativa como apoyo instrumental para el diseño conceptual, análisis de requisitos, generación de borradores y revisión de código, actuando siempre bajo mi estricta autoría intelectual, control crítico y verificación experimental.

Reconozco y acepto los siguientes postulados esenciales de la cátedra:
1. **Responsabilidad Intelectual:** Soy plenamente responsable de cada línea de código, consulta SQL, script de simulación y argumento técnico incluido en este entregable.
2. **Defensa Oral Individual:** Entiendo que cualquier contenido, decisión arquitectónica o código generado con asistencia de IA que no pueda explicar, justificar o defender técnicamente durante la evaluación presencial será considerado como no realizado.
3. **Verificación Empírica Obligatoria:** Ningún código o recomendación provista por la IA fue aceptado de forma pasiva; todos los artefactos fueron ejecutados y testeados en entornos reales de PostgreSQL 16+ y SQLite 3.37+.

---

## 2. Herramientas Utilizadas y Alcance de la Asistencia

- **Herramientas de IA empleadas:** Antigravity AI Assistant / Gemini / Kiro Specs.
- **Ámbitos de aplicación:**
  - Redacción de requisitos en notación EARS (`requirements.md`).
  - Asistencia en la formulación de consultas avanzadas de SQLite con agregaciones condicionales (`semaforo.sql`).
  - Code review automatizado y análisis estático de vulnerabilidades de los scripts desarrollados a lo largo del cuatrimestre.
  - Generación del script de maquetación en ReportLab para la compilación del informe académico.

---

## 3. Registro de Decisiones Relevantes (Aceptadas vs. Descartadas)

| Ámbito Técnico | Propuesta Inicial de la IA | Decisión y Corrección Humana | Justificación Académica / Motor |
|---|---|---|---|
| **Almacenamiento Monetario Móvil** | Utilizar `REAL` o `NUMERIC` en SQLite para guardar importes con coma decimal. | **Descartada.** Se implementó `INTEGER` representando centavos y modo `STRICT`. | Prevención de errores de redondeo de coma flotante binaria IEEE 754 según el patrón *Money*. |
| **Soberanía Transaccional** | Permitir que la tablet confirme ventas y descuente stock en PostgreSQL vía API remota. | **Descartada.** Se mantuvo la arquitectura asimétrica *"el móvil propone, el servidor dispone"*. | Garantía de aislamiento ACID centralizado; `SIMULADO_APROBADO` es una prueba de prefactibilidad local. |
| **Bajas de Catálogo** | Ejecutar `DELETE FROM producto_cache` ante bajas del servidor. | **Descartada.** Se implementó el patrón de Lápidas (*Tombstones*) con `disponible = 0` y `eliminado = 1`. | Mantenimiento de integridad referencial histórica para claves foráneas de borradores existentes. |
| **Idempotencia de Simulación** | Evaluar la totalidad de la cola de sincronización en cada ciclo del semáforo. | **Corregida.** Se restringió el universo de cálculo a `WHERE c.estado = 'PENDIENTE'`. | Evitar sobreescritura de estados ya liquidados (`RECHAZADO`, `CONFLICTO`, `SIMULADO_APROBADO`). |
| **Revisión de DDL en Servidor** | Sugerencia de reemplazar restricciones `CHECK` en PostgreSQL por triggers `BEFORE`. | **Descartada.** Se ratificaron las restricciones `CHECK` declarativas. | Mayor rendimiento a nivel motor interno y simplicidad operativa sin latencia de contexto PL/pgSQL. |

---

## 4. Firma y Conformidad

Manifiesto haber cumplido estrictamente con las reglas no negociables del Trabajo Práctico N.º 8:
- Trabajo realizado sobre una copia aislada de la base (`foodstore_u8_pruebas`) con datos sintéticos.
- Ausencia total de credenciales reales, correos electrónicos o datos personales sensibles en SQLite y en las interacciones con la IA.
- Respeto inquebrantable de la Regla de Oro: la tablet no alteró stock ni pedidos en PostgreSQL.

**Firma del Alumno:** Maximiliano Nardez  
**Fecha:** 6 de noviembre de 2026
