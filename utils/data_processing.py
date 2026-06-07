import pandas as pd
from load_data import load_all_datasets

def get_filter_options():
    """Get unique values for all filter dimensions."""
    datasets = load_all_datasets()
    
    # Get unique years
    years = sorted(datasets['kpis']['anio'].unique())
    
    # Get unique months (preserve order)
    month_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    months = [m for m in month_order if m in datasets['kpis']['mes'].unique()]
    
    # Get unique regions
    regions = sorted(datasets['ventas']['region'].unique())
    
    # Get unique channels
    canales = sorted(datasets['ventas']['canal'].unique())
    
    # Get unique categories
    categorias = sorted(datasets['ventas']['categoria'].unique())
    
    # Get unique customer segments
    segmentos = sorted(datasets['clientes']['segmento_cliente'].unique())
    
    return {
        'years': years,
        'months': months,
        'regions': regions,
        'canales': canales,
        'categorias': categorias,
        'segmentos': segmentos
    }

def apply_filters(df, filters):
    """Apply filters to a dataframe."""
    filtered = df.copy()
    
    if 'anio' in filters and filters['anio'] and 'anio' in df.columns:
        filtered = filtered[filtered['anio'].isin(filters['anio'])]
    
    if 'mes' in filters and filters['mes'] and 'mes' in df.columns:
        filtered = filtered[filtered['mes'].isin(filters['mes'])]
    
    if 'region' in filters and filters['region'] and 'region' in df.columns:
        filtered = filtered[filtered['region'].isin(filters['region'])]
    
    if 'canal' in filters and filters['canal'] and 'canal' in df.columns:
        filtered = filtered[filtered['canal'].isin(filters['canal'])]
    
    if 'categoria' in filters and filters['categoria'] and 'categoria' in df.columns:
        filtered = filtered[filtered['categoria'].isin(filters['categoria'])]
    
    if 'segmento_cliente' in filters and filters['segmento_cliente'] and 'segmento_cliente' in df.columns:
        filtered = filtered[filtered['segmento_cliente'].isin(filters['segmento_cliente'])]
    
    return filtered

def display():
    options = get_filter_options()
    
    stats = [
        ("Years", f"{len(options['years'])} options"),
        ("Months", f"{len(options['months'])} options"),
        ("Regions", f"{len(options['regions'])} options"),
        ("Canales", f"{len(options['canales'])} options"),
        ("Categorias", f"{len(options['categorias'])} options"),
        ("Segmentos", f"{len(options['segmentos'])} options")
    ]
    
    return [
        {"_display_type": "stats", "stats": stats},
        {"title": "Filter Options", "df": pd.DataFrame({
            'Dimension': ['Years', 'Months', 'Regions', 'Canales', 'Categorias', 'Segmentos'],
            'Values': [
                ', '.join(map(str, options['years'])),
                ', '.join(options['months'][:3]) + '...',
                ', '.join(options['regions'][:3]) + '...',
                ', '.join(options['canales']),
                ', '.join(options['categorias'][:3]) + '...',
                ', '.join(options['segmentos'][:2]) + '...'
            ]
        })}
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
