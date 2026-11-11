# Especificación de Requisitos de Software (SRS) - Módulo Móvil Food Store
**Proyecto:** Food Store en la feria: la base de la tablet y el cierre de la capa de datos  
**Herramienta de Especificación:** Kiro Specs  
**Notación:** EARS (Easy Approach to Requirements Syntax)  
**Materia:** Base de Datos II - Tecnicatura Universitaria en Programación (UTN)  

---

## 1. Contexto Operativo
El Food Truck opera en ferias y eventos gastronómicos al aire libre sin conexión celular garantizada (modo *offline-first*). La tablet del cajero permite navegar el catálogo de productos y confeccionar borradores de pedidos en una base de datos local SQLite 3.37+.  
Al recuperar conectividad o realizar cierres de turno, la tablet sincroniza sus borradores contra la réplica del servidor central PostgreSQL 16+ mediante el algoritmo del Semáforo.  

**Regla de oro de diseño:** *El móvil propone, el servidor dispone.* La tablet nunca decide precios, no descuenta stock ni confirma ventas transaccionales definitivas.

---

## 2. Requisitos del Sistema en Notación EARS

### REQ-01 · Detección y Gestión de Conflictos de Precio
- **Patrón EARS:** Event-Driven (`WHEN <event> THE SYSTEM SHALL <action>`)
- **Enunciado:**  
  `WHEN el precio actual de un producto en el snapshot del servidor difiere del precio visto por la tablet al armar el borrador (precio_centavos_visto <> s.precio_centavos), THE SYSTEM SHALL marcar la solicitud en cola_sync con estado CONFLICTO y registrar el detalle de la discrepancia tarifaria.`
- **Caso de Prueba Asociado:** **Caso C2** (Detección de precio desactualizado, re-cotización y posterior aprobación).

### REQ-02 · Validación Restrictiva de Quiebre de Stock
- **Patrón EARS:** Event-Driven (`WHEN <event> THE SYSTEM SHALL <action>`)
- **Enunciado:**  
  `WHEN la cantidad solicitada de cualquiera de los productos del borrador excede el inventario físico disponible en el snapshot del servidor (cantidad > s.stock), THE SYSTEM SHALL marcar la solicitud en cola_sync con estado RECHAZADO y registrar el déficit de unidades.`
- **Caso de Prueba Asociado:** **Caso C3** (Intento de compra por encima del stock del servidor).

### REQ-03 · Manejo de Bajas Lógicas mediante Lápidas (Tombstones)
- **Patrón EARS:** Event-Driven (`WHEN <event> THE SYSTEM SHALL <action>`)
- **Enunciado:**  
  `WHEN un producto incluido en un borrador fue dado de baja lógica en el servidor (activo = FALSE / eliminado = 't') o marcado como no disponible, THE SYSTEM SHALL marcar la solicitud en cola_sync con estado RECHAZADO, y al sincronizar el catálogo local (producto_cache), excluirlo de las consultas de venta manteniendo la fila para integridad referencial histórica.`
- **Caso de Prueba Asociado:** **Caso C4** (Baja lógica en servidor con persistencia de lápida en cliente).

### REQ-04 · Garantía de Idempotencia en la Ingesta de Solicitudes
- **Patrón EARS:** Event-Driven (`WHEN <event> THE SYSTEM SHALL <action>`)
- **Enunciado:**  
  `WHEN se recibe una solicitud de sincronización con un identificador único (solicitud_uuid) que ya existe en la base de datos, THE SYSTEM SHALL abortar la inserción por violación de clave primaria e impedir que re-ejecuciones del semáforo alteren el estado de solicitudes ya evaluadas.`
- **Caso de Prueba Asociado:** **Caso C6** (Reenvío idéntico con retención de estado resuelto y prevención de reevaluación).

---

## 3. Matriz de Trazabilidad de Requisitos

| Requisito | Caso de Prueba | Condición Servidor | Estado Semáforo Esperado | Acción Cliente |
|---|:---:|---|:---:|---|
| **REQ-01** | **C2** | `precio_servidor != precio_visto` | `CONFLICTO` | Actualizar borrador con nuevo precio y reintentar |
| **REQ-02** | **C3** | `cantidad > stock_servidor` | `RECHAZADO` | Informar al cliente y reducir cantidad o quitar ítem |
| **REQ-03** | **C4** | `activo = FALSE` (Lápida) | `RECHAZADO` | Quitar producto dado de baja; no se exhibe más |
| **REQ-04** | **C6** | `solicitud_uuid` duplicado | `ERROR PK / NO REEVALÚA` | Descartar reenvío de red; mantener resultado previo |
