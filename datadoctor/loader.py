from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd


def load(source: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy()

    path = Path(source)
    suffix = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(
            f"Unsupported file format: '{suffix}'. Supported formats: .csv, .xlsx, .xls"
        )
