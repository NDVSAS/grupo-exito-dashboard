import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from load_data import load_all_datasets
from data_processing import apply_filters

COLORS = {
    'yellow': '#FFD200',
    'black': '#1C1C1C',
    'grey': '#E5E5E5',
    'chart_colors': ["#845EEE", "#55B685", "#E9A23B", "#DA5597", "#52B3D0"]
}

def apply_chart_style(fig):
    """Apply corporate styling to charts."""
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        colorway=COLORS['chart_colors'],
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True),
        font={'family': 'Arial, sans-serif'}
    )
    return fig

def create_profitability_charts(filters):
    """Create profitability analysis charts."""
    datasets = load_all_datasets()
    ventas_df = apply_filters(datasets['ventas'], filters)
    
    charts = []
    
    if len(ventas_df) > 0:
        # Margin by Channel and Category
        margin_analysis = ventas_df.groupby(['canal', 'categoria']).agg({
            'ventas_cop': 'sum',
            'margen_estimado_cop': 'sum'
        }).reset_index()
        margin_analysis['margen_pct'] = (margin_analysis['margen_estimado_cop'] / 
                                         margin_analysis['ventas_cop']) * 100
        
        fig1 = px.bar(margin_analysis, x='categoria', y='margen_pct', color='canal',
                      title='Margen % por Categoría y Canal', barmode='group')
        fig1.update_yaxes(title='Margen (%)')
        fig1.update_xaxes(title='Categoría')
        apply_chart_style(fig1)
        charts.append(fig1)
        
        # Contribution Analysis (Revenue vs Margin)
        contribution = ventas_df.groupby('categoria').agg({
            'ventas_cop': 'sum',
            'margen_estimado_cop': 'sum'
        }).reset_index()
        contribution['margen_pct'] = (contribution['margen_estimado_cop'] / 
                                      contribution['ventas_cop']) * 100
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Ventas',
            x=contribution['categoria'],
            y=contribution['ventas_cop'],
            yaxis='y',
            offsetgroup=1
        ))
        fig2.add_trace(go.Scatter(
            name='Margen %',
            x=contribution['categoria'],
            y=contribution['margen_pct'],
            yaxis='y2',
            mode='lines+markers',
            line=dict(color=COLORS['chart_colors'][1], width=3)
        ))
        fig2.update_layout(
            title='Contribución: Ventas vs Margen % por Categoría',
            yaxis=dict(title='Ventas (COP)'),
            yaxis2=dict(title='Margen (%)', overlaying='y', side='right'),
            hovermode='x unified'
        )
        apply_chart_style(fig2)
        charts.append(fig2)
    
    return charts

def create_efficiency_charts(filters):
    """Create operational efficiency charts."""
    datasets = load_all_datasets()
    inventarios_df = apply_filters(datasets['inventarios'], filters)
    ventas_df = apply_filters(datasets['ventas'], filters)
    logistica_df = apply_filters(datasets['logistica'], filters)
    
    charts = []
    
    if len(inventarios_df) > 0:
        # Inventory Turnover vs Days of Inventory
        inv_efficiency = inventarios_df.groupby('categoria').agg({
            'rotacion_inventario': 'mean',
            'dias_inventario_estimado': 'mean',
            'disponibilidad_pct': 'mean'
        }).reset_index()
        
        fig1 = px.scatter(inv_efficiency, x='dias_inventario_estimado', 
                         y='rotacion_inventario', size='disponibilidad_pct',
                         color='categoria', title='Eficiencia de Inventario: Rotación vs Días',
                         labels={'dias_inventario_estimado': 'Días de Inventario',
                                'rotacion_inventario': 'Rotación'})
        apply_chart_style(fig1)
        charts.append(fig1)
    
    if len(ventas_df) > 0:
        # Sales per Transaction (Productivity)
        productivity = ventas_df.groupby(['region', 'canal']).agg({
            'ventas_cop': 'sum',
            'pedidos_transacciones': 'sum',
            'unidades_vendidas': 'sum'
        }).reset_index()
        productivity['venta_por_transaccion'] = (productivity['ventas_cop'] / 
                                                  productivity['pedidos_transacciones'])
        productivity['unidades_por_transaccion'] = (productivity['unidades_vendidas'] / 
                                                     productivity['pedidos_transacciones'])
        
        fig2 = px.bar(productivity, x='region', y='venta_por_transaccion', color='canal',
                     title='Productividad: Venta Promedio por Transacción',
                     barmode='group')
        fig2.update_yaxes(title='Venta por Transacción (COP)')
        apply_chart_style(fig2)
        charts.append(fig2)
    
    if len(logistica_df) > 0:
        # Cost Efficiency: Delivery Cost vs Volume
        cost_efficiency = logistica_df.groupby('region').agg({
            'costo_logistico_promedio_cop': 'mean',
            'pedidos': 'sum',
            'entregas_a_tiempo_pct': 'mean'
        }).reset_index()
        
        fig3 = px.scatter(cost_efficiency, x='pedidos', y='costo_logistico_promedio_cop',
                         size='entregas_a_tiempo_pct', color='region',
                         title='Eficiencia Logística: Costo vs Volumen',
                         labels={'pedidos': 'Volumen de Pedidos',
                                'costo_logistico_promedio_cop': 'Costo Promedio (COP)'})
        apply_chart_style(fig3)
        charts.append(fig3)
    
    return charts

def create_customer_behavior_charts(filters):
    """Create customer behavior analysis charts."""
    datasets = load_all_datasets()
    clientes_df = apply_filters(datasets['clientes'], filters)
    ventas_df = apply_filters(datasets['ventas'], filters)
    
    charts = []
    
    if len(clientes_df) > 0:
        # Customer Lifetime Value Distribution
        clv_dist = clientes_df.groupby('segmento_cliente').agg({
            'clv_estimado_anual_cop': 'mean',
            'frecuencia_compra_mensual': 'mean',
            'ticket_promedio_cop': 'mean',
            'clientes_activos': 'sum'
        }).reset_index()
        
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name='CLV Promedio',
            x=clv_dist['segmento_cliente'],
            y=clv_dist['clv_estimado_anual_cop'],
            yaxis='y',
            offsetgroup=1
        ))
        fig1.add_trace(go.Scatter(
            name='Frecuencia Mensual',
            x=clv_dist['segmento_cliente'],
            y=clv_dist['frecuencia_compra_mensual'],
            yaxis='y2',
            mode='lines+markers',
            line=dict(color=COLORS['chart_colors'][1], width=3)
        ))
        fig1.update_layout(
            title='Comportamiento del Cliente: CLV vs Frecuencia',
            yaxis=dict(title='CLV Anual (COP)'),
            yaxis2=dict(title='Frecuencia Mensual', overlaying='y', side='right'),
            hovermode='x unified'
        )
        apply_chart_style(fig1)
        charts.append(fig1)
        
        # Segment Value Matrix
        fig2 = px.scatter(clv_dist, x='frecuencia_compra_mensual', y='ticket_promedio_cop',
                         size='clientes_activos', color='segmento_cliente',
                         title='Matriz de Valor: Frecuencia vs Ticket Promedio',
                         labels={'frecuencia_compra_mensual': 'Frecuencia de Compra',
                                'ticket_promedio_cop': 'Ticket Promedio (COP)'})
        apply_chart_style(fig2)
        charts.append(fig2)
    
    if len(ventas_df) > 0:
        # Channel Mix Evolution
        channel_evolution = ventas_df.groupby(['mes', 'canal'])['ventas_cop'].sum().reset_index()
        channel_pivot = channel_evolution.pivot(index='mes', columns='canal', values='ventas_cop')
        channel_pct = channel_pivot.div(channel_pivot.sum(axis=1), axis=0) * 100
        
        fig3 = go.Figure()
        for canal in channel_pct.columns:
            fig3.add_trace(go.Scatter(
                name=canal,
                x=channel_pct.index,
                y=channel_pct[canal],
                mode='lines+markers',
                stackgroup='one'
            ))
        fig3.update_layout(
            title='Evolución del Mix de Canales (%)',
            yaxis_title='Participación (%)',
            xaxis_title='Mes',
            hovermode='x unified'
        )
        apply_chart_style(fig3)
        charts.append(fig3)
    
    return charts

def create_benchmarking_charts(filters):
    """Create comparative benchmarking charts."""
    datasets = load_all_datasets()
    ventas_df = apply_filters(datasets['ventas'], filters)
    inventarios_df = apply_filters(datasets['inventarios'], filters)
    logistica_df = apply_filters(datasets['logistica'], filters)
    
    charts = []
    
    if len(ventas_df) > 0:
        # Regional Performance Comparison
        regional_perf = ventas_df.groupby('region').agg({
            'ventas_cop': 'sum',
            'margen_estimado_cop': 'sum',
            'ticket_promedio_cop': 'mean'
        }).reset_index()
        regional_perf['margen_pct'] = (regional_perf['margen_estimado_cop'] / 
                                        regional_perf['ventas_cop']) * 100
        
        # Normalize for comparison
        regional_perf['ventas_index'] = (regional_perf['ventas_cop'] / 
                                         regional_perf['ventas_cop'].mean()) * 100
        regional_perf['margen_index'] = (regional_perf['margen_pct'] / 
                                         regional_perf['margen_pct'].mean()) * 100
        regional_perf['ticket_index'] = (regional_perf['ticket_promedio_cop'] / 
                                         regional_perf['ticket_promedio_cop'].mean()) * 100
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatterpolar(
            r=regional_perf['ventas_index'],
            theta=regional_perf['region'],
            fill='toself',
            name='Ventas'
        ))
        fig1.add_trace(go.Scatterpolar(
            r=regional_perf['margen_index'],
            theta=regional_perf['region'],
            fill='toself',
            name='Margen'
        ))
        fig1.add_trace(go.Scatterpolar(
            r=regional_perf['ticket_index'],
            theta=regional_perf['region'],
            fill='toself',
            name='Ticket'
        ))
        fig1.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 150])),
            title='Comparativo Regional (Índice Base 100)'
        )
        apply_chart_style(fig1)
        charts.append(fig1)
    
    if len(inventarios_df) > 0 and len(logistica_df) > 0:
        # Service Level Comparison
        inv_service = inventarios_df.groupby('region')['disponibilidad_pct'].mean().reset_index()
        log_service = logistica_df.groupby('region')['entregas_a_tiempo_pct'].mean().reset_index()
        
        service_comparison = inv_service.merge(log_service, on='region')
        
        fig2 = px.scatter(service_comparison, x='disponibilidad_pct', 
                         y='entregas_a_tiempo_pct', text='region',
                         title='Nivel de Servicio: Disponibilidad vs Entregas a Tiempo',
                         labels={'disponibilidad_pct': 'Disponibilidad Inventario (%)',
                                'entregas_a_tiempo_pct': 'Entregas a Tiempo (%)'})
        fig2.update_traces(textposition='top center')
        
        # Add quadrant lines
        fig2.add_hline(y=service_comparison['entregas_a_tiempo_pct'].mean(), 
                      line_dash="dash", line_color="gray")
        fig2.add_vline(x=service_comparison['disponibilidad_pct'].mean(), 
                      line_dash="dash", line_color="gray")
        apply_chart_style(fig2)
        charts.append(fig2)
    
    if len(ventas_df) > 0:
        # Channel Performance Gap Analysis
        channel_perf = ventas_df.groupby('canal').agg({
            'ventas_cop': 'sum',
            'ticket_promedio_cop': 'mean',
            'margen_estimado_pct': 'mean'
        }).reset_index()
        
        # Calculate gap from best performer
        channel_perf['gap_ventas'] = ((channel_perf['ventas_cop'].max() - 
                                       channel_perf['ventas_cop']) / 
                                      channel_perf['ventas_cop'].max()) * 100
        channel_perf['gap_ticket'] = ((channel_perf['ticket_promedio_cop'].max() - 
                                       channel_perf['ticket_promedio_cop']) / 
                                      channel_perf['ticket_promedio_cop'].max()) * 100
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='Gap en Ventas',
            x=channel_perf['canal'],
            y=channel_perf['gap_ventas']
        ))
        fig3.add_trace(go.Bar(
            name='Gap en Ticket',
            x=channel_perf['canal'],
            y=channel_perf['gap_ticket']
        ))
        fig3.update_layout(
            title='Brechas de Desempeño por Canal (% vs Líder)',
            yaxis_title='Gap (%)',
            barmode='group'
        )
        apply_chart_style(fig3)
        charts.append(fig3)
    
    return charts

def display():
    """Test the advanced charts with no filters."""
    filters = {}
    
    results = []
    
    # Test each chart type
    prof_charts = create_profitability_charts(filters)
    eff_charts = create_efficiency_charts(filters)
    cust_charts = create_customer_behavior_charts(filters)
    bench_charts = create_benchmarking_charts(filters)
    
    total_charts = len(prof_charts) + len(eff_charts) + len(cust_charts) + len(bench_charts)
    
    stats = [
        ("Profitability Charts", len(prof_charts)),
        ("Efficiency Charts", len(eff_charts)),
        ("Customer Behavior Charts", len(cust_charts)),
        ("Benchmarking Charts", len(bench_charts)),
        ("Total New Charts", total_charts)
    ]
    
    results.append({"_display_type": "stats", "stats": stats})
    
    # Show one sample from each category
    if prof_charts:
        results.append({"title": "Sample: Profitability Analysis", "fig": prof_charts[0]})
    if eff_charts:
        results.append({"title": "Sample: Efficiency Analysis", "fig": eff_charts[0]})
    if cust_charts:
        results.append({"title": "Sample: Customer Behavior", "fig": cust_charts[0]})
    if bench_charts:
        results.append({"title": "Sample: Benchmarking", "fig": bench_charts[0]})
    
    return results

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
