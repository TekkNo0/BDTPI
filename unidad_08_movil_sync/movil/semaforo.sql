-- ============================================================================
-- TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN - UTN
-- BASE DE DATOS II - TRABAJO PRÁCTICO N.º 8 (UNIDAD 8)
-- Archivo: semaforo.sql (Consigna 2.b)
-- Motor: SQLite 3.37+
--
-- Regla de oro: El móvil propone, el servidor dispone.
-- Este script evalúa las solicitudes en estado 'PENDIENTE' en cola_sync contra
-- la última foto del servidor en snapshot_servidor, aplicando la lógica
-- del semáforo:
--  * ROJO (RECHAZADO): Algún producto no existe, no está disponible,
--    fue dado de baja (lápida) o no alcanza el stock del servidor.
--  * AMARILLO (CONFLICTO): No hay rojo, pero cambió algún precio en el servidor.
--  * VERDE (SIMULADO_APROBADO): Todos los productos y precios coinciden.
--
-- Idempotencia: Solo procesa filas con estado = 'PENDIENTE'. Si se re-ejecuta,
-- las solicitudes ya evaluadas no se modifican ni duplican.
-- ============================================================================

WITH evaluacion_items AS (
    SELECT 
        c.solicitud_uuid,
        i.producto_id,
        i.cantidad,
        i.precio_centavos_visto,
        s.id AS servidor_id,
        s.stock AS servidor_stock,
        s.precio_centavos AS servidor_precio_centavos,
        s.disponible AS servidor_disponible,
        s.eliminado AS servidor_eliminado,
        -- Condición ROJO: Inexistente, dado de baja ('t'), no disponible ('f') o stock insuficiente
        CASE 
            WHEN s.id IS NULL THEN 1
            WHEN s.eliminado IN ('t', '1') THEN 1
            WHEN s.disponible IN ('f', '0') THEN 1
            WHEN i.cantidad > s.stock THEN 1
            ELSE 0 
        END AS es_rojo,
        -- Condición AMARILLO: No hay rojo, pero difiere el precio visto del precio actual en servidor
        CASE 
            WHEN s.id IS NOT NULL 
             AND s.eliminado NOT IN ('t', '1') 
             AND s.disponible NOT IN ('f', '0') 
             AND i.cantidad <= s.stock 
             AND i.precio_centavos_visto <> s.precio_centavos THEN 1
            ELSE 0 
        END AS es_amarillo,
        -- Detalle descriptivo de causa por ítem
        CASE 
            WHEN s.id IS NULL THEN 'Producto ' || i.producto_id || ' inexistente en servidor'
            WHEN s.eliminado IN ('t', '1') THEN 'Producto ' || i.producto_id || ' dado de baja (lápida)'
            WHEN s.disponible IN ('f', '0') THEN 'Producto ' || i.producto_id || ' no disponible'
            WHEN i.cantidad > s.stock THEN 'Stock insuficiente para prod ' || i.producto_id || ' (solicitado: ' || i.cantidad || ', disponible: ' || COALESCE(s.stock, 0) || ')'
            WHEN i.precio_centavos_visto <> s.precio_centavos THEN 'Precio modificado en prod ' || i.producto_id || ' (visto: $' || printf('%.2f', i.precio_centavos_visto / 100.0) || ', servidor: $' || printf('%.2f', s.precio_centavos / 100.0) || ')'
            ELSE NULL 
        END AS motivo_item
    FROM cola_sync c
    JOIN item_borrador i ON c.id_local = i.id_local
    LEFT JOIN snapshot_servidor s ON i.producto_id = s.id
    WHERE c.estado = 'PENDIENTE'
),
evaluacion_solicitud AS (
    SELECT 
        solicitud_uuid,
        CASE 
            WHEN SUM(es_rojo) > 0 THEN 'RECHAZADO'
            WHEN SUM(es_amarillo) > 0 THEN 'CONFLICTO'
            ELSE 'SIMULADO_APROBADO'
        END AS nuevo_estado,
        CASE 
            WHEN SUM(es_rojo) > 0 THEN GROUP_CONCAT(motivo_item, ' | ')
            WHEN SUM(es_amarillo) > 0 THEN GROUP_CONCAT(motivo_item, ' | ')
            ELSE 'Validación exitosa: stock y precios coinciden con servidor'
        END AS nuevo_motivo
    FROM evaluacion_items
    GROUP BY solicitud_uuid
)
UPDATE cola_sync
SET 
    estado = (SELECT nuevo_estado FROM evaluacion_solicitud WHERE evaluacion_solicitud.solicitud_uuid = cola_sync.solicitud_uuid),
    motivo = (SELECT nuevo_motivo FROM evaluacion_solicitud WHERE evaluacion_solicitud.solicitud_uuid = cola_sync.solicitud_uuid)
WHERE solicitud_uuid IN (SELECT solicitud_uuid FROM evaluacion_solicitud);

-- Visualización de la cola de sincronización tras la ejecución
SELECT 
    solicitud_uuid,
    id_local,
    estado,
    COALESCE(motivo, 'Sin observaciones') AS motivo
FROM cola_sync
ORDER BY solicitud_uuid;
