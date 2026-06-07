import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

class DrillDownManager:
    """Manages drill-down state and generates drill-down visualizations."""
    
    def __init__(self):
        self.datasets = load_all_datasets()
    
    def get_sales_drilldown(self, filters, drill_path=None):
        """
        Sales drill-down: Total → Region → Category → Time Period
        drill_path: list of tuples [(level, value), ...]
        e.g. [('region', 'Bogota y Cundinamarca'), ('categoria', 'Mercado y alimentos')]
        """
        ventas_df = apply_filters(self.datasets['ventas'], filters)
        
        if drill_path is None:
            drill_path = []
        
        # Apply drill-down filters
        for level, value in drill_path:
            if level in ventas_df.columns:
                ventas_df = ventas_df[ventas_df[level] == value]
        
        # Determine next drill level
        drill_levels = ['region', 'categoria', 'mes']
        current_level_idx = len(drill_path)
        
        if current_level_idx >= len(drill_levels):
            # Final level - show detailed table
            return self._create_detail_view(ventas_df, drill_path, 'sales')
        
        next_level = drill_levels[current_level_idx]
        
        # Aggregate by next level
        agg_data = ventas_df.groupby(next_level).agg({
            'ventas_cop': 'sum',
            'margen_estimado_cop': 'sum',
            'unidades_vendidas': 'sum',
            'pedidos_transacciones': 'sum'
        }).reset_index()
        
        agg_data['margen_pct'] = (agg_data['margen_estimado_cop'] / agg_data['ventas_cop']) * 100
        agg_data = agg_data.sort_values('ventas_cop', ascending=False)
        
        # Create chart
        fig = px.bar(agg_data, x=next_level, y='ventas_cop',
                     title=f'Ventas por {next_level.replace("_", " ").title()}',
                     hover_data=['margen_pct', 'unidades_vendidas'])
        fig.update_yaxes(title='Ventas (COP)')
        apply_chart_style(fig)
        
        # Calculate comparison metrics
        total_sales = agg_data['ventas_cop'].sum()
        avg_sales = agg_data['ventas_cop'].mean()
        top_performer = agg_data.iloc[0][next_level]
        top_sales = agg_data.iloc[0]['ventas_cop']
        
        comparison = {
            'total': total_sales,
            'average': avg_sales,
            'top_performer': top_performer,
            'top_value': top_sales,
            'count': len(agg_data)
        }
        
        # Create trend if at category level
        trend_fig = None
        if current_level_idx >= 1:  # At category level or deeper
            trend_data = ventas_df.groupby('mes')['ventas_cop'].sum().reset_index()
            trend_fig = px.line(trend_data, x='mes', y='ventas_cop',
                               title='Tendencia Mensual',
                               markers=True)
            apply_chart_style(trend_fig)
        
        return {
            'chart': fig,
            'data_table': agg_data,
            'comparison': comparison,
            'trend': trend_fig,
            'next_level': next_level,
            'drill_path': drill_path
        }
    
    def get_margin_drilldown(self, filters, drill_path=None):
        """
        Margin drill-down: Overall → Channel → Category → Time Period
        """
        ventas_df = apply_filters(self.datasets['ventas'], filters)
        
        if drill_path is None:
            drill_path = []
        
        # Apply drill-down filters
        for level, value in drill_path:
            if level in ventas_df.columns:
                ventas_df = ventas_df[ventas_df[level] == value]
        
        drill_levels = ['canal', 'categoria', 'mes']
        current_level_idx = len(drill_path)
        
        if current_level_idx >= len(drill_levels):
            return self._create_detail_view(ventas_df, drill_path, 'margin')
        
        next_level = drill_levels[current_level_idx]
        
        # Aggregate
        agg_data = ventas_df.groupby(next_level).agg({
            'ventas_cop': 'sum',
            'margen_estimado_cop': 'sum'
        }).reset_index()
        
        agg_data['margen_pct'] = (agg_data['margen_estimado_cop'] / agg_data['ventas_cop']) * 100
        agg_data = agg_data.sort_values('margen_pct', ascending=False)
        
        # Create dual-axis chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Ventas',
            x=agg_data[next_level],
            y=agg_data['ventas_cop'],
            yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            name='Margen %',
            x=agg_data[next_level],
            y=agg_data['margen_pct'],
            yaxis='y2',
            mode='lines+markers',
            line=dict(width=3)
        ))
        fig.update_layout(
            title=f'Margen por {next_level.replace("_", " ").title()}',
            yaxis=dict(title='Ventas (COP)'),
            yaxis2=dict(title='Margen (%)', overlaying='y', side='right'),
            hovermode='x unified'
        )
        apply_chart_style(fig)
        
        comparison = {
            'avg_margin': agg_data['margen_pct'].mean(),
            'top_margin': agg_data.iloc[0]['margen_pct'],
            'top_performer': agg_data.iloc[0][next_level],
            'total_margin_cop': agg_data['margen_estimado_cop'].sum()
        }
        
        trend_fig = None
        if current_level_idx >= 1:
            trend_data = ventas_df.groupby('mes').agg({
                'ventas_cop': 'sum',
                'margen_estimado_cop': 'sum'
            }).reset_index()
            trend_data['margen_pct'] = (trend_data['margen_estimado_cop'] / trend_data['ventas_cop']) * 100
            
            trend_fig = px.line(trend_data, x='mes', y='margen_pct',
                               title='Tendencia de Margen %',
                               markers=True)
            apply_chart_style(trend_fig)
        
        return {
            'chart': fig,
            'data_table': agg_data,
            'comparison': comparison,
            'trend': trend_fig,
            'next_level': next_level,
            'drill_path': drill_path
        }
    
    def get_inventory_drilldown(self, filters, drill_path=None):
        """
        Inventory drill-down: Region → Category → Format
        """
        inv_df = apply_filters(self.datasets['inventarios'], filters)
        
        if drill_path is None:
            drill_path = []
        
        for level, value in drill_path:
            if level in inv_df.columns:
                inv_df = inv_df[inv_df[level] == value]
        
        drill_levels = ['region', 'categoria', 'formato_tienda']
        current_level_idx = len(drill_path)
        
        if current_level_idx >= len(drill_levels):
            return self._create_detail_view(inv_df, drill_path, 'inventory')
        
        next_level = drill_levels[current_level_idx]
        
        agg_data = inv_df.groupby(next_level).agg({
            'disponibilidad_pct': 'mean',
            'quiebre_inventario': 'sum',
            'rotacion_inventario': 'mean',
            'dias_inventario_estimado': 'mean'
        }).reset_index()
        
        agg_data = agg_data.sort_values('disponibilidad_pct', ascending=False)
        
        # Create chart
        fig = px.bar(agg_data, x=next_level, y='disponibilidad_pct',
                     title=f'Disponibilidad de Inventario por {next_level.replace("_", " ").title()}',
                     hover_data=['quiebre_inventario', 'rotacion_inventario'])
        fig.update_yaxes(title='Disponibilidad (%)')
        apply_chart_style(fig)
        
        comparison = {
            'avg_availability': agg_data['disponibilidad_pct'].mean() * 100,
            'total_stockouts': agg_data['quiebre_inventario'].sum(),
            'avg_turnover': agg_data['rotacion_inventario'].mean(),
            'best_performer': agg_data.iloc[0][next_level]
        }
        
        trend_fig = None
        if current_level_idx >= 1:
            trend_data = inv_df.groupby('mes')['disponibilidad_pct'].mean().reset_index()
            trend_fig = px.line(trend_data, x='mes', y='disponibilidad_pct',
                               title='Tendencia de Disponibilidad',
                               markers=True)
            apply_chart_style(trend_fig)
        
        return {
            'chart': fig,
            'data_table': agg_data,
            'comparison': comparison,
            'trend': trend_fig,
            'next_level': next_level,
            'drill_path': drill_path
        }
    
    def get_customer_drilldown(self, filters, drill_path=None):
        """
        Customer drill-down: Segment → Detailed metrics
        """
        clientes_df = apply_filters(self.datasets['clientes'], filters)
        
        if drill_path is None:
            drill_path = []
        
        for level, value in drill_path:
            if level in clientes_df.columns:
                clientes_df = clientes_df[clientes_df[level] == value]
        
        if len(drill_path) == 0:
            # First level - show segments
            agg_data = clientes_df.groupby('segmento_cliente').agg({
                'clientes_estimados': 'sum',
                'clv_estimado_anual_cop': 'mean',
                'frecuencia_compra_mensual': 'mean',
                'ticket_promedio_cop': 'mean',
                'retencion_pct': 'mean',
                'nps_estimado': 'mean'
            }).reset_index()
            
            agg_data = agg_data.sort_values('clv_estimado_anual_cop', ascending=False)
            
            fig = px.bar(agg_data, x='segmento_cliente', y='clv_estimado_anual_cop',
                        title='CLV por Segmento de Cliente',
                        hover_data=['clientes_estimados', 'frecuencia_compra_mensual'])
            fig.update_yaxes(title='CLV Anual (COP)')
            apply_chart_style(fig)
            
            comparison = {
                'total_customers': agg_data['clientes_estimados'].sum(),
                'avg_clv': agg_data['clv_estimado_anual_cop'].mean(),
                'top_segment': agg_data.iloc[0]['segmento_cliente'],
                'top_clv': agg_data.iloc[0]['clv_estimado_anual_cop']
            }
            
            # Trend by month
            trend_data = clientes_df.groupby('mes')['clv_estimado_anual_cop'].mean().reset_index()
            trend_fig = px.line(trend_data, x='mes', y='clv_estimado_anual_cop',
                               title='Tendencia de CLV Promedio',
                               markers=True)
            apply_chart_style(trend_fig)
            
            return {
                'chart': fig,
                'data_table': agg_data,
                'comparison': comparison,
                'trend': trend_fig,
                'next_level': 'segmento_cliente',
                'drill_path': drill_path
            }
        else:
            # Detail view for selected segment
            return self._create_detail_view(clientes_df, drill_path, 'customer')
    
    def get_logistics_drilldown(self, filters, drill_path=None):
        """
        Logistics drill-down: Region → Channel
        """
        log_df = apply_filters(self.datasets['logistica'], filters)
        
        if drill_path is None:
            drill_path = []
        
        for level, value in drill_path:
            if level in log_df.columns:
                log_df = log_df[log_df[level] == value]
        
        drill_levels = ['region', 'canal']
        current_level_idx = len(drill_path)
        
        if current_level_idx >= len(drill_levels):
            return self._create_detail_view(log_df, drill_path, 'logistics')
        
        next_level = drill_levels[current_level_idx]
        
        agg_data = log_df.groupby(next_level).agg({
            'entregas_a_tiempo_pct': 'mean',
            'tiempo_promedio_entrega_horas': 'mean',
            'costo_logistico_promedio_cop': 'mean',
            'pedidos': 'sum'
        }).reset_index()
        
        agg_data = agg_data.sort_values('entregas_a_tiempo_pct', ascending=False)
        
        fig = px.bar(agg_data, x=next_level, y='entregas_a_tiempo_pct',
                     title=f'Entregas a Tiempo por {next_level.replace("_", " ").title()}',
                     hover_data=['tiempo_promedio_entrega_horas', 'costo_logistico_promedio_cop'])
        fig.update_yaxes(title='Entregas a Tiempo (%)')
        apply_chart_style(fig)
        
        comparison = {
            'avg_on_time': agg_data['entregas_a_tiempo_pct'].mean() * 100,
            'avg_delivery_time': agg_data['tiempo_promedio_entrega_horas'].mean(),
            'avg_cost': agg_data['costo_logistico_promedio_cop'].mean(),
            'best_performer': agg_data.iloc[0][next_level]
        }
        
        trend_fig = None
        if current_level_idx >= 1:
            trend_data = log_df.groupby('mes')['entregas_a_tiempo_pct'].mean().reset_index()
            trend_fig = px.line(trend_data, x='mes', y='entregas_a_tiempo_pct',
                               title='Tendencia de Entregas a Tiempo',
                               markers=True)
            apply_chart_style(trend_fig)
        
        return {
            'chart': fig,
            'data_table': agg_data,
            'comparison': comparison,
            'trend': trend_fig,
            'next_level': next_level,
            'drill_path': drill_path
        }
    
    def _create_detail_view(self, df, drill_path, metric_type):
        """Create final detail view with full data table."""
        # Show raw data with key columns
        if metric_type == 'sales':
            cols = ['periodo', 'region', 'canal', 'categoria', 'ventas_cop', 
                   'margen_estimado_cop', 'unidades_vendidas', 'ticket_promedio_cop']
        elif metric_type == 'margin':
            cols = ['periodo', 'canal', 'categoria', 'ventas_cop', 
                   'margen_estimado_cop', 'margen_estimado_pct']
        elif metric_type == 'inventory':
            cols = ['periodo', 'region', 'categoria', 'formato_tienda', 
                   'disponibilidad_pct', 'quiebre_inventario', 'rotacion_inventario']
        elif metric_type == 'customer':
            cols = ['periodo', 'segmento_cliente', 'clientes_estimados', 
                   'clv_estimado_anual_cop', 'frecuencia_compra_mensual', 'nps_estimado']
        elif metric_type == 'logistics':
            cols = ['periodo', 'region', 'canal', 'entregas_a_tiempo_pct', 
                   'tiempo_promedio_entrega_horas', 'costo_logistico_promedio_cop']
        else:
            cols = df.columns.tolist()[:10]
        
        available_cols = [c for c in cols if c in df.columns]
        detail_df = df[available_cols].head(100)
        
        return {
            'chart': None,
            'data_table': detail_df,
            'comparison': {'message': 'Detalle completo - nivel final'},
            'trend': None,
            'next_level': None,
            'drill_path': drill_path
        }

def display():
    """Test drill-down functionality."""
    manager = DrillDownManager()
    
    # Test sales drill-down at different levels
    results = []
    
    # Level 0 - by region
    sales_l0 = manager.get_sales_drilldown({})
    results.append({"_display_type": "stats", "stats": [
        ("Sales Drill Level", "0 - By Region"),
        ("Next Level", sales_l0['next_level']),
        ("Total Sales", f"${sales_l0['comparison']['total']/1e9:.1f}B"),
        ("Top Performer", sales_l0['comparison']['top_performer'])
    ]})
    results.append({"title": "Sales by Region", "fig": sales_l0['chart']})
    
    # Level 1 - drill into top region
    top_region = sales_l0['data_table'].iloc[0]['region']
    sales_l1 = manager.get_sales_drilldown({}, drill_path=[('region', top_region)])
    results.append({"_display_type": "stats", "stats": [
        ("Sales Drill Level", f"1 - {top_region} by Category"),
        ("Next Level", sales_l1['next_level']),
        ("Categories", sales_l1['comparison']['count'])
    ]})
    results.append({"title": f"Sales in {top_region} by Category", "fig": sales_l1['chart']})
    
    if sales_l1['trend']:
        results.append({"title": "Trend Analysis", "fig": sales_l1['trend']})
    
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
