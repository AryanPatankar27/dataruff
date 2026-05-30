from __future__ import annotations

import re

import pandas as pd

from datadoctor.models import Issue, ScoreBreakdown

_WEIGHTS = {
    "completeness": 0.25,
    "validity": 0.25,
    "consistency": 0.20,
    "uniqueness": 0.20,
    "schema_compliance": 0.10,
}

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_VALIDITY_ISSUE_TYPES = {"invalid_email", "invalid_date", "mixed_types"}
_CONSISTENCY_ISSUE_TYPES = {"mixed_types", "numeric_as_string", "inconsistent_date_format"}


def compute(
    df: pd.DataFrame, issues: list[Issue], schema: dict | None = None
) -> ScoreBreakdown:
    completeness = _completeness(df)
    validity = _validity(df, issues)
    consistency = _consistency(df, issues)
    uniqueness = _uniqueness(df, issues)
    schema_compliance = _schema_compliance(df, schema) if schema else 100.0

    overall = (
        completeness * _WEIGHTS["completeness"]
        + validity * _WEIGHTS["validity"]
        + consistency * _WEIGHTS["consistency"]
        + uniqueness * _WEIGHTS["uniqueness"]
        + schema_compliance * _WEIGHTS["schema_compliance"]
    )

    return ScoreBreakdown(
        overall=int(round(overall)),
        completeness=round(completeness, 1),
        validity=round(validity, 1),
        consistency=round(consistency, 1),
        uniqueness=round(uniqueness, 1),
        schema_compliance=round(schema_compliance, 1),
    )


def _completeness(df: pd.DataFrame) -> float:
    if df.empty or df.shape[0] * df.shape[1] == 0:
        return 100.0
    total = df.shape[0] * df.shape[1]
    null_count = int(df.isna().sum().sum())
    return max(0.0, (1 - null_count / total) * 100)


def _validity(df: pd.DataFrame, issues: list[Issue]) -> float:
    total = df.shape[0] * df.shape[1]
    if total == 0:
        return 100.0
    invalid = sum(i.count for i in issues if i.type in _VALIDITY_ISSUE_TYPES)
    return max(0.0, (1 - min(invalid, total) / total) * 100)


def _consistency(df: pd.DataFrame, issues: list[Issue]) -> float:
    n_cols = max(df.shape[1], 1)
    inconsistent = sum(1 for i in issues if i.type in _CONSISTENCY_ISSUE_TYPES)
    penalty = (inconsistent / n_cols) * 100
    return max(0.0, 100.0 - penalty)


def _uniqueness(df: pd.DataFrame, issues: list[Issue]) -> float:
    if len(df) == 0:
        return 100.0
    dup_issues = [i for i in issues if i.type == "duplicate_rows"]
    if not dup_issues:
        return 100.0
    total_dups = sum(i.count for i in dup_issues)
    dup_ratio = min(total_dups / len(df), 1.0)
    return max(0.0, (1 - dup_ratio) * 100)


def _schema_compliance(df: pd.DataFrame, schema: dict) -> float:
    if not schema:
        return 100.0

    total_checks = len(schema) * max(len(df), 1)
    failed = 0

    for col, rule in schema.items():
        if col not in df.columns:
            failed += len(df)
            continue

        series = df[col]

        if rule == "email":
            str_series = series.dropna().astype(str)
            fails = (~str_series.str.match(_EMAIL_RE)).sum()
            failed += int(fails)

        elif rule == "not_null":
            failed += int(series.isna().sum())

        elif rule == "unique":
            failed += int(series.duplicated().sum())

        elif rule == "positive":
            numeric = pd.to_numeric(series, errors="coerce")
            failed += int((numeric <= 0).sum())

        elif isinstance(rule, str) and rule.startswith("regex:"):
            pattern = re.compile(rule[6:])
            str_series = series.dropna().astype(str)
            fails = (~str_series.str.match(pattern)).sum()
            failed += int(fails)

        elif isinstance(rule, str) and "-" in rule:
            try:
                lo_str, hi_str = rule.split("-", 1)
                lo, hi = float(lo_str), float(hi_str)
                numeric = pd.to_numeric(series, errors="coerce")
                fails = int(((numeric < lo) | (numeric > hi)).sum())
                failed += fails
            except ValueError:
                pass

    return max(0.0, (1 - failed / total_checks) * 100)
