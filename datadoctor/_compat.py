"""
Pandas 2.x / 3.x dtype compatibility.

In pandas 2.x string columns have dtype ``object`` (dtype.name == 'object').
In pandas 3.x (infer_string=True by default) they have a ``StringDtype``
instance whose repr shows as ``dtype: str`` (dtype.name may be 'str',
'string', or 'string[python]' depending on the sub-release).

The safest guard is ``isinstance(dtype, pd.StringDtype)`` — it covers every
StringDtype variant without relying on the `.name` attribute.
"""
from __future__ import annotations

import pandas as pd


def is_str_col(series: pd.Series) -> bool:
    """
    True for any string-like column, pandas 2.x and 3.x compatible.

    - pandas 2.x default:  dtype == object   (plain Python objects)
    - pandas 3.x default:  isinstance(dtype, pd.StringDtype)
                            (repr shows as ``dtype: str``)
    """
    dtype = series.dtype
    # Fast path: classic object dtype used by pandas 2.x
    if dtype == object:
        return True
    # All StringDtype variants (pd.StringDtype was added in pandas 1.0 and is
    # the default in pandas 3.x regardless of storage backend)
    if hasattr(pd, "StringDtype") and isinstance(dtype, pd.StringDtype):
        return True
    # Extra safety-net: catch any future/vendor string dtype by name
    name = getattr(dtype, "name", "")
    return name in ("str", "string", "large_string") or "string" in str(dtype).lower()


def str_columns(df: pd.DataFrame) -> list[str]:
    """Return names of all string-like columns in *df*."""
    return [col for col in df.columns if is_str_col(df[col])]
