from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from dataruff.loader import load
from dataruff.models import ComparisonReport


def compare(
    old_source: Union[str, Path, pd.DataFrame],
    new_source: Union[str, Path, pd.DataFrame],
) -> ComparisonReport:
    old_df = load(old_source)
    new_df = load(new_source)

    old_cols = set(old_df.columns)
    new_cols = set(new_df.columns)
    cols_added = sorted(new_cols - old_cols)
    cols_removed = sorted(old_cols - new_cols)

    type_changes: dict[str, tuple[str, str]] = {}
    for col in old_cols & new_cols:
        if str(old_df[col].dtype) != str(new_df[col].dtype):
            type_changes[col] = (str(old_df[col].dtype), str(new_df[col].dtype))

    common_cols = sorted(old_cols & new_cols)
    if common_cols:
        old_hashes = set(
            pd.util.hash_pandas_object(old_df[common_cols], index=False)
        )
        new_hashes = set(
            pd.util.hash_pandas_object(new_df[common_cols], index=False)
        )
        rows_added = len(new_hashes - old_hashes)
        rows_deleted = len(old_hashes - new_hashes)
    else:
        rows_added = max(0, len(new_df) - len(old_df))
        rows_deleted = max(0, len(old_df) - len(new_df))

    return ComparisonReport(
        rows_added=rows_added,
        rows_deleted=rows_deleted,
        columns_added=cols_added,
        columns_removed=cols_removed,
        type_changes=type_changes,
        value_changes=rows_added + rows_deleted,
    )
