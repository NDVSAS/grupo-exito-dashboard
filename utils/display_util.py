import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

def _serialize_result(obj):
    """Convierte objetos no serializables a formatos compatibles con JSON."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, Path):
        return str(obj)
    try:
        import numpy as np
        import pandas as pd

        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if isinstance(obj, pd.Series):
            return obj.to_dict()
    except Exception:
        pass

    return str(obj)

def _dumps(obj):
    """Serializa objetos Python a JSON con soporte para pandas/numpy."""
    return json.dumps(obj, ensure_ascii=False, default=_serialize_result)
