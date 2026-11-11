-- ============================================================================
-- TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN - UTN
-- BASE DE DATOS II - TRABAJO PRÁCTICO N.º 8 (UNIDAD 8)
-- Archivo: pruebas_sqlite.sql (Consigna 1.c)
-- Motor: SQLite 3.37+
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- CARGA INICIAL DE CONTROL EN producto_cache (para pruebas autónomas)
-- ----------------------------------------------------------------------------
DELETE FROM cola_sync;
DELETE FROM item_borrador;
DELETE FROM pedido_borrador;
DELETE FROM producto_cache;

INSERT INTO producto_cache (id, nombre, precio_centavos, stock_visto, disponible, eliminado, fecha_copia) VALUES
(1, 'Producto Pizzas 1 501ml', 53707, 3, 1, 0, '2026-11-06 15:30:00'),
(2, 'Producto Empanadas 2 502ml', 57414, 6, 1, 0, '2026-11-06 15:30:00'),
(3, 'Producto Sandwiches 3 503ml', 61121, 9, 1, 0, '2026-11-06 15:30:00'),
(4, 'Producto Ensaladas 4 504ml', 64828, 12, 1, 0, '2026-11-06 15:30:00'),
(5, 'Producto Postres 5 505ml', 68535, 0, 0, 0, '2026-11-06 15:30:00'); -- Sin stock/no disponible

-- ============================================================================
-- 1. TRANSACCIONES: UN BORRADOR COMPLETO CON COMMIT Y OTRO CON ROLLBACK
-- ============================================================================

-- 1.a) Transacción exitosa: Creación atómica de un borrador completo
BEGIN TRANSACTION;

INSERT INTO pedido_borrador (id_local, usuario, forma_pago, fecha)
VALUES ('borrador-uuid-001', 'operador_caja_1', 'EFECTIVO', '2026-11-06 15:35:00');

INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
VALUES 
('borrador-uuid-001', 1, 2, 53707),
('borrador-uuid-001', 2, 1, 57414);

INSERT INTO cola_sync (solicitud_uuid, id_local, estado, motivo)
VALUES ('solicitud-uuid-001', 'borrador-uuid-001', 'PENDIENTE', NULL);

COMMIT;

-- Verificación de inserción exitosa
SELECT 'Borradores confirmados:' AS info, count(*) AS total FROM pedido_borrador WHERE id_local = 'borrador-uuid-001';
SELECT 'Items asociados:' AS info, count(*) AS total FROM item_borrador WHERE id_local = 'borrador-uuid-001';
SELECT 'Solicitud en cola:' AS info, solicitud_uuid, estado FROM cola_sync WHERE solicitud_uuid = 'solicitud-uuid-001';


-- 1.b) Transacción abortada (ROLLBACK): Simulación de cancelación por parte del usuario
BEGIN TRANSACTION;

INSERT INTO pedido_borrador (id_local, usuario, forma_pago, fecha)
VALUES ('borrador-uuid-cancelado', 'operador_caja_1', 'TARJETA', '2026-11-06 15:36:00');

INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
VALUES ('borrador-uuid-cancelado', 3, 5, 61121);

-- El cliente cancela antes de confirmar el borrador
ROLLBACK;

-- Verificación de que ROLLBACK no dejó filas huérfanas
SELECT 'Verificación ROLLBACK borrador (debe ser 0):' AS info, count(*) AS total 
FROM pedido_borrador WHERE id_local = 'borrador-uuid-cancelado';
SELECT 'Verificación ROLLBACK items (debe ser 0):' AS info, count(*) AS total 
FROM item_borrador WHERE id_local = 'borrador-uuid-cancelado';


-- ============================================================================
-- 2. CASO C1: CONSULTA DEL CATÁLOGO DISPONIBLE SIN CONECTARSE AL SERVIDOR
-- ============================================================================
-- Regla de negocio local: Se listan únicamente los productos disponibles, no eliminados
-- y con stock visto positivo. La consulta se ejecuta de manera 100% offline en la tablet.

SELECT 
    id,
    nombre,
    precio_centavos,
    printf('$%.2f', precio_centavos / 100.0) AS precio_formateado,
    stock_visto,
    fecha_copia
FROM producto_cache
WHERE disponible = 1 
  AND eliminado = 0 
  AND stock_visto > 0
ORDER BY id;


-- ============================================================================
-- 3. CASO C7: INTEGRIDAD ESTRICTA (CANTIDAD EN 0 Y PRODUCTO INEXISTENTE)
-- ============================================================================

-- Conteo inicial de items de control
SELECT count(*) AS items_iniciales FROM item_borrador;

-- Intento 1: Cantidad en 0 viola la restricción CHECK (cantidad > 0)
-- En SQLite en línea de comandos o API, genera: CHECK constraint failed: cantidad > 0
-- (Comentado con '--' para permitir la corrida en lote del script; descomentar para probar el error en vivo)
-- INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
-- VALUES ('borrador-uuid-001', 1, 0, 53707);

-- Intento 2: Producto inexistente viola la restricción FOREIGN KEY (producto_id)
-- En SQLite, genera: FOREIGN KEY constraint failed
-- (Comentado con '--' para permitir la corrida en lote del script; descomentar para probar el error en vivo)
-- INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
-- VALUES ('borrador-uuid-001', 99999, 1, 50000);

-- Verificación final: Se comprueba que la tabla item_borrador mantiene la misma cantidad de filas
SELECT 'Conteo final de items tras intentos fallidos (debe mantenerse intacto):' AS control, count(*) AS total 
FROM item_borrador;
