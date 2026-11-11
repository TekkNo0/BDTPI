# Documento de Diseño Técnico (Design Spec) - Módulo Móvil Food Store
**Proyecto:** Food Store en la feria: la base de la tablet y el cierre de la capa de datos  
**Herramienta de Especificación:** Kiro Specs  
**Materia:** Base de Datos II - Tecnicatura Universitaria en Programación (UTN)  

---

## 1. Arquitectura de Sincronización Desconectada (Offline-First)

El sistema implementa un modelo de datos asimétrico entre el nodo central (servidor transaccional PostgreSQL 16+) y los nodos periféricos (tablets operativas SQLite 3.37+):

```
+-------------------------------------------------------------+
|               POSTGRESQL 16+ (Servidor Central)             |
|  * Fuente Única de la Verdad (SSOT - ACID)                  |
|  * Tablas: producto, pedido, detalle_pedido, usuario        |
|  * Vista: v_snapshot_movil (Precios en centavos, lápidas)   |
+-------------------------------------------------------------+
                              |
                     Exportación periódica
                   \copy -> servidor_snapshot.csv
                              |
                              v
+-------------------------------------------------------------+
|                SQLITE 3.37+ (Tablet Food Truck)             |
|  * Tablas STRICT: snapshot_servidor, producto_cache         |
|  * Borradores locales: pedido_borrador, item_borrador       |
|  * Cola de sincronización: cola_sync                        |
|  * Motor de validación: semaforo.sql                        |
+-------------------------------------------------------------+
```

---

## 2. Decisiones de Diseño Estructural y de Esquema

### 2.1 Tablas Tipadas Estrictas (`STRICT` Mode)
SQLite tradicionalmente utiliza un sistema de tipos flexible (*type affinity*), donde cualquier columna puede almacenar cualquier tipo de dato. Para un entorno de punto de venta profesional, se aprovecha la característica `STRICT` (introducida en SQLite 3.37+), que impone verificación estricta de tipos en tiempo de inserción/actualización:
- Rechaza tipos incompatibles con error `cannot store TEXT value in INT column`.
- Garantiza que enteros, textos y restricciones `CHECK` se cumplan con la misma severidad que un motor cliente-servidor como PostgreSQL.

### 2.2 Patrón Monetario: Enteros en Centavos (`precio_centavos`)
En lugar de emplear tipos de coma flotante (`REAL` o `FLOAT`), que introducen errores de precisión acumulativa por redondeo binario IEEE 754 (p. ej. `0.1 + 0.2 != 0.3`), los precios monetarios se normalizan a enteros en centavos:
$$\text{precio\_centavos} = \text{ROUND}(\text{precio\_pg} \times 100)$$
Esto asegura comparaciones booleanas exactas (`item.precio_centavos_visto = s.precio_centavos`) y coherencia aritmética absoluta.

### 2.3 Manejo de Bajas Lógicas mediante Lápidas (Tombstones)
La tabla `producto_cache` cuenta con las columnas `disponible` (0 o 1) y `eliminado` (0 o 1).  
Cuando un producto es marcado como `activo = FALSE` en PostgreSQL:
1. En la vista `v_snapshot_movil`, `eliminado` se proyecta como `'t'` y `disponible` como `'f'`.
2. En la tablet, la fila correspondiente en `producto_cache` actualiza `eliminado = 1` y `disponible = 0`.
3. La interfaz filtra: `WHERE disponible = 1 AND eliminado = 0`. El producto desaparece inmediatamente del catálogo visual de ventas, pero la fila física permanece en SQLite para preservar la integridad referencial (`FOREIGN KEY`) de borradores históricos previos.

---

## 3. Máquina de Estados del Semáforo

Cada borrador en la tablet genera un registro en `cola_sync` con un identificador unívoco (`solicitud_uuid`) en estado `PENDIENTE`. La evaluación se realiza de forma atómica en bloques de consultas (`semaforo.sql`):

```
                        [ Solicitud PENDIENTE ]
                                   |
                      +------------+------------+
                      |                         |
            ¿Falla de Stock, Lápida       ¿Diferencia de
            o Producto Inexistente?          Precios?
                      |                         |
                     SÍ                        SÍ
                      |                         |
                      v                         v
               [ RECHAZADO ]             [ CONFLICTO ]
               (Semáforo ROJO)        (Semáforo AMARILLO)
                      |                         |
                      |                 Cliente acepta nuevo precio:
                      |                 Actualiza borrador y emite
                      |                 nueva solicitud PENDIENTE
                      |                         |
                      +------------+------------+
                                   | (NO a ambos)
                                   v
                         [ SIMULADO_APROBADO ]
                           (Semáforo VERDE)
```

- **Inmutabilidad de Estados Resueltos:** El script evalúa estrictamente `WHERE c.estado = 'PENDIENTE'`. Una vez que una solicitud transita a `RECHAZADO`, `CONFLICTO` o `SIMULADO_APROBADO`, ejecuciones subsecuentes del semáforo ignoran dicha fila.
- **Principio de Aprobación Simulada:** `SIMULADO_APROBADO` certifica que el borrador es matemáticamente viable frente al snapshot cargado, pero **no constituye una venta confirmada ni modifica PostgreSQL**.

---

## 4. Idempotencia y Mitigación de Duplicados en Red (Parada 8)

1. **A nivel Móvil (Tablet):** `solicitud_uuid` es la clave primaria (`PRIMARY KEY`) de la tabla `cola_sync`. Un reintento accidental de envío o un doble toque de pantalla dispara un error de restricción única (`UNIQUE constraint failed`), impidiendo que el cliente registre transacciones duplicadas.
2. **A nivel Servidor de Producción (PostgreSQL):** En un sistema real de ingesta HTTP/REST/gRPC, el endpoint de sincronización recibe `solicitud_uuid` y lo inserta en una tabla de bandeja de entrada transaccional (`ingesta_pedidos`) protegida con restricción `UNIQUE (solicitud_uuid)`. Si un corte de señal ocurre antes de recibir el acuse de recibo (ACK) y el móvil retransmite, PostgreSQL aplica:
   ```sql
   INSERT INTO ingesta_pedidos (solicitud_uuid, ...) 
   VALUES ($1, ...) 
   ON CONFLICT (solicitud_uuid) DO NOTHING;
   ```
   Retornando el estado previamente liquidado sin duplicar débitos financieros ni deducciones de stock.
