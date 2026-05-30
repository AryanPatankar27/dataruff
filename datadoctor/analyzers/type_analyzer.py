from __future__ import annotations

import pandas as pd

from datadoctor.models import Issue


def analyze(df: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []

    for col in df.columns:
        if df[col].dtype != object:
            continue

        series = df[col].dropna()
        if len(series) == 0:
            continue

        # Detect mixed Python types (e.g., int and str coexisting)
        type_counts: dict[str, int] = {}
        for val in series:
            t = type(val).__name__
            type_counts[t] = type_counts.get(t, 0) + 1

        if len(type_counts) > 1 and not set(type_counts.keys()) <= {"str", "bytes"}:
            issues.append(
                Issue(
                    type="mixed_types",
                    severity="medium",
                    count=len(series),
                    column=col,
                    details={"types_found": list(type_counts.keys())},
                )
            )
            continue  # skip numeric-as-string check for mixed columns

        # Detect numeric values stored as strings
        numeric_mask = pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce").notna()
        if numeric_mask.all() and len(series) > 0:
            issues.append(
                Issue(
                    type="numeric_as_string",
                    severity="low",
                    count=len(series),
                    column=col,
                    details={"suggestion": f"Column '{col}' contains numeric values stored as strings."},
                )
            )

    return issues
