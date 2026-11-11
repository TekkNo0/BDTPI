"""
Compilador del Informe Técnico Integrador (Segunda Entrega TPI) a PDF
Genera: docs/INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.pdf
Utiliza ReportLab para generar un PDF formal, prolijo y estructurado.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, num_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 800, "Base de Datos II · TPI «Food Store» · Segunda Entrega (Unidades 4 a 8)")
            self.drawRightString(A4[0] - 54, 800, "Maximiliano Nardez · UTN")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 794, A4[0] - 54, 794)

        # Footer
        footer_text = f"Página {self._pageNumber} de {num_pages}"
        self.drawRightString(A4[0] - 54, 36, footer_text)
        self.drawString(54, 36, "Universidad Tecnológica Nacional (UTN) · Ciclo Lectivo 2026")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 48, A4[0] - 54, 48)

        self.restoreState()

def build_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_pdf = os.path.join(script_dir, "INFORME_INTEGRADOR_TPI_SEGUNDA_ENTREGA.pdf")

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2B6CB0'),
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4A5568')
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#2C5282'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1A202C')
    )

    story = []

    # Title & Header
    story.append(Paragraph("Informe Técnico Integrador · Segunda Entrega", title_style))
    story.append(Paragraph("Proyecto «Food Store» · Persistencia Políglota y Gestión de Datos (U4 a U8)", subtitle_style))
    
    meta_text = (
        "<b>Institución:</b> Universidad Tecnológica Nacional (UTN) · Tecnicatura Universitaria en Programación<br/>"
        "<b>Asignatura:</b> Base de Datos II · Ciclo Lectivo 2026 | <b>Alumno:</b> Maximiliano Nardez<br/>"
        "<b>Motores:</b> PostgreSQL 17 (OLTP) · MongoDB 9.0+ (NoSQL Read Model) · SQLite 3.37+ (Edge POS)<br/>"
        "<b>Repositorio:</b> https://github.com/TekkNo0/BDTPI | <b>Rama de Entrega:</b> unidades-7-8"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=10))

    # Section 1: Resumen
    story.append(Paragraph("1. Arquitectura Políglota de «Food Store»", h1_style))
    story.append(Paragraph(
        "El proyecto integrador Food Store articula una solución de datos distribuida y políglota para un modelo de negocio mixto (restaurante / food truck en ferias gastronómicas):",
        body_style
    ))

    arch_data = [
        [Paragraph("<b>Motor</b>", body_style), Paragraph("<b>Rol Arquitectónico</b>", body_style), Paragraph("<b>Responsabilidad y Datos Custodiados</b>", body_style), Paragraph("<b>Soberanía</b>", body_style)],
        [Paragraph("<b>PostgreSQL 17</b>", body_style), Paragraph("Núcleo Transaccional (OLTP / ACID)", body_style), Paragraph("Catálogo maestro, inventario real, facturación firme, auditoría de seguridad y roles.", body_style), Paragraph("<b>SSOT (Única Fuente de Verdad)</b>", body_style)],
        [Paragraph("<b>MongoDB 9.0+</b>", body_style), Paragraph("Modelo Documental (Read Model)", body_style), Paragraph("Colección desnormalizada de pedidos y líneas embebidas para analítica rápida sin JOINs.", body_style), Paragraph("Solo Lectura / Sincronizado", body_style)],
        [Paragraph("<b>SQLite 3.37+</b>", body_style), Paragraph("Caché Periférica (Offline-First)", body_style), Paragraph("Instantánea local del catálogo en tablet POS y borradores de pedidos generados en feria.", body_style), Paragraph("El móvil propone, el servidor dispone", body_style)]
    ]
    t_arch = Table(arch_data, colWidths=[80, 110, 190, 107])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    # Section 2: Implementación por unidad
    story.append(Paragraph("2. Elementos Implementados por Unidad (4 a 8)", h1_style))
    story.append(Paragraph(
        "• <b>Unidad 4 (Normalización y Redundancia):</b> Detección de anomalías en control de lotes y refactorización a <b>Forma Normal de Boyce-Codd (FNBC)</b>. Migración de datos sin pérdida en transacciones reversibles. Desnormalización controlada con tabla resumen <code>venta_categoria_diaria</code> mantenida mediante triggers automáticos y validada con <code>EXPLAIN ANALYZE</code>.<br/>"
        "• <b>Unidad 5 (Seguridad y Auditoría):</b> Implementación del principio de mínimo privilegio con 4 roles (<code>foodstore_admin</code>, <code>foodstore_operador</code>, <code>foodstore_auditor</code>, <code>rol_cajero</code>). Auditoría nativa de accesos y DDL. Simulacro de acceso indebido/escalamiento de privilegios reconstruido por logs forenses. Anonimización con hashes criptográficos SHA-256 en <code>usuario_anon</code>.<br/>"
        "• <b>Unidad 6 (Mantenimiento y Recuperación):</b> Respaldo lógico automatizado en formato binario custom (<code>pg_dump -Fc</code>) vía scripts en PowerShell y Bash. Rutinas de mantenimiento seguro (<code>maintenance.sql</code> y <code>health_check.sql</code> sin <code>VACUUM FULL</code>). Simulacro de desastre con restauración contra reloj (RTO = 10.49 s, RPO = 0 s) e informe post-incidente.<br/>"
        "• <b>Unidad 7 (NoSQL Documental):</b> Pipeline ETL en Python (<code>migrar_datos.py</code>) para migrar pedidos de PostgreSQL a MongoDB embebiendo cliente y detalle. Batería de 4 consultas analíticas en <code>mongosh</code> y consultas equivalentes en SQL con análisis comparativo.<br/>"
        "• <b>Unidad 8 (Bases Móviles e Integración):</b> Base SQLite <code>foodstore_movil.db</code> en tablet POS con directiva <code>STRICT</code> y patrón Money (centavos enteros). Algoritmo del Semáforo (<code>semaforo.sql</code>) y simulador en Python (<code>simulador.py</code>) para resolución determinista de conflictos C2 a C6. Code Review de toda la cursada asistido por IA.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Section 3: Metodología y Pruebas
    story.append(Paragraph("3. Metodología de Pruebas y Resultados Cuantitativos", h1_style))
    story.append(Paragraph(
        "<b>Desempeño de Desnormalización (U4):</b> En un dataset poblado con 200.000 pedidos y 600.000 líneas, la consulta normalizada con agregación y múltiples JOINs demandó <b>185.34 ms</b>. La consulta sobre <code>venta_categoria_diaria</code> resolvió en <b>0.82 ms</b> (aceleración superior a <b>220x</b>) con actualización atómica continua garantizada por triggers.<br/>"
        "<b>Simulacro de Intrusión (U5):</b> Se comprobó el bloqueo inmediato del rol cajero al intentar alterar precios (<code>ERROR: permission denied for table producto</code>). El registro de auditoría capturó IP, usuario, hora e instrucción exacta del atacante permitiendo diseñar la contención preventiva.<br/>"
        "<b>Simulacro de Desastre (U6):</b> Ante la pérdida simulada del servidor, el script desatendido <code>restore_test.ps1</code> aprovisionó la base limpia, restauró datos, índices y restricciones en <b>10.49 segundos (RTO)</b> con <b>0 segundos de pérdida (RPO)</b>, validado por <code>validaciones_minimas.sql</code>.<br/>"
        "<b>Benchmark PostgreSQL vs. MongoDB (U7):</b> La lectura de pedidos con detalle completo en MongoDB (<code>findOne</code>) tomó <b>1.2 ms</b> sin sobrecosto de JOINs, frente a <b>4.8 ms</b> en PostgreSQL. PostgreSQL demostró mayor eficiencia en agregaciones complejas sobre tablas altamente indexadas.<br/>"
        "<b>Casos de Conflicto de Sincronización Móvil (U8):</b> El simulador evaluó los 5 escenarios deterministas: C2 (Aprobado por stock/precio idéntico), C3 (Rechazado por stock insuficiente), C4 (Conflicto por incremento de precio en servidor → semáforo amarillo para re-cotización), C5 (Rechazado por ítem inactivo/lápida) y C6 (Rechazado integral por falla en una línea de pedido mixto).",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Section 4: Decisiones de Diseño
    story.append(Paragraph("4. Decisiones Fundamentadas de Diseño y Arquitectura", h1_style))
    story.append(Paragraph(
        "• <b>FNBC vs. Desnormalización:</b> Se normalizó a FNBC en entidades donde las dependencias transitivas generaban anomalías de modificación (lotes y depósitos). Se desnormalizó selectivamente en reportes de alta frecuencia donde el cálculo dinámico penalizaba el CPU, blindando la consistencia mediante triggers transaccionales.<br/>"
        "• <b>Mínimo Privilegio:</b> El personal de punto de venta (cajeros) carece de permisos de DDL o de modificación sobre transacciones cerradas, garantizando inmutabilidad contable.<br/>"
        "• <b>Formato de Respaldo:</b> Se eligió <code>pg_dump -Fc</code> frente a volcados en texto plano (SQL) por comprimir el almacenamiento en más del 65% y permitir restauración paralela (<code>-j</code>) y selectiva.<br/>"
        "• <b>Regla de Oro en Movilidad:</b> <i>'El móvil propone, el servidor dispone'</i>. La tablet no confirma pedidos ni altera inventario; genera borradores que PostgreSQL valida y arbitra de forma definitiva.<br/>"
        "• <b>Patrón Money en SQLite:</b> Se descartó el tipo <code>REAL</code> debido a los errores de redondeo inherentes a la coma flotante IEEE 754; se adoptó <code>INTEGER</code> en centavos enteros con tabla <code>STRICT</code>.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Section 5: Code Review y DUIA
    story.append(Paragraph("5. Declaración DUIA y Code Review Asistido por IA", h1_style))
    story.append(Paragraph(
        "Se aplicó el Protocolo de IA sobre datos: anonimización absoluta de información y revisión humana crítica de cada propuesta. A continuación se resumen los hallazgos del Code Review sobre los scripts de la cursada:",
        body_style
    ))

    cr_data = [
        [Paragraph("<b>#</b>", body_style), Paragraph("<b>Unidad / Script</b>", body_style), Paragraph("<b>Propuesta de la IA</b>", body_style), Paragraph("<b>Decisión</b>", body_style), Paragraph("<b>Fundamentación Técnica</b>", body_style)],
        [Paragraph("<b>H1</b>", body_style), Paragraph("U1 / <code>schema.sql</code>", body_style), Paragraph("Reemplazar <code>CHECK (precio >= 0)</code> por triggers PL/pgSQL.", body_style), Paragraph("<b>DESCARTADO</b>", body_style), Paragraph("Las restricciones <code>CHECK</code> declarativas corren en el kernel de C sin latencia ni sobrecosto.", body_style)],
        [Paragraph("<b>H2</b>", body_style), Paragraph("U5 / <code>roles.sql</code>", body_style), Paragraph("Permisos excesivos (<code>GRANT ALL</code>) en rol cajero.", body_style), Paragraph("<b>ACEPTADO</b>", body_style), Paragraph("Se corrigió a mínimo privilegio: solo <code>SELECT, INSERT</code> revocando <code>UPDATE</code>.", body_style)],
        [Paragraph("<b>H3</b>", body_style), Paragraph("U8 / <code>schema_sqlite.sql</code>", body_style), Paragraph("Almacenar importes en SQLite como <code>REAL</code> con decimales.", body_style), Paragraph("<b>DESCARTADO</b>", body_style), Paragraph("Evita errores de redondeo binario. Se aplicó patrón Money en centavos enteros (<code>INTEGER</code>).", body_style)],
        [Paragraph("<b>H4</b>", body_style), Paragraph("U7 / <code>migrar_datos.py</code>", body_style), Paragraph("Cargar pedidos en MongoDB con bucle <code>insertOne</code>.", body_style), Paragraph("<b>DESCARTADO</b>", body_style), Paragraph("Ineficiente por latencia RTT. Se usó <code>insertMany</code> ejecutando el lote en < 10 ms.", body_style)]
    ]
    t_cr = Table(cr_data, colWidths=[22, 95, 120, 80, 170])
    t_cr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_cr)
    story.append(Spacer(1, 10))

    # Section 6: Checklist
    story.append(Paragraph("6. Checklist de Cumplimiento Oficial de Entrega", h1_style))
    story.append(Paragraph(
        "[X] <b>Unidad 4:</b> Normalización a FNBC validada, migración reversible y desnormalización con triggers.<br/>"
        "[X] <b>Unidad 5:</b> Mínimo privilegio, auditoría activada, simulacro de intrusión y tabla anonimizada.<br/>"
        "[X] <b>Unidad 6:</b> Respaldo programado, rutinas de salud y simulacro de desastre con informe post-incidente.<br/>"
        "[X] <b>Unidad 7:</b> Base documental MongoDB sobre datos reales y comparativa técnica vs. relacional.<br/>"
        "[X] <b>Unidad 8:</b> SQLite móvil offline-first, algoritmo de semáforo con conflictos probados y Code Review.<br/>"
        "[X] <b>Criterio Cátedra:</b> Repositorio único con branch <code>unidades-7-8</code> e Informe Técnico Integrador.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {output_pdf}")

if __name__ == "__main__":
    build_pdf()
