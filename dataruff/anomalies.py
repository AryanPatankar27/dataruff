from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import numpy as np
import pandas as pd

from dataruff.analyzers.outlier import analyze as _outlier_analyze
from dataruff.analyzers.outlier import get_outlier_mask
from dataruff.loader import load


def find_anomalies(
    source: Union[str, Path, pd.DataFrame],
    method: str = "iqr",
) -> dict[str, Any]:
    if method not in ("iqr", "zscore"):
        raise ValueError(f"Unknown method '{method}'. Choose 'iqr' or 'zscore'.")

    df = load(source)
    issues = _outlier_analyze(df, method=method)

    total = sum(i.count for i in issues)

    # Collect the union of anomalous row indices
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    anomalous_mask = pd.Series(False, index=df.index)
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) >= 4:
            col_mask = get_outlier_mask(series, method=method)
            full_mask = col_mask.reindex(df.index, fill_value=False)
            anomalous_mask = anomalous_mask | full_mask

    return {
        "total_anomalous_records": int(anomalous_mask.sum()),
        "method": method,
        "by_column": [
            {
                "column": i.column,
                "count": i.count,
                "percentage": i.details.get("percentage"),
                "severity": i.severity,
                "min": i.details.get("min"),
                "max": i.details.get("max"),
                "mean": i.details.get("mean"),
            }
            for i in issues
        ],
        "anomalous_indices": anomalous_mask[anomalous_mask].index.tolist(),
    }
