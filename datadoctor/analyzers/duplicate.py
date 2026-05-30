from __future__ import annotations

import pandas as pd

from datadoctor.models import Issue

_HIGH_THRESHOLD = 0.10  # >10% duplicates → high severity


def analyze(df: pd.DataFrame) -> list[Issue]:
    if df.empty:
        return []

    mask = df.duplicated()
    dup_count = int(mask.sum())

    if dup_count == 0:
        return []

    pct = dup_count / len(df)
    severity = "high" if pct > _HIGH_THRESHOLD else "medium"

    return [
        Issue(
            type="duplicate_rows",
            severity=severity,
            count=dup_count,
            details={
                "percentage": round(pct * 100, 2),
                "duplicate_indices": df[mask].index.tolist(),
            },
        )
    ]
