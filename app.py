import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from load_data import load_all_datasets
from data_processing import get_filter_options, apply_filters
from insights_generator import generate_insights
from advanced_charts_2 import (
    create_profitability_charts,
    create_efficiency_charts,
    create_customer_behavior_charts,
    create_benchmarking_charts
)
from pdf_report_generator import ExecutiveSummaryReport
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Dashboard Ejecutivo Grupo Exito",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Corporate colors
COLORS = {
    'yellow': '#FFD200',
    'black': '#1C1C1C',
    'grey': '#E5E5E5',
    'chart_colors': ["#845EEE", "#55B685", "#E9A23B", "#DA5597", "#52B3D0"]
}

# Custom CSS
st.markdown(f"""
<style>
    .main {{
        background-color: white;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['grey']};
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['yellow']};
        color: {COLORS['black']};
    }}
    h1 {{
        color: {COLORS['black']};
    }}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return load_all_datasets()

@st.cache_data
def get_filters():
    return get_filter_options()

datasets = load_data()
filter_options = get_filters()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Dashboard Ejecutivo Grupo Exito")
with col2:
    if st.button("Generar Reporte PDF", use_container_width=True):
        with st.spinner("Generando reporte..."):
            try:
                filters = {
                    'anio': st.session_state.get('filter_year', []),
                    'mes': st.session_state.get('filter_month', []),
                    'region': st.session_state.get('filter_region', []),
                    'canal': st.session_state.get('filter_canal', []),
                    'categoria': st.session_state.get('filter_categoria', []),
                    'segmento_cliente': st.session_state.get('filter_segmento', [])
                }
                report = ExecutiveSummaryReport(filters=filters)
                output_path = report.generate_report()
                
                with open(output_path, 'rb') as f:
                    st.download_button(
                        label="Descargar PDF",
                        data=f,
                        file_name=f"Grupo_Exito_Executive_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                st.success("Reporte generado exitosamente")
            except Exception as e:
                st.error(f"Error generando reporte: {str(e)}")

# Sidebar filters
st.sidebar.header("Filtros Globales")

filter_year = st.sidebar.multiselect(
    "Ano",
    options=filter_options['years'],
    default=filter_options['years'],
    key='filter_year'
)

filter_month = st.sidebar.multiselect(
    "Mes",
    options=filter_options['months'],
    default=filter_options['months'],
    key='filter_month'
)

filter_region = st.sidebar.multiselect(
    "Region",
    options=filter_options['regions'],
    default=filter_options['regions'],
    key='filter_region'
)

filter_canal = st.sidebar.multiselect(
    "Canal",
    options=filter_options['canales'],
    default=filter_options['canales'],
    key='filter_canal'
)

filter_categoria = st.sidebar.multiselect(
    "Categoria",
    options=filter_options['categorias'],
    default=filter_options['categorias'],
    key='filter_categoria'
)

filter_segmento = st.sidebar.multiselect(
    "Segmento Cliente",
    options=filter_options['segmentos'],
    default=filter_options['segmentos'],
    key='filter_segmento'
)

# Build filters dict
filters = {
    'anio': filter_year,
    'mes': filter_month,
    'region': filter_region,
    'canal': filter_canal,
    'categoria': filter_categoria,
    'segmento_cliente': filter_segmento
}

# Helper functions
def format_currency(value):
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.0f}"

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resumen Ejecutivo",
    "Analisis Comercial",
    "Clientes y Fidelizacion",
    "Inventarios y Abastecimiento",
    "Logistica y Experiencia Omnicanal"
])

# Tab 1: Resumen Ejecutivo
with tab1:
    st.header("Resumen Ejecutivo")
    
    kpis_df = apply_filters(datasets['kpis'], filters)
    
    if len(kpis_df) > 0:
        ventas_totales = kpis_df['ventas_totales_cop'].sum()
        ventas_omnicanal = kpis_df['ventas_omnicanal_cop'].sum()
        conversion_digital = kpis_df['conversion_digital_pct'].mean()
        nps = kpis_df['nps_estimado'].mean()
        disponibilidad = kpis_df['disponibilidad_inventario_pct'].mean()
        entregas_tiempo = kpis_df['entregas_a_tiempo_pct'].mean()
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ventas Totales", format_currency(ventas_totales))
        with col2:
            st.metric("Ventas Omnicanal", format_currency(ventas_omnicanal))
        with col3:
            st.metric("Conversion Digital", f"{conversion_digital*100:.2f}%")
        with col4:
            st.metric("NPS", f"{nps:.1f}")
        
        col5, col6 = st.columns(2)
        with col5:
            st.metric("Disponibilidad Inventario", f"{disponibilidad*100:.1f}%")
        with col6:
            st.metric("Entregas a Tiempo", f"{entregas_tiempo*100:.1f}%")
        
        # Evolution chart
        st.subheader("Evolucion de Ventas")
        kpis_sorted = kpis_df.sort_values('periodo')
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=kpis_sorted['mes'],
            y=kpis_sorted['ventas_totales_cop'],
            name='Ventas Totales',
            mode='lines+markers'
        ))
        fig.add_trace(go.Scatter(
            x=kpis_sorted['mes'],
            y=kpis_sorted['ventas_omnicanal_cop'],
            name='Ventas Omnicanal',
            mode='lines+markers'
        ))
        fig.update_layout(
            template='plotly',
            xaxis_title='Mes',
            yaxis_title='Ventas (COP)',
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Insights
        st.subheader("Insights Automaticos")
        insights = generate_insights(filters)
        for i, insight in enumerate(insights, 1):
            st.markdown(f"{i}. {insight}")
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados")

# Tab 2: Analisis Comercial
with tab2:
    st.header("Analisis Comercial")
    
    ventas_df = apply_filters(datasets['ventas'], filters)
    
    if len(ventas_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Ventas por Canal")
            ventas_canal = ventas_df.groupby('canal')['ventas_cop'].sum().sort_values(ascending=False).reset_index()
            import plotly.express as px
            fig = px.bar(ventas_canal, x='canal', y='ventas_cop')
            fig.update_layout(template='plotly', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Participacion por Canal")
            fig = px.pie(ventas_canal, values='ventas_cop', names='canal')
            fig.update_layout(template='plotly', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Analisis de Rentabilidad")
        prof_charts = create_profitability_charts(filters)
        for chart in prof_charts:
            chart.update_layout(template='plotly')
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados")

# Tab 3: Clientes y Fidelizacion
with tab3:
    st.header("Clientes y Fidelizacion")
    
    clientes_df = apply_filters(datasets['clientes'], filters)
    
    if len(clientes_df) > 0:
        st.subheader("Clientes por Segmento")
        clientes_seg = clientes_df.groupby('segmento_cliente')['clientes_estimados'].sum().reset_index()
        import plotly.express as px
        fig = px.bar(clientes_seg, x='segmento_cliente', y='clientes_estimados')
        fig.update_layout(template='plotly', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Analisis de Comportamiento")
        behavior_charts = create_customer_behavior_charts(filters)
        for chart in behavior_charts:
            chart.update_layout(template='plotly')
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados")

# Tab 4: Inventarios
with tab4:
    st.header("Inventarios y Abastecimiento")
    
    inventarios_df = apply_filters(datasets['inventarios'], filters)
    
    if len(inventarios_df) > 0:
        st.subheader("Disponibilidad por Region")
        disp_region = inventarios_df.groupby('region')['disponibilidad_pct'].mean().reset_index()
        import plotly.express as px
        fig = px.bar(disp_region, x='region', y='disponibilidad_pct')
        fig.update_layout(template='plotly', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Analisis de Eficiencia Operativa")
        eff_charts = create_efficiency_charts(filters)
        for chart in eff_charts:
            chart.update_layout(template='plotly')
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados")

# Tab 5: Logistica
with tab5:
    st.header("Logistica y Experiencia Omnicanal")
    
    logistica_df = apply_filters(datasets['logistica'], filters)
    
    if len(logistica_df) > 0:
        st.subheader("Entregas a Tiempo por Region")
        entregas_region = logistica_df.groupby('region')['entregas_a_tiempo_pct'].mean().reset_index()
        import plotly.express as px
        fig = px.bar(entregas_region, x='region', y='entregas_a_tiempo_pct')
        fig.update_layout(template='plotly', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Analisis Comparativo")
        bench_charts = create_benchmarking_charts(filters)
        for chart in bench_charts:
            chart.update_layout(template='plotly')
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados")

# Footer
st.markdown("---")
st.markdown("**Dashboard Ejecutivo Grupo Exito** | Generado con Streamlit")
