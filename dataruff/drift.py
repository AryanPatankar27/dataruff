from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from dataruff.analyzers.drift_analyzer import analyze as _drift_analyze
from dataruff.loader import load
from dataruff.models import DriftReport


def detect_drift(
    old_source: Union[str, Path, pd.DataFrame],
    new_source: Union[str, Path, pd.DataFrame],
) -> DriftReport:
    old_df = load(old_source)
    new_df = load(new_source)
    result = _drift_analyze(old_df, new_df)
    return DriftReport(**result)
