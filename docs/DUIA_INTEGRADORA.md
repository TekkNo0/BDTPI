# Declaración de Uso de Inteligencia Artificial (DUIA)
## Trabajo Práctico Integrador · Segunda Entrega (Unidades 4 a 8)

**Institución:** Universidad Tecnológica Nacional (UTN) · Tecnicatura Universitaria en Programación  
**Asignatura:** Base de Datos II · Ciclo Lectivo 2026  
**Estudiante:** Maximiliano Nardez  
**Proyecto:** Food Store  
**Fecha:** Noviembre 2026  

---

### 1. Alcance y Compromiso Ético
El presente documento certifica que el desarrollo de la Segunda Entrega del Trabajo Práctico Integrador (Unidades 4 a 8) cumplió de manera estricta el **Protocolo Obligatorio de Uso de IA sobre Datos** dispuesto por la cátedra:

1. **Comprensión y Verificación Humana:** Ningún script, consulta SQL, pipeline o archivo de configuración generado o asistido por IA fue aplicado a ciegas. Cada componente fue analizado línea por línea, comprendido en su totalidad y evaluado en entornos de prueba antes de su adopción definitiva.
2. **Protección de Datos Sensibles:** En ninguna interacción con modelos de IA se transmitieron contraseñas, secretos, información personal identificable (PII) o credenciales reales. Toda interacción utilizó esquemas DDL abstractos o datasets anonimizados.
3. **Soberanía del Criterio Profesional:** La IA fue empleada como copiloto técnico y asistente de diseño; las decisiones finales de arquitectura, adopción de patrones, rechazo de sugerencias y mitigación de vulnerabilidades fueron ejercidas por el estudiante.

---

### 2. Registro de Herramientas de IA y Casos de Uso

| Herramienta | Ámbito de Aplicación | Finalidad Específica |
|---|---|---|
| **Kiro Specs** | Unidades 5 y 8 | Redacción formal de especificaciones de diseño, requerimientos y tareas de sincronización (`requirements.md`, `design.md`, `tasks.md`). |
| **OpenCode** | Unidades 4, 5 y 6 | Asistencia en la terminal para el diseño de DDL relacional, scripts de backup en PowerShell/Bash y pruebas de auditoría de seguridad. |
| **Antigravity** | Unidades 7, 8 e Integración | Generación de pipelines de migración PG → Mongo, simulación del algoritmo de sincronización en Python y consolidación del informe integrador. |

---

### 3. Registro de Prompts y Decisiones Clave

#### Caso 1: Refactorización a Forma Normal de Boyce-Codd (FNBC) en Unidad 4
* **Prompt Base:** *"Analiza las dependencias funcionales de la tabla `control_lote_almacen` sabiendo que `lote, deposito -> ubicacion_deposito, cantidad` y que `deposito -> ubicacion_deposito`. Propón la descomposición en FNBC y una estrategia de migración sin pérdida de información."*
* **Resultado:** La IA propuso descomponer en `lote_deposito` y `almacenamiento_lote`.
* **Decisión Humana:** **Aceptada.** Se agregó de forma autónoma una vista de compatibilidad con el nombre de la tabla legada para garantizar compatibilidad hacia atrás en aplicaciones existentes.

#### Caso 2: Manejo de importes monetarios en SQLite (Unidad 8)
* **Prompt Base:** *"¿Cómo conviene modelar los precios de productos en una base SQLite en una tablet móvil para acelerar los cálculos de subtotales?"*
* **Sugerencia de la IA:** Sugirió emplear el tipo de dato `REAL` por simplicidad sintáctica.
* **Decisión Humana:** **Rechazada rotundamente.** Se adoptó el *Money Pattern*, tipando en `INTEGER` (centavos enteros) bajo la directiva `STRICT` para erradicar errores de coma flotante binaria (IEEE 754).

#### Caso 3: Inserción de documentos en MongoDB (Unidad 7)
* **Prompt Base:** *"Genera un pipeline en Python para cargar los pedidos migrados desde PostgreSQL a la colección `pedidos` en MongoDB."*
* **Sugerencia de la IA:** Inicialmente generó un bucle `for` iterando con `collection.insert_one(pedido)` alegando "mayor control por documento".
* **Decisión Humana:** **Rechazada y optimizada.** Se reemplazó por un único llamado `collection.insert_many(pedidos)` en bloque atómico, minimizando el Round-Trip Time (RTT) a menos de 10 ms.
