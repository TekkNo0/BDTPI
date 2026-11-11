# Trabajo Práctico — Unidad 7: NoSQL y Nuevas Formas de Almacenamiento
**Proyecto Integrador:** Food Store | **Motores:** PostgreSQL 17 & MongoDB 9.0+ / mongosh 2.14+  
**Materia:** Base de Datos II — Unidad 7 | **Alumno:** Maximo Monardez  
**Repositorio:** `https://github.com/TekkNo0/TPU7`

---

## 📁 Estructura del Entregable

```text
food-store-tp-u7/
├── informe_u7.pdf             # [ENTREGABLE PRINCIPAL] Informe formal consolidado (hasta 5 páginas)
├── informe_u7.md              # Documento fuente en Markdown del informe completo
├── consultas_mongodb.js       # [ENTREGABLE OBLIGATORIO] Script con insertMany y las 4 consultas en MongoDB
├── consultas_postgresql.sql   # [ENTREGABLE OBLIGATORIO] Script con consultas equivalentes y verificación en PostgreSQL
├── migrar_datos.py            # Pipeline de extracción/migración automatizada de PG a Mongo (Python)
├── pedidos_migrados.json      # Dataset de 10 pedidos con líneas migrados en formato JSON
├── generate_pdf.py            # Script en ReportLab que compila el PDF de entrega formal
├── BITACORA.md                # Bitácora de asistencia de IA (tabla obligatoria de 3 columnas y contrastes)
├── README.md                  # Guía técnica de reproducción del entorno y evidencias
└── docs/                      # Evidencias de salidas de consola capturadas
    ├── consultas_mongo_output.txt  # Salida real de mongosh
    └── consultas_pg_output.txt     # Salida real de psql
```

---

## 🚀 Guía de Reproducción Rápida

### 1. Requisitos Previos
- **PostgreSQL 17** corriendo localmente en el puerto `5432` con la base `foodstore` cargada.
- **MongoDB 9.0+** corriendo localmente en el puerto `27017`.
- **mongosh** instalado y disponible en el entorno.
- **Python 3.12+** con dependencias instaladas (`pymongo`, `psycopg2-binary`, `reportlab`).

### 2. Ejecutar la Migración y Consultas en MongoDB
Para crear la base `foodstore`, la colección `pedidos`, migrar los 10 documentos con `insertMany` y correr las consultas de la Consigna 4:
```powershell
mongosh --file .\food-store-tp-u7\consultas_mongodb.js
```

### 3. Ejecutar las Consultas Equivalentes en PostgreSQL
Para ejecutar las consultas relacionales equivalentes en PostgreSQL 17 y verificar la integridad de totales:
```powershell
$env:PGPASSWORD = "tu_password"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d foodstore -f .\food-store-tp-u7\consultas_postgresql.sql
```

### 4. Compilar el Informe PDF Académico
Para recompilar el PDF formal de hasta 5 páginas:
```powershell
python .\food-store-tp-u7\generate_pdf.py
```

---

## 📊 Tabla Comparativa de Verificación de Resultados

| Consulta | Cantidad en PostgreSQL (Subconjunto) | Cantidad en MongoDB | Coinciden los IDs | Identificadores Recuperados |
|---|:---:|:---:|:---:|:---|
| **Estado seleccionado (`CONFIRMADO`)** | **5** | **5** | **Sí** | IDs: `[1, 2, 3, 4, 5]` |
| **Producto seleccionado (`producto_id = 8`)** | **1** | **1** | **Sí** | ID: `[1]` |
| **Total superior a umbral (> $15.000)** | **5** | **5** | **Sí** | IDs: `[3, 4, 7, 8, 9]` |

- **Integridad Financiera:** $\Delta (\text{Total Cabecera} - \sum \text{Subtotales Líneas}) = \$0.00$ verificado en los 10 pedidos en ambos motores.
- **Conclusión Técnica:** Arquitectura híbrida políglota con PostgreSQL en la ingesta transaccional ACID de checkout y MongoDB como vista materializada desnormalizada de alta disponibilidad para lecturas intensivas de pedidos confirmados.
