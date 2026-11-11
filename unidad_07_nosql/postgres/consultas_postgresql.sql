-- ============================================================================
-- TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN
-- BASES DE DATOS II — UNIDAD 7: NoSQL y nuevas formas de almacenamiento
-- PROYECTO: Food Store — Consultas Equivalentes y Verificación en PostgreSQL
--
-- Alumno: Maximiliano Nardez
-- Motor: PostgreSQL 17
-- Base de datos: foodstore
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PARTE 1 · INSPECCIÓN DE TABLAS Y CLAVES DEL SUBMODELO RELACIONAL (Consigna 1)
-- ----------------------------------------------------------------------------

-- Tablas que intervienen:
-- 1. pedido (id [PK], usuario_id [FK -> usuario.id], fecha, estado, forma_pago, total, ...)
-- 2. detalle_pedido (id [PK], pedido_id [FK -> pedido.id], producto_id [FK -> producto.id], cantidad, precio_unitario)
-- 3. usuario (id [PK], nombre, apellido, email, telefono, ...)
-- 4. producto (id [PK], nombre, descripcion, precio, stock, ...)

-- Verificación de cardinalidades iniciales en PostgreSQL
SELECT 'pedido' AS entidad, count(*) AS total_registros FROM pedido
UNION ALL
SELECT 'detalle_pedido', count(*) FROM detalle_pedido
UNION ALL
SELECT 'usuario', count(*) FROM usuario
UNION ALL
SELECT 'producto', count(*) FROM producto;

-- ----------------------------------------------------------------------------
-- PARTE 2 · CONSULTAS EQUIVALENTES A LAS DE MONGODB (Consigna 5)
-- ----------------------------------------------------------------------------

-- ============================================================================
-- CONSULTA 1 EQUIVALENTE (Apartado b): Filtrar pedidos por estado 'CONFIRMADO'
-- ============================================================================

-- A) Acotada al subconjunto migrado (IDs 1 al 10):
-- Esta consulta refleja exactamente el universo migrado a la colección MongoDB.
SELECT 
    p.id AS pedido_id,
    p.estado,
    p.total,
    p.forma_pago,
    u.nombre AS cliente_nombre,
    u.apellido AS cliente_apellido
FROM pedido p
JOIN usuario u ON p.usuario_id = u.id
WHERE p.estado = 'CONFIRMADO'
  AND p.id BETWEEN 1 AND 10
ORDER BY p.id;

-- Conteo en subconjunto migrado:
SELECT count(*) AS cantidad_confirmados_subconjunto
FROM pedido
WHERE estado = 'CONFIRMADO'
  AND id BETWEEN 1 AND 10;

-- B) Sobre la totalidad de la base PostgreSQL (Demostración de divergencia de alcance):
SELECT count(*) AS cantidad_confirmados_global_pg
FROM pedido
WHERE estado = 'CONFIRMADO';


-- ============================================================================
-- CONSULTA 2 EQUIVALENTE (Apartado c): Buscar pedidos que contengan el producto 8
-- Producto ID: 8 ('Producto Salsas 8 508ml')
-- ============================================================================

-- A) Acotada al subconjunto migrado (IDs 1 al 10):
-- Requiere JOIN entre 'pedido' y 'detalle_pedido' (en MongoDB es directo en el array 'items')
SELECT DISTINCT
    p.id AS pedido_id,
    p.estado,
    p.total,
    u.nombre AS cliente_nombre,
    dp.producto_id,
    pr.nombre AS producto_nombre,
    dp.cantidad,
    dp.precio_unitario,
    ROUND(dp.cantidad * dp.precio_unitario, 2) AS subtotal
FROM pedido p
JOIN usuario u ON p.usuario_id = u.id
JOIN detalle_pedido dp ON p.id = dp.pedido_id
JOIN producto pr ON dp.producto_id = pr.id
WHERE dp.producto_id = 8
  AND p.id BETWEEN 1 AND 10
ORDER BY p.id;

-- Conteo en subconjunto migrado:
SELECT count(DISTINCT p.id) AS cantidad_pedidos_con_prod8_subconjunto
FROM pedido p
JOIN detalle_pedido dp ON p.id = dp.pedido_id
WHERE dp.producto_id = 8
  AND p.id BETWEEN 1 AND 10;

-- B) Sobre la totalidad de la base PostgreSQL:
SELECT count(DISTINCT p.id) AS cantidad_pedidos_con_prod8_global_pg
FROM pedido p
JOIN detalle_pedido dp ON p.id = dp.pedido_id
WHERE dp.producto_id = 8;


-- ============================================================================
-- CONSULTA 3 EQUIVALENTE (Apartado d): Pedidos con total > $15.000
-- ============================================================================
SELECT 
    p.id AS pedido_id,
    p.total,
    p.estado,
    u.nombre AS cliente_nombre,
    u.apellido AS cliente_apellido
FROM pedido p
JOIN usuario u ON p.usuario_id = u.id
WHERE p.total > 15000
  AND p.id BETWEEN 1 AND 10
ORDER BY p.total DESC;

-- Conteo en subconjunto migrado:
SELECT count(*) AS cantidad_pedidos_total_mayor_15000
FROM pedido
WHERE total > 15000
  AND id BETWEEN 1 AND 10;


-- ============================================================================
-- VALIDACIÓN DE INTEGRIDAD FINANCIERA (Consigna 3)
-- Verificar que la suma de subtotales de líneas sea idéntica al total de cabecera
-- ============================================================================
SELECT 
    p.id AS pedido_id,
    p.total AS total_cabecera,
    ROUND(SUM(dp.cantidad * dp.precio_unitario), 2) AS suma_lineas,
    ROUND(p.total - SUM(dp.cantidad * dp.precio_unitario), 2) AS diferencia
FROM pedido p
JOIN detalle_pedido dp ON p.id = dp.pedido_id
WHERE p.id BETWEEN 1 AND 10
GROUP BY p.id, p.total
ORDER BY p.id;
