import pandas as pd
from pathlib import Path

def load_all_datasets():
    """Load all 6 datasets for the dashboard."""
    uploads = Path(__file__).parent.parent / "data"
    
    datasets = {
        'ventas': pd.read_csv(uploads / "01_ventas_mensuales_canal_categoria_region.csv"),
        'inventarios': pd.read_csv(uploads / "02_inventarios_region_formato_categoria.csv"),
        'conversion': pd.read_csv(uploads / "03_conversion_digital_funnel.csv"),
        'clientes': pd.read_csv(uploads / "04_clientes_segmentos_clv_nps.csv"),
        'logistica': pd.read_csv(uploads / "05_logistica_entregas_region_canal.csv"),
        'kpis': pd.read_csv(uploads / "06_kpis_dashboard_mensual.csv"),
        'diccionario': pd.read_csv(uploads / "00_diccionario_datasets.csv")
    }
    
    return datasets

def display():
    datasets = load_all_datasets()
    
    stats = []
    for name, df in datasets.items():
        if name != 'diccionario':
            stats.append((name.capitalize(), f"{len(df):,} rows × {len(df.columns)} cols"))
    
    results = [{"_display_type": "stats", "stats": stats}]
    
    # Show structure of each dataset
    for name, df in datasets.items():
        if name != 'diccionario':
            results.append({
                "title": f"{name.capitalize()} Dataset",
                "df": pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null': df.count().values,
                    'Sample': [str(df[col].iloc[0]) if len(df) > 0 else '' for col in df.columns]
                })
            })
    
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
