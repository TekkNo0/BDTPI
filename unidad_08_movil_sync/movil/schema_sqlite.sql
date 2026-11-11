-- ============================================================================
-- TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN - UTN
-- BASE DE DATOS II - TRABAJO PRÁCTICO N.º 8 (UNIDAD 8)
-- Proyecto: Food Store en la feria: la base de la tablet y el cierre de la capa de datos
-- Archivo: schema_sqlite.sql
-- Motor: SQLite 3.37+ (Probado en SQLite 3.50+)
--
-- Regla de oro: El móvil propone, el servidor dispone.
-- ============================================================================

-- Activación obligatoria de integridad referencial (claves foráneas) en SQLite
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. TABLA: snapshot_servidor
-- Propósito: Tabla intermedia de ingesta para importar el CSV exportado desde
-- la vista v_snapshot_movil de PostgreSQL. Almacena la última foto recibida.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS snapshot_servidor;
CREATE TABLE snapshot_servidor (
    id              INTEGER PRIMARY KEY,
    nombre          TEXT NOT NULL,
    precio_centavos INTEGER NOT NULL,
    stock           INTEGER NOT NULL,
    disponible      TEXT NOT NULL,  -- 't' o 'f' según exportación de PostgreSQL
    eliminado       TEXT NOT NULL,  -- 't' o 'f' según lápida de PostgreSQL
    fecha_copia     TEXT NOT NULL
) STRICT;

-- ----------------------------------------------------------------------------
-- 2. TABLA: producto_cache (Consigna 1.b)
-- Propósito: Catálogo local en la tablet utilizado por la aplicación para
-- consultar productos fuera de línea. Los booleanos se normalizan a 0 y 1.
-- Restricciones:
--  * precio_centavos >= 0 (almacenamiento en centavos enteros para evitar float)
--  * disponible IN (0, 1)
--  * eliminado IN (0, 1) (manejo de lápidas / soft delete)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS producto_cache;
CREATE TABLE producto_cache (
    id              INTEGER PRIMARY KEY,
    nombre          TEXT NOT NULL,
    precio_centavos INTEGER NOT NULL CHECK (precio_centavos >= 0),
    stock_visto     INTEGER NOT NULL DEFAULT 0,
    disponible      INTEGER NOT NULL CHECK (disponible IN (0, 1)),
    eliminado       INTEGER NOT NULL CHECK (eliminado IN (0, 1)),
    fecha_copia     TEXT NOT NULL
) STRICT;

-- ----------------------------------------------------------------------------
-- 3. TABLA: pedido_borrador (Consigna 1.b)
-- Propósito: Cabecera del borrador de pedido creado localmente en la tablet.
-- Restricciones:
--  * id_local: UUID identificador generado en el cliente móvil
--  * forma_pago: solo EFECTIVO, TARJETA o TRANSFERENCIA
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS pedido_borrador;
CREATE TABLE pedido_borrador (
    id_local        TEXT PRIMARY KEY,
    usuario         TEXT NOT NULL,
    forma_pago      TEXT NOT NULL CHECK (forma_pago IN ('EFECTIVO', 'TARJETA', 'TRANSFERENCIA')),
    fecha           TEXT NOT NULL
) STRICT;

-- ----------------------------------------------------------------------------
-- 4. TABLA: item_borrador (Consigna 1.b)
-- Propósito: Líneas de detalle del borrador de pedido.
-- Restricciones:
--  * Claves foráneas a pedido_borrador(id_local) y producto_cache(id)
--  * cantidad > 0 (no se permiten cantidades nulas o negativas)
--  * precio_centavos_visto >= 0
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS item_borrador;
CREATE TABLE item_borrador (
    id_local              TEXT NOT NULL,
    producto_id           INTEGER NOT NULL,
    cantidad              INTEGER NOT NULL CHECK (cantidad > 0),
    precio_centavos_visto INTEGER NOT NULL CHECK (precio_centavos_visto >= 0),
    PRIMARY KEY (id_local, producto_id),
    FOREIGN KEY (id_local) REFERENCES pedido_borrador (id_local) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto_cache (id)
) STRICT;

-- ----------------------------------------------------------------------------
-- 5. TABLA: cola_sync (Consigna 1.b)
-- Propósito: Cola local de solicitudes de sincronización a procesar o simular.
-- Restricciones:
--  * solicitud_uuid: clave primaria única que previene duplicados (idempotencia)
--  * estado: solo PENDIENTE, CONFLICTO, RECHAZADO o SIMULADO_APROBADO
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS cola_sync;
CREATE TABLE cola_sync (
    solicitud_uuid  TEXT PRIMARY KEY,
    id_local        TEXT NOT NULL,
    estado          TEXT NOT NULL CHECK (estado IN ('PENDIENTE', 'CONFLICTO', 'RECHAZADO', 'SIMULADO_APROBADO')),
    motivo          TEXT,
    FOREIGN KEY (id_local) REFERENCES pedido_borrador (id_local) ON DELETE CASCADE
) STRICT;
