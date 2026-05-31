"""
Pandas 2.x / 3.x dtype compatibility.

In pandas 2.x string columns have dtype ``object``.
In pandas 3.x they have dtype ``StringDtype`` (name='string').
Every guard that used ``series.dtype == object`` is replaced with
``is_str_col(series)`` so both versions work.
"""
from __future__ import annotations

import pandas as pd

# dtype names that represent text data across pandas versions
_STR_DTYPE_NAMES = frozenset({"object", "string", "large_string"})


def is_str_col(series: pd.Series) -> bool:
    """True for object and StringDtype columns (pandas 2.x and 3.x)."""
    return series.dtype == object or series.dtype.name in _STR_DTYPE_NAMES


def str_columns(df: pd.DataFrame) -> list[str]:
    """Return names of all string-like columns in *df*."""
    return [col for col in df.columns if is_str_col(df[col])]
