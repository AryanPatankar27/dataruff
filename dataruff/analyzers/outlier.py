from __future__ import annotations

import numpy as np
import pandas as pd

from dataruff.models import Issue

_MIN_ROWS = 4
_HIGH_OUTLIER_THRESHOLD = 0.10


def analyze(df: pd.DataFrame, method: str = "iqr") -> list[Issue]:
    issues: list[Issue] = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < _MIN_ROWS:
            continue

        if method == "zscore":
            mask = _zscore_mask(series)
        else:
            mask = _iqr_mask(series)

        count = int(mask.sum())
        if count == 0:
            continue

        pct = count / len(series)
        severity = "high" if pct > _HIGH_OUTLIER_THRESHOLD else "medium"

        issues.append(
            Issue(
                type="outlier",
                severity=severity,
                count=count,
                column=col,
                details={
                    "method": method,
                    "percentage": round(pct * 100, 2),
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "mean": round(float(series.mean()), 4),
                    "std": round(float(series.std()), 4),
                },
            )
        )

    return issues


def get_outlier_mask(series: pd.Series, method: str = "iqr") -> pd.Series:
    if method == "zscore":
        return _zscore_mask(series)
    return _iqr_mask(series)


def _iqr_mask(series: pd.Series) -> pd.Series:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (series < lower) | (series > upper)


def _zscore_mask(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    std = series.std()
    if std == 0:
        return pd.Series(False, index=series.index)
    z = (series - series.mean()) / std
    return z.abs() > threshold
