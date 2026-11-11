import json

with open("food-store-tp-u7/pedidos_migrados.json", "r", encoding="utf-8") as f:
    pedidos = json.load(f)

js_content = """/**
 * TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN
 * BASES DE DATOS II — UNIDAD 7: NoSQL y nuevas formas de almacenamiento
 * PROYECTO: Food Store — Migración y Consultas Documentales en MongoDB
 * 
 * Alumno: Maximiliano Nardez
 * Motor: MongoDB 9.0+ / mongosh 2.14+
 * Base de datos: foodstore
 * Colección: pedidos
 */

// Seleccionar la base de datos de trabajo
db = db.getSiblingDB("foodstore");

// ============================================================================
// PARTE 1 · CREACIÓN DE COLECCIÓN Y MIGRACIÓN (Consigna 2)
// ============================================================================

// Limpieza de colección previa si existiera
db.pedidos.drop();

// Inserción de 10 pedidos reales migrados desde PostgreSQL (IDs 1 al 10)
// Estructura documental con objetos embebidos (cliente) y arreglos (items)
// conservando tipos de datos, fechas ISODate, subtotales y precios históricos.
db.pedidos.insertMany(""" + json.dumps(pedidos, indent=2, ensure_ascii=False) + """);

print("\\n[OK] Migración finalizada. Cantidad de documentos en pedidos: " + db.pedidos.countDocuments());

// ============================================================================
// PARTE 2 · CONSULTAS Y VERIFICACIÓN (Consigna 4)
// ============================================================================

print("\\n================================================================================");
print("CONSIGNA 4.a: Mostrar todos los pedidos, incluyendo su identificador y estado");
print("================================================================================");
db.pedidos.find(
    {}, 
    { _id: 1, estado: 1 }
).forEach(p => {
    print("Pedido ID: " + p._id + " | Estado: " + p.estado);
});

print("\\n================================================================================");
print("CONSIGNA 4.b: Filtrar pedidos por un estado que exista ('CONFIRMADO')");
print("================================================================================");
db.pedidos.find(
    { estado: "CONFIRMADO" },
    { _id: 1, estado: 1, total: 1, forma_pago: 1, "cliente.nombre": 1, "cliente.apellido": 1 }
).forEach(p => {
    print("Pedido ID: " + p._id + " | Estado: " + p.estado + " | Total: $" + p.total + " | Pago: " + p.forma_pago + " | Cliente: " + p.cliente.nombre + " " + p.cliente.apellido);
});

print("\\n================================================================================");
print("CONSIGNA 4.c: Buscar pedidos que contengan un producto determinado en sus líneas");
print("Filtro: producto_id = 8 ('Producto Salsas 8 508ml')");
print("================================================================================");
db.pedidos.find(
    { "items.producto_id": 8 },
    { _id: 1, estado: 1, total: 1, "cliente.nombre": 1, items: 1 }
).forEach(p => {
    print("Pedido ID: " + p._id + " | Total: $" + p.total + " | Cliente: " + p.cliente.nombre);
    p.items.forEach(it => {
        print("   -> Item: " + it.producto_nombre + " (Prod ID: " + it.producto_id + ") | Cant: " + it.cantidad + " | P.Unit: $" + it.precio_unitario + " | Subtotal: $" + it.subtotal);
    });
});

print("\\n================================================================================");
print("CONSIGNA 4.d: Buscar pedidos cuyo total sea superior a un importe ($15.000)");
print("Justificación: Separa compras individuales/rápidas de pedidos familiares o grupales");
print("================================================================================");
db.pedidos.find(
    { total: { $gt: 15000 } },
    { _id: 1, total: 1, estado: 1, "cliente.nombre": 1, "cliente.apellido": 1 }
).sort({ total: -1 }).forEach(p => {
    print("Pedido ID: " + p._id + " | Total: $" + p.total + " | Estado: " + p.estado + " | Cliente: " + p.cliente.nombre + " " + p.cliente.apellido);
});

print("\\n================================================================================");
print("VERIFICACIÓN DE INTEGRIDAD FINANCIERA (Suma de líneas vs Total cabecera)");
print("================================================================================");
db.pedidos.aggregate([
    { $unwind: "$items" },
    { $group: {
        _id: "$_id",
        total_cabecera: { $first: "$total" },
        suma_subtotales: { $sum: "$items.subtotal" }
    }},
    { $project: {
        _id: 1,
        total_cabecera: 1,
        suma_subtotales: { $round: ["$suma_subtotales", 2] },
        diferencia: { $round: [{ $subtract: ["$total_cabecera", "$suma_subtotales"] }, 2] }
    }},
    { $sort: { _id: 1 } }
]).forEach(r => {
    print("Pedido " + r._id + " -> Cabecera: $" + r.total_cabecera + " | Líneas: $" + r.suma_subtotales + " | Dif: $" + r.diferencia);
});
"""

with open("food-store-tp-u7/consultas_mongodb.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("consultas_mongodb.js generado exitosamente.")
