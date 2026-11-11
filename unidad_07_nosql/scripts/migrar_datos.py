import psycopg2
import psycopg2.extras
from pymongo import MongoClient
import json
from datetime import datetime

# Conexión a PostgreSQL
pg_conn = psycopg2.connect(
    dbname="foodstore",
    user="postgres",
    password="barcala1947",
    host="localhost",
    port=5432
)

# Conexión a MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["foodstore"]
pedidos_col = mongo_db["pedidos"]

# Limpiar colección previa si existiera
pedidos_col.drop()

# Extraer pedidos 1 a 10 de PostgreSQL
with pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("""
        SELECT 
            p.id AS pedido_id,
            p.fecha,
            p.estado,
            p.forma_pago,
            p.total,
            p.metadata,
            u.id AS usuario_id,
            u.nombre AS cliente_nombre,
            u.apellido AS cliente_apellido,
            u.email AS cliente_email,
            u.telefono AS cliente_telefono
        FROM pedido p
        JOIN usuario u ON p.usuario_id = u.id
        WHERE p.id BETWEEN 1 AND 10
        ORDER BY p.id;
    """)
    pedidos_pg = cur.fetchall()

    docs_to_insert = []
    for p in pedidos_pg:
        # Obtener items de este pedido
        cur.execute("""
            SELECT 
                dp.id AS detalle_id,
                dp.producto_id,
                pr.nombre AS producto_nombre,
                dp.cantidad,
                dp.precio_unitario,
                ROUND(dp.cantidad * dp.precio_unitario, 2) AS subtotal
            FROM detalle_pedido dp
            JOIN producto pr ON dp.producto_id = pr.id
            WHERE dp.pedido_id = %s
            ORDER BY dp.id;
        """, (p["pedido_id"],))
        items_pg = cur.fetchall()

        items = []
        for it in items_pg:
            items.append({
                "detalle_id": it["detalle_id"],
                "producto_id": it["producto_id"],
                "producto_nombre": it["producto_nombre"],
                "cantidad": it["cantidad"],
                "precio_unitario": float(it["precio_unitario"]),
                "subtotal": float(it["subtotal"])
            })

        doc = {
            "_id": p["pedido_id"],
            "pedido_id": p["pedido_id"],
            "fecha": p["fecha"].isoformat(),
            "estado": p["estado"],
            "forma_pago": p["forma_pago"],
            "total": float(p["total"]),
            "cliente": {
                "usuario_id": p["usuario_id"],
                "nombre": p["cliente_nombre"],
                "apellido": p["cliente_apellido"],
                "email": p["cliente_email"],
                "telefono": p["cliente_telefono"]
            },
            "items": items,
            "cantidad_items": len(items)
        }
        docs_to_insert.append(doc)

# Insertar en MongoDB
result = pedidos_col.insert_many(docs_to_insert)
print(f"Insertados exitosamente {len(result.inserted_ids)} pedidos en MongoDB:")
print(f"IDs: {result.inserted_ids}")

# Guardar un archivo JSON exportado con los datos
with open("pedidos_migrados.json", "w", encoding="utf-8") as f:
    json.dump(docs_to_insert, f, indent=2, ensure_ascii=False)

print("Datos guardados en pedidos_migrados.json")
