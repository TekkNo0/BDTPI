"""
============================================================================
TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN - UTN
BASE DE DATOS II - TRABAJO PRÁCTICO N.º 8 (UNIDAD 8)
Script: simulador.py (Consigna 2.b y 2.c)
Descripción:
  Automatiza el ciclo de sincronización offline-first:
  1. Carga de esquema SQLite (STRICT) en foodstore_movil.db.
  2. Importación de la instantánea de PostgreSQL (servidor_snapshot.csv).
  3. Carga y refresco de producto_cache.
  4. Ejecución detallada de los Casos C2, C3, C4, C5 y C6.
  5. Ejecución del Semáforo (semaforo.sql).
  6. Comprobación de integridad inmutable en PostgreSQL (pedidos y stock).
============================================================================
"""

import os
import csv
import sqlite3
import psycopg2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "foodstore_movil.db")
SCHEMA_SQL = os.path.join(BASE_DIR, "schema_sqlite.sql")
SEMAFORO_SQL = os.path.join(BASE_DIR, "semaforo.sql")
SNAPSHOT_CSV = os.path.join(BASE_DIR, "servidor_snapshot.csv")

PG_CONFIG = {
    "dbname": "foodstore_u8_pruebas",
    "user": "postgres",
    "password": os.environ.get("PGPASSWORD", "barcala1947"),
    "host": "localhost",
    "port": 5432
}

def export_pg_snapshot():
    """Genera y exporta la vista v_snapshot_movil de PostgreSQL a CSV"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE VIEW v_snapshot_movil AS
        SELECT 
            id,
            nombre,
            ROUND(precio * 100)::INTEGER AS precio_centavos,
            stock,
            (activo AND stock > 0)::BOOLEAN AS disponible,
            (NOT activo)::BOOLEAN AS eliminado,
            TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS') AS fecha_copia
        FROM producto
        ORDER BY id;
    """)
    conn.commit()

    with open(SNAPSHOT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nombre", "precio_centavos", "stock", "disponible", "eliminado", "fecha_copia"])
        cur.execute("""
            SELECT id, nombre, precio_centavos, stock,
                   CASE WHEN disponible THEN 't' ELSE 'f' END,
                   CASE WHEN eliminado THEN 't' ELSE 'f' END,
                   fecha_copia
            FROM v_snapshot_movil
            ORDER BY id;
        """)
        for row in cur.fetchall():
            writer.writerow(row)
    cur.close()
    conn.close()
    print(f"[OK] Instantánea exportada a {SNAPSHOT_CSV}")

def init_sqlite_db():
    """Inicializa la base SQLite con el esquema estricto"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()
    print(f"[OK] Base de datos SQLite creada en {DB_PATH}")

def import_snapshot_to_sqlite(conn=None):
    """Importa el CSV en snapshot_servidor y puebla producto_cache"""
    should_close = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        should_close = True
        
    cur = conn.cursor()
    cur.execute("DELETE FROM snapshot_servidor;")
    with open(SNAPSHOT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO snapshot_servidor (id, nombre, precio_centavos, stock, disponible, eliminado, fecha_copia)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["id"]),
                row["nombre"],
                int(row["precio_centavos"]),
                int(row["stock"]),
                row["disponible"],
                row["eliminado"],
                row["fecha_copia"]
            ))
            
    # Cargar o actualizar producto_cache
    cur.execute("""
        INSERT OR REPLACE INTO producto_cache (id, nombre, precio_centavos, stock_visto, disponible, eliminado, fecha_copia)
        SELECT 
            id,
            nombre,
            precio_centavos,
            stock,
            CASE WHEN disponible IN ('t', '1') THEN 1 ELSE 0 END,
            CASE WHEN eliminado IN ('t', '1') THEN 1 ELSE 0 END,
            fecha_copia
        FROM snapshot_servidor;
    """)
    conn.commit()
    if should_close:
        conn.close()
    print("[OK] Snapshot importado y producto_cache actualizado en SQLite")

def run_semaforo(conn=None):
    """Ejecuta la lógica del semáforo SQL sobre las solicitudes PENDIENTE"""
    should_close = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        should_close = True
    
    with open(SEMAFORO_SQL, "r", encoding="utf-8") as f:
        sql = f.read()
    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()
    
    cur.execute("SELECT solicitud_uuid, id_local, estado, motivo FROM cola_sync ORDER BY solicitud_uuid;")
    filas = cur.fetchall()
    if should_close:
        conn.close()
    return filas

def run_all_cases():
    print("=" * 70)
    print("INICIO DE SIMULACIÓN Y PRUEBAS DE CASOS C2 A C6")
    print("=" * 70)
    
    # 0. Exportar instantánea inicial de PostgreSQL
    export_pg_snapshot()
    init_sqlite_db()
    import_snapshot_to_sqlite()
    
    # Capturar estado inicial en PostgreSQL para verificación de inmutabilidad
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cur = pg_conn.cursor()
    pg_cur.execute("SELECT count(*) FROM pedido;")
    pedidos_antes = pg_cur.fetchone()[0]
    pg_cur.execute("SELECT sum(stock) FROM producto;")
    stock_antes = pg_cur.fetchone()[0]
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    
    # -------------------------------------------------------------------------
    # CASO C2: Un borrador; después subís ese precio en el servidor.
    # -------------------------------------------------------------------------
    print("\n>>> CASO C2: Cambio de precio en servidor")
    # En la tablet, el cliente crea un borrador con producto 1 a su precio visto inicial (53707 centavos)
    cur.execute("INSERT INTO pedido_borrador VALUES ('BORR-C2', 'cajero_1', 'EFECTIVO', '2026-11-06 16:00:00');")
    cur.execute("INSERT INTO item_borrador VALUES ('BORR-C2', 1, 1, 53707);")
    cur.execute("INSERT INTO cola_sync VALUES ('REQ-C2-01', 'BORR-C2', 'PENDIENTE', NULL);")
    conn.commit()
    
    # En PostgreSQL: El administrador actualiza el precio del producto 1 de 537.07 a 650.00
    pg_cur.execute("UPDATE producto SET precio = 650.00 WHERE id = 1;")
    pg_conn.commit()
    print("  * Servidor: Precio de producto 1 actualizado a $650.00")
    
    # Exportar nueva instantánea y refrescar snapshot_servidor en SQLite (sin actualizar aún el borrador del cliente)
    export_pg_snapshot()
    import_snapshot_to_sqlite(conn)
    
    # Correr semáforo: REQ-C2-01 debe dar CONFLICTO
    run_semaforo(conn)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = 'REQ-C2-01';")
    c2_1 = cur.fetchone()
    print(f"  * Resultado REQ-C2-01: {c2_1[0]} | Motivo: {c2_1[1]}")
    assert c2_1[0] == "CONFLICTO", f"Esperado CONFLICTO, obtenido {c2_1[0]}"
    
    # Cliente acepta el nuevo precio: se actualiza el borrador local y se emite una nueva solicitud
    cur.execute("UPDATE item_borrador SET precio_centavos_visto = 65000 WHERE id_local = 'BORR-C2' AND producto_id = 1;")
    cur.execute("INSERT INTO cola_sync VALUES ('REQ-C2-02', 'BORR-C2', 'PENDIENTE', NULL);")
    conn.commit()
    print("  * Cliente acepta precio ($650.00): Borrador actualizado y emitida solicitud REQ-C2-02")
    
    run_semaforo(conn)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = 'REQ-C2-02';")
    c2_2 = cur.fetchone()
    print(f"  * Resultado REQ-C2-02: {c2_2[0]} | Motivo: {c2_2[1]}")
    assert c2_2[0] == "SIMULADO_APROBADO", f"Esperado SIMULADO_APROBADO, obtenido {c2_2[0]}"

    # -------------------------------------------------------------------------
    # CASO C3: Un borrador por más unidades de las que quedan.
    # -------------------------------------------------------------------------
    print("\n>>> CASO C3: Quiebre de stock en servidor")
    # Producto 2 tiene stock = 6 en servidor. El cliente pide 10 unidades
    cur.execute("INSERT INTO pedido_borrador VALUES ('BORR-C3', 'cajero_1', 'TARJETA', '2026-11-06 16:10:00');")
    cur.execute("INSERT INTO item_borrador VALUES ('BORR-C3', 2, 10, 57414);")
    cur.execute("INSERT INTO cola_sync VALUES ('REQ-C3-01', 'BORR-C3', 'PENDIENTE', NULL);")
    conn.commit()
    
    run_semaforo(conn)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = 'REQ-C3-01';")
    c3 = cur.fetchone()
    print(f"  * Resultado REQ-C3-01: {c3[0]} | Motivo: {c3[1]}")
    assert c3[0] == "RECHAZADO", f"Esperado RECHAZADO, obtenido {c3[0]}"

    # -------------------------------------------------------------------------
    # CASO C4: Un borrador con un producto que después das de baja (baja lógica).
    # -------------------------------------------------------------------------
    print("\n>>> CASO C4: Baja lógica de producto (Lápida)")
    # El borrador se crea cuando el producto 3 aún estaba activo
    cur.execute("INSERT INTO pedido_borrador VALUES ('BORR-C4', 'cajero_1', 'TRANSFERENCIA', '2026-11-06 16:15:00');")
    cur.execute("INSERT INTO item_borrador VALUES ('BORR-C4', 3, 2, 61121);")
    cur.execute("INSERT INTO cola_sync VALUES ('REQ-C4-01', 'BORR-C4', 'PENDIENTE', NULL);")
    conn.commit()
    
    # En PostgreSQL: Se aplica baja lógica (lápida) al producto 3
    pg_cur.execute("UPDATE producto SET activo = FALSE WHERE id = 3;")
    pg_conn.commit()
    print("  * Servidor: Producto 3 dado de baja (activo = FALSE)")
    
    # Exportar instantánea y actualizar SQLite
    export_pg_snapshot()
    import_snapshot_to_sqlite(conn)
    
    run_semaforo(conn)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = 'REQ-C4-01';")
    c4 = cur.fetchone()
    print(f"  * Resultado REQ-C4-01: {c4[0]} | Motivo: {c4[1]}")
    assert c4[0] == "RECHAZADO", f"Esperado RECHAZADO, obtenido {c4[0]}"
    
    # Al recargar el catálogo, el producto ya no aparece pero la fila queda
    cur.execute("SELECT count(*) FROM producto_cache WHERE id = 3;")
    fila_queda = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM producto_cache WHERE id = 3 AND disponible = 1 AND eliminado = 0;")
    visible_catalogo = cur.fetchone()[0]
    print(f"  * En producto_cache: Fila persiste={fila_queda == 1}, Visible en catálogo={visible_catalogo == 1}")
    assert fila_queda == 1 and visible_catalogo == 0, "Error en manejo de lápida en producto_cache"

    # -------------------------------------------------------------------------
    # CASO C5: Un borrador sin cambios.
    # -------------------------------------------------------------------------
    print("\n>>> CASO C5: Borrador limpio sin alteraciones")
    # Producto 4 tiene stock 12, precio 64828 centavos, activo = TRUE
    cur.execute("INSERT INTO pedido_borrador VALUES ('BORR-C5', 'cajero_1', 'EFECTIVO', '2026-11-06 16:20:00');")
    cur.execute("INSERT INTO item_borrador VALUES ('BORR-C5', 4, 1, 64828);")
    cur.execute("INSERT INTO cola_sync VALUES ('REQ-C5-01', 'BORR-C5', 'PENDIENTE', NULL);")
    conn.commit()
    
    run_semaforo(conn)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = 'REQ-C5-01';")
    c5 = cur.fetchone()
    print(f"  * Resultado REQ-C5-01: {c5[0]} | Motivo: {c5[1]}")
    assert c5[0] == "SIMULADO_APROBADO", f"Esperado SIMULADO_APROBADO, obtenido {c5[0]}"

    # -------------------------------------------------------------------------
    # CASO C6: Reenviar la misma solicitud (mismo UUID) e idempotencia.
    # -------------------------------------------------------------------------
    print("\n>>> CASO C6: Idempotencia y prevención de duplicados")
    # Intento 1: Re-insertar en cola_sync con la misma solicitud_uuid ('REQ-C5-01')
    duplicado_bloqueado = False
    try:
        cur.execute("INSERT INTO cola_sync VALUES ('REQ-C5-01', 'BORR-C5', 'PENDIENTE', NULL);")
        conn.commit()
    except sqlite3.IntegrityError as e:
        duplicado_bloqueado = True
        print(f"  * Excepción capturada con éxito (PK violation): {e}")
    assert duplicado_bloqueado, "Fallo: permitió reinsertar solicitud_uuid duplicado"
    
    # Intento 2: Repetir la simulación del semáforo: REQ-C5-01 ya está resuelto y no debe reevaluarse
    estado_previo = c5[0]
    run_semaforo(conn)
    cur.execute("SELECT estado FROM cola_sync WHERE solicitud_uuid = 'REQ-C5-01';")
    estado_posterior = cur.fetchone()[0]
    print(f"  * Estado antes: {estado_previo} | Estado posterior a re-simulación: {estado_posterior}")
    assert estado_previo == estado_posterior, "Fallo: la simulación alteró una solicitud no pendiente"

    # -------------------------------------------------------------------------
    # COMPROBACIÓN FINAL EN POSTGRESQL: EL SERVIDOR NO FUE MODIFICADO
    # -------------------------------------------------------------------------
    print("\n>>> COMPROBACIÓN FINAL EN POSTGRESQL (Servidor de pruebas)")
    pg_cur.execute("SELECT count(*) FROM pedido;")
    pedidos_despues = pg_cur.fetchone()[0]
    pg_cur.execute("SELECT sum(stock) FROM producto;")
    stock_despues = pg_cur.fetchone()[0]
    
    print(f"  * Pedidos en PG antes: {pedidos_antes} | Pedidos en PG después: {pedidos_despues}")
    print(f"  * Suma stock en PG antes: {stock_antes} | Suma stock en PG después: {stock_despues}")
    
    assert pedidos_antes == pedidos_despues, "ERROR: Se crearon pedidos en PostgreSQL!"
    assert stock_antes == stock_despues, "ERROR: Se alteró el stock en PostgreSQL!"
    print("  * REGLA DE ORO CONFIRMADA: PostgreSQL no cambió pedidos ni stock.")
    
    conn.close()
    pg_cur.close()
    pg_conn.close()
    print("\n[ÉXITO TOTAL] Todas las pruebas y casos C2 a C6 ejecutados correctamente.")

if __name__ == "__main__":
    run_all_cases()
