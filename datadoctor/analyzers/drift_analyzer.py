from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from datadoctor._compat import is_str_col

_KS_SIGNIFICANCE = 0.05
_CATEGORY_DRIFT_THRESHOLD = 0.05


def analyze(old_df: pd.DataFrame, new_df: pd.DataFrame) -> dict[str, Any]:
    distribution_drift: dict[str, float] = {}
    category_drift: dict[str, dict[str, Any]] = {}
    missing_value_drift: dict[str, float] = {}
    drifted: set[str] = set()

    common_cols = set(old_df.columns) & set(new_df.columns)

    for col in sorted(common_cols):
        old_s = old_df[col]
        new_s = new_df[col]

        # Missing-value drift
        old_null = old_s.isna().mean()
        new_null = new_s.isna().mean()
        mv_change = round(abs(new_null - old_null) * 100, 2)
        missing_value_drift[col] = mv_change
        if mv_change > 5.0:
            drifted.add(col)

        # Numeric distribution drift (KS test)
        if pd.api.types.is_numeric_dtype(old_s) and pd.api.types.is_numeric_dtype(new_s):
            old_clean = old_s.dropna().astype(float)
            new_clean = new_s.dropna().astype(float)
            if len(old_clean) > 1 and len(new_clean) > 1:
                stat, p_value = stats.ks_2samp(old_clean, new_clean)
                distribution_drift[col] = round(float(stat), 4)
                if p_value < _KS_SIGNIFICANCE:
                    drifted.add(col)

        # Categorical distribution drift
        elif is_str_col(old_s) and is_str_col(new_s):
            old_freq = old_s.value_counts(normalize=True)
            new_freq = new_s.value_counts(normalize=True)
            all_cats = set(old_freq.index) | set(new_freq.index)
            changes: dict[str, Any] = {}
            for cat in all_cats:
                old_p = float(old_freq.get(cat, 0.0))
                new_p = float(new_freq.get(cat, 0.0))
                if abs(new_p - old_p) > _CATEGORY_DRIFT_THRESHOLD:
                    changes[str(cat)] = {
                        "old_pct": round(old_p * 100, 2),
                        "new_pct": round(new_p * 100, 2),
                    }
            if changes:
                category_drift[col] = changes
                drifted.add(col)

    return {
        "distribution_drift": distribution_drift,
        "category_drift": category_drift,
        "missing_value_drift": missing_value_drift,
        "drifted_columns": sorted(drifted),
    }
