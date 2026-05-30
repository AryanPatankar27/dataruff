from __future__ import annotations

import pandas as pd

from datadoctor.models import Issue

_HIGH_NULL_THRESHOLD = 0.30
_MEDIUM_NULL_THRESHOLD = 0.05


def analyze(df: pd.DataFrame) -> list[Issue]:
    if df.empty:
        return []

    issues: list[Issue] = []

    empty_cols = [col for col in df.columns if df[col].isna().all()]
    if empty_cols:
        issues.append(
            Issue(
                type="empty_columns",
                severity="high",
                count=len(empty_cols),
                details={"columns": empty_cols},
            )
        )

    for col in df.columns:
        if col in empty_cols:
            continue
        null_count = int(df[col].isna().sum())
        if null_count == 0:
            continue
        pct = null_count / len(df)
        if pct > _HIGH_NULL_THRESHOLD:
            severity = "high"
        elif pct > _MEDIUM_NULL_THRESHOLD:
            severity = "medium"
        else:
            severity = "low"

        issues.append(
            Issue(
                type="null_values",
                severity=severity,
                count=null_count,
                column=col,
                details={"percentage": round(pct * 100, 2)},
            )
        )

    return issues
