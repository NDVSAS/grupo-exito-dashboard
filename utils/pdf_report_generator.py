import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from load_data import load_all_datasets
from data_processing import apply_filters
from insights_generator import generate_insights
from advanced_charts_2 import (
    create_profitability_charts,
    create_efficiency_charts,
    create_customer_behavior_charts,
    create_benchmarking_charts
)

COLORS = {
    'yellow': '#FFD200',
    'black': '#1C1C1C',
    'grey': '#E5E5E5',
}

def format_currency(value):
    """Format value as COP currency."""
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.0f}"

def fig_to_image(fig, width=6*inch, height=4*inch):
    """Convert Plotly figure to ReportLab Image."""
    img_bytes = pio.to_image(fig, format='png', width=800, height=533)
    img_buffer = BytesIO(img_bytes)
    return Image(img_buffer, width=width, height=height)

class ExecutiveSummaryReport:
    """Generate executive summary PDF reports."""
    
    def __init__(self, filters=None):
        self.filters = filters if filters else {}
        self.datasets = load_all_datasets()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(COLORS['black']),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(COLORS['black']),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='Insight',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=8
        ))
    
    def generate_report(self, output_path=None, sections=None):
        """
        Generate complete executive summary PDF.
        
        sections: list of section names to include
                 ['executive_summary', 'sales', 'customers', 'inventory', 'logistics']
        """
        if output_path is None:
            data_dir = Path(__file__).parent / "data"
            data_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = data_dir / f"executive_summary_{timestamp}.pdf"
        
        if sections is None:
            sections = ['executive_summary', 'sales', 'customers', 'inventory', 'logistics']
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title page
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Executive summary
        if 'executive_summary' in sections:
            story.extend(self._create_executive_summary())
            story.append(PageBreak())
        
        # Sales analysis
        if 'sales' in sections:
            story.extend(self._create_sales_section())
            story.append(PageBreak())
        
        # Customer analysis
        if 'customers' in sections:
            story.extend(self._create_customer_section())
            story.append(PageBreak())
        
        # Inventory analysis
        if 'inventory' in sections:
            story.extend(self._create_inventory_section())
            story.append(PageBreak())
        
        # Logistics analysis
        if 'logistics' in sections:
            story.extend(self._create_logistics_section())
            story.append(PageBreak())
        
        # Methodology and sources
        story.extend(self._create_methodology_section())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_title_page(self):
        """Create title page."""
        elements = []
        
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph("Dashboard Ejecutivo", self.styles['CustomTitle']))
        elements.append(Paragraph("Grupo Éxito", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        report_date = datetime.now().strftime("%B %Y")
        elements.append(Paragraph(
            f"Reporte Generado: {report_date}",
            self.styles['Normal']
        ))
        
        # Filter summary
        if self.filters:
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Filtros Aplicados:", self.styles['Heading3']))
            
            filter_text = []
            if self.filters.get('anio'):
                filter_text.append(f"Año: {', '.join(map(str, self.filters['anio']))}")
            if self.filters.get('region'):
                filter_text.append(f"Región: {', '.join(self.filters['region'])}")
            if self.filters.get('canal'):
                filter_text.append(f"Canal: {', '.join(self.filters['canal'])}")
            
            for line in filter_text:
                elements.append(Paragraph(line, self.styles['Normal']))
        
        return elements
    
    def _create_executive_summary(self):
        """Create executive summary section."""
        elements = []
        
        elements.append(Paragraph("Resumen Ejecutivo", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Get KPIs
        kpis_df = apply_filters(self.datasets['kpis'], self.filters)
        
        if len(kpis_df) == 0:
            elements.append(Paragraph("No hay datos disponibles con los filtros seleccionados", 
                                     self.styles['Normal']))
            return elements
        
        ventas_totales = kpis_df['ventas_totales_cop'].sum()
        ventas_omnicanal = kpis_df['ventas_omnicanal_cop'].sum()
        conversion_digital = kpis_df['conversion_digital_pct'].mean()
        nps = kpis_df['nps_estimado'].mean()
        disponibilidad = kpis_df['disponibilidad_inventario_pct'].mean()
        entregas_tiempo = kpis_df['entregas_a_tiempo_pct'].mean()
        
        # KPI Table
        kpi_data = [
            ['Métrica', 'Valor'],
            ['Ventas Totales', format_currency(ventas_totales)],
            ['Ventas Omnicanal', format_currency(ventas_omnicanal)],
            ['Conversión Digital', f"{conversion_digital*100:.2f}%"],
            ['NPS', f"{nps:.1f}"],
            ['Disponibilidad Inventario', f"{disponibilidad*100:.1f}%"],
            ['Entregas a Tiempo', f"{entregas_tiempo*100:.1f}%"]
        ]
        
        kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['yellow'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(COLORS['black'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # AI Insights
        elements.append(Paragraph("Insights Clave", self.styles['Heading3']))
        insights = generate_insights(self.filters)
        
        for insight in insights:
            elements.append(Paragraph(f"• {insight}", self.styles['Insight']))
        
        return elements
    
    def _create_sales_section(self):
        """Create sales analysis section."""
        elements = []
        
        elements.append(Paragraph("Análisis de Ventas y Rentabilidad", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        ventas_df = apply_filters(self.datasets['ventas'], self.filters)
        
        if len(ventas_df) == 0:
            elements.append(Paragraph("No hay datos disponibles", self.styles['Normal']))
            return elements
        
        # Sales by channel
        ventas_canal = ventas_df.groupby('canal').agg({
            'ventas_cop': 'sum',
            'margen_estimado_cop': 'sum'
        }).reset_index()
        ventas_canal['margen_pct'] = (ventas_canal['margen_estimado_cop'] / 
                                       ventas_canal['ventas_cop']) * 100
        ventas_canal = ventas_canal.sort_values('ventas_cop', ascending=False)
        
        # Create table
        table_data = [['Canal', 'Ventas', 'Margen', 'Margen %']]
        for _, row in ventas_canal.iterrows():
            table_data.append([
                row['canal'],
                format_currency(row['ventas_cop']),
                format_currency(row['margen_estimado_cop']),
                f"{row['margen_pct']:.1f}%"
            ])
        
        sales_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['yellow'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(COLORS['black'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(sales_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add profitability chart
        prof_charts = create_profitability_charts(self.filters)
        if prof_charts and len(prof_charts) > 0:
            elements.append(Paragraph("Análisis de Margen por Categoría", self.styles['Heading3']))
            elements.append(fig_to_image(prof_charts[0], width=6*inch, height=3.5*inch))
        
        return elements
    
    def _create_customer_section(self):
        """Create customer analysis section."""
        elements = []
        
        elements.append(Paragraph("Análisis de Clientes", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        clientes_df = apply_filters(self.datasets['clientes'], self.filters)
        
        if len(clientes_df) == 0:
            elements.append(Paragraph("No hay datos disponibles", self.styles['Normal']))
            return elements
        
        # Customer segments
        seg_data = clientes_df.groupby('segmento_cliente').agg({
            'clientes_estimados': 'sum',
            'clv_estimado_anual_cop': 'mean',
            'frecuencia_compra_mensual': 'mean',
            'nps_estimado': 'mean'
        }).reset_index()
        seg_data = seg_data.sort_values('clv_estimado_anual_cop', ascending=False)
        
        # Create table
        table_data = [['Segmento', 'Clientes', 'CLV Anual', 'Frecuencia', 'NPS']]
        for _, row in seg_data.iterrows():
            table_data.append([
                row['segmento_cliente'][:25],
                f"{row['clientes_estimados']:,.0f}",
                format_currency(row['clv_estimado_anual_cop']),
                f"{row['frecuencia_compra_mensual']:.2f}",
                f"{row['nps_estimado']:.0f}"
            ])
        
        cust_table = Table(table_data, colWidths=[2*inch, 1*inch, 1.2*inch, 1*inch, 0.8*inch])
        cust_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['yellow'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(COLORS['black'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(cust_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add behavior chart
        behavior_charts = create_customer_behavior_charts(self.filters)
        if behavior_charts and len(behavior_charts) > 0:
            elements.append(Paragraph("Comportamiento del Cliente", self.styles['Heading3']))
            elements.append(fig_to_image(behavior_charts[0], width=6*inch, height=3.5*inch))
        
        return elements
    
    def _create_inventory_section(self):
        """Create inventory analysis section."""
        elements = []
        
        elements.append(Paragraph("Análisis de Inventarios", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        inv_df = apply_filters(self.datasets['inventarios'], self.filters)
        
        if len(inv_df) == 0:
            elements.append(Paragraph("No hay datos disponibles", self.styles['Normal']))
            return elements
        
        # Inventory by region
        inv_region = inv_df.groupby('region').agg({
            'disponibilidad_pct': 'mean',
            'quiebre_inventario': 'sum',
            'rotacion_inventario': 'mean',
            'dias_inventario_estimado': 'mean'
        }).reset_index()
        inv_region = inv_region.sort_values('disponibilidad_pct', ascending=False)
        
        # Create table
        table_data = [['Región', 'Disponibilidad', 'Quiebres', 'Rotación', 'Días Inv.']]
        for _, row in inv_region.iterrows():
            table_data.append([
                row['region'][:20],
                f"{row['disponibilidad_pct']*100:.1f}%",
                f"{row['quiebre_inventario']:.0f}",
                f"{row['rotacion_inventario']:,.0f}",
                f"{row['dias_inventario_estimado']:.0f}"
            ])
        
        inv_table = Table(table_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['yellow'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(COLORS['black'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(inv_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add efficiency chart
        eff_charts = create_efficiency_charts(self.filters)
        if eff_charts and len(eff_charts) > 0:
            elements.append(Paragraph("Eficiencia de Inventario", self.styles['Heading3']))
            elements.append(fig_to_image(eff_charts[0], width=6*inch, height=3.5*inch))
        
        return elements
    
    def _create_logistics_section(self):
        """Create logistics analysis section."""
        elements = []
        
        elements.append(Paragraph("Análisis Logístico", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        log_df = apply_filters(self.datasets['logistica'], self.filters)
        
        if len(log_df) == 0:
            elements.append(Paragraph("No hay datos disponibles", self.styles['Normal']))
            return elements
        
        # Logistics by region
        log_region = log_df.groupby('region').agg({
            'entregas_a_tiempo_pct': 'mean',
            'tiempo_promedio_entrega_horas': 'mean',
            'costo_logistico_promedio_cop': 'mean',
            'pedidos': 'sum'
        }).reset_index()
        log_region = log_region.sort_values('entregas_a_tiempo_pct', ascending=False)
        
        # Create table
        table_data = [['Región', 'Entregas a Tiempo', 'Tiempo Prom.', 'Costo Prom.', 'Pedidos']]
        for _, row in log_region.iterrows():
            table_data.append([
                row['region'][:20],
                f"{row['entregas_a_tiempo_pct']*100:.1f}%",
                f"{row['tiempo_promedio_entrega_horas']:.0f}h",
                format_currency(row['costo_logistico_promedio_cop']),
                f"{row['pedidos']:,.0f}"
            ])
        
        log_table = Table(table_data, colWidths=[2*inch, 1.3*inch, 1*inch, 1.2*inch, 1*inch])
        log_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['yellow'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(COLORS['black'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(log_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add benchmarking chart
        bench_charts = create_benchmarking_charts(self.filters)
        if bench_charts and len(bench_charts) > 0:
            elements.append(Paragraph("Comparativo Regional", self.styles['Heading3']))
            elements.append(fig_to_image(bench_charts[0], width=6*inch, height=3.5*inch))
        
        return elements
    
    def _create_methodology_section(self):
        """Create methodology and data sources section."""
        elements = []
        
        elements.append(Paragraph("Metodología y Fuentes de Datos", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph("Fuentes de Datos:", self.styles['Heading3']))
        elements.append(Paragraph(
            "• Ventas mensuales por canal, categoría y región (2024)",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            "• Inventarios por región, formato y categoría",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            "• Conversión digital y embudo de ventas online",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            "• Segmentos de clientes, CLV y NPS",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            "• Métricas logísticas y entregas por región y canal",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph("Limitaciones:", self.styles['Heading3']))
        elements.append(Paragraph(
            "• Los datos corresponden únicamente al año 2024",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            "• Dataset sintético académico basado en informes públicos de Grupo Éxito",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            "• Métricas de CLV y NPS son estimaciones basadas en patrones de compra",
            self.styles['Normal']
        ))
        
        return elements

def display():
    """Test PDF report generation."""
    # Generate report with no filters
    report = ExecutiveSummaryReport(filters={})
    output_path = report.generate_report()
    
    return [
        {"_display_type": "stats", "stats": [
            ("Report Generated", "Success"),
            ("Output Path", str(output_path)),
            ("File Size", f"{output_path.stat().st_size / 1024:.1f} KB")
        ]},
        {"_display_type": "markdown", "value": f"""
## Executive Summary PDF Report Generated

The report has been saved to:
```
{output_path}
```

**Sections Included:**
- Executive Summary with KPIs and AI insights
- Sales and Profitability Analysis
- Customer Segmentation and Behavior
- Inventory and Supply Chain Metrics
- Logistics Performance Analysis
- Methodology and Data Sources

**Features:**
- Corporate branding (Grupo Éxito colors)
- Summary tables for each section
- Key visualizations embedded as images
- Filter summary on title page
- Professional formatting with page breaks
"""}
    ]

# --- Execute display() ---
"""Serializes and outputs the result of display() for the Plotly Studio runtime."""

import json
import traceback

from utils.display_util import _dumps, _serialize_result  # type: ignore[import-not-found]

if __name__ == "__main__":
    try:
        if "display" in dir():
            _result = display()  # type: ignore[name-defined]  # noqa: F821 - defined in user code
        else:
            # Fallback for data modules that define classes/functions but no display().
            # Just report success so the step doesn't error out.
            _result = {
                "_display_type": "stats",
                "stats": [("Status", "Module loaded successfully")],
            }
        _serialized = _serialize_result(_result)
        _json_str = _dumps(_serialized)
    except Exception as _display_err:
        _json_str = json.dumps({"type": "error", "value": traceback.format_exc()})
    print("__RESULT_START__")
    print(_json_str)
    print("__RESULT_END__")
