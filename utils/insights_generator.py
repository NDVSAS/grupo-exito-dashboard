import pandas as pd
from load_data import load_all_datasets
from data_processing import apply_filters

def generate_insights(filters=None):
    """Generate automatic insights based on the data."""
    if filters is None:
        filters = {}
    
    datasets = load_all_datasets()
    
    # Apply filters
    ventas_df = apply_filters(datasets['ventas'], filters)
    inventarios_df = apply_filters(datasets['inventarios'], filters)
    clientes_df = apply_filters(datasets['clientes'], filters)
    logistica_df = apply_filters(datasets['logistica'], filters)
    kpis_df = apply_filters(datasets['kpis'], filters)
    
    insights = []
    
    # 1. Canal con mayores ventas
    if len(ventas_df) > 0:
        canal_ventas = ventas_df.groupby('canal')['ventas_cop'].sum().sort_values(ascending=False)
        top_canal = canal_ventas.index[0]
        top_canal_ventas = canal_ventas.iloc[0]
        pct_total = (top_canal_ventas / canal_ventas.sum()) * 100
        insights.append(f"**{top_canal}** lidera con ${top_canal_ventas/1e9:.1f}B ({pct_total:.1f}% del total)")
    
    # 2. Categoría líder
    if len(ventas_df) > 0:
        cat_ventas = ventas_df.groupby('categoria')['ventas_cop'].sum().sort_values(ascending=False)
        top_cat = cat_ventas.index[0]
        top_cat_ventas = cat_ventas.iloc[0]
        insights.append(f"**{top_cat}** es la categoría líder con ${top_cat_ventas/1e9:.1f}B")
    
    # 3. Región con menor disponibilidad
    if len(inventarios_df) > 0:
        region_disp = inventarios_df.groupby('region')['disponibilidad_pct'].mean().sort_values()
        low_region = region_disp.index[0]
        low_disp = region_disp.iloc[0] * 100
        insights.append(f"**{low_region}** tiene la menor disponibilidad ({low_disp:.1f}%)")
    
    # 4. Segmento con mayor CLV
    if len(clientes_df) > 0:
        seg_clv = clientes_df.groupby('segmento_cliente')['clv_estimado_anual_cop'].mean().sort_values(ascending=False)
        top_seg = seg_clv.index[0]
        top_clv = seg_clv.iloc[0]
        insights.append(f"**{top_seg}** tiene el mayor CLV (${top_clv:,.0f})")
    
    # 5. Región con mayor tiempo de entrega
    if len(logistica_df) > 0:
        region_tiempo = logistica_df.groupby('region')['tiempo_promedio_entrega_horas'].mean().sort_values(ascending=False)
        slow_region = region_tiempo.index[0]
        slow_tiempo = region_tiempo.iloc[0]
        insights.append(f"**{slow_region}** tiene el mayor tiempo de entrega ({slow_tiempo:.0f} horas)")
    
    # 6. Tendencia mensual de ventas
    if len(kpis_df) > 0 and len(kpis_df) >= 2:
        kpis_sorted = kpis_df.sort_values('periodo')
        first_month = kpis_sorted.iloc[0]['ventas_totales_cop']
        last_month = kpis_sorted.iloc[-1]['ventas_totales_cop']
        change_pct = ((last_month - first_month) / first_month) * 100
        trend = "crecimiento" if change_pct > 0 else "decrecimiento"
        insights.append(f"Ventas muestran {trend} de {abs(change_pct):.1f}% en el período")
    
    # 7. Riesgo de quiebre de inventario
    if len(inventarios_df) > 0:
        high_risk = inventarios_df[inventarios_df['disponibilidad_pct'] < 0.5]
        if len(high_risk) > 0:
            risk_count = len(high_risk)
            total_count = len(inventarios_df)
            risk_pct = (risk_count / total_count) * 100
            insights.append(f"**{risk_pct:.1f}%** de SKUs en riesgo de quiebre (disponibilidad < 50%)")
        else:
            insights.append("Inventarios estables sin riesgo crítico de quiebre")
    
    return insights

def display():
    insights = generate_insights()
    
    insights_text = "\n\n".join([f"{i+1}. {insight}" for i, insight in enumerate(insights)])
    
    return {"_display_type": "markdown", "value": f"## AI Insights\n\n{insights_text}"}

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
