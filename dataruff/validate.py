from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Union

import pandas as pd

from dataruff.loader import load
from dataruff.scoring.engine import _schema_compliance

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def validate(
    source: Union[str, Path, pd.DataFrame],
    schema: dict[str, str],
) -> dict[str, Any]:
    df = load(source)
    compliance_score = _schema_compliance(df, schema)
    violations = _collect_violations(df, schema)

    return {
        "schema_compliance_score": round(compliance_score, 1),
        "violations": violations,
        "passed": len(violations) == 0,
    }


def _collect_violations(df: pd.DataFrame, schema: dict[str, str]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []

    for col, rule in schema.items():
        if col not in df.columns:
            violations.append({"column": col, "rule": rule, "error": "column_not_found"})
            continue

        series = df[col]

        if rule == "email":
            str_s = series.dropna().astype(str)
            fails = str_s[~str_s.str.match(_EMAIL_RE)]
            if len(fails) > 0:
                violations.append({
                    "column": col,
                    "rule": rule,
                    "violation_count": len(fails),
                    "examples": fails.head(3).tolist(),
                })

        elif rule == "not_null":
            null_count = int(series.isna().sum())
            if null_count > 0:
                violations.append({
                    "column": col,
                    "rule": rule,
                    "violation_count": null_count,
                })

        elif rule == "unique":
            dup_count = int(series.duplicated().sum())
            if dup_count > 0:
                violations.append({
                    "column": col,
                    "rule": rule,
                    "violation_count": dup_count,
                })

        elif rule == "positive":
            numeric = pd.to_numeric(series, errors="coerce")
            fails = int((numeric <= 0).sum())
            if fails > 0:
                violations.append({
                    "column": col,
                    "rule": rule,
                    "violation_count": fails,
                })

        elif isinstance(rule, str) and rule.startswith("regex:"):
            pattern = re.compile(rule[6:])
            str_s = series.dropna().astype(str)
            fails = str_s[~str_s.str.match(pattern)]
            if len(fails) > 0:
                violations.append({
                    "column": col,
                    "rule": rule,
                    "violation_count": len(fails),
                    "examples": fails.head(3).tolist(),
                })

        elif isinstance(rule, str) and "-" in rule:
            try:
                lo_str, hi_str = rule.split("-", 1)
                lo, hi = float(lo_str), float(hi_str)
                numeric = pd.to_numeric(series, errors="coerce")
                out_of_range = numeric[(numeric < lo) | (numeric > hi)]
                if len(out_of_range) > 0:
                    violations.append({
                        "column": col,
                        "rule": rule,
                        "violation_count": len(out_of_range),
                        "out_of_range_values": out_of_range.head(3).tolist(),
                    })
            except ValueError:
                violations.append({"column": col, "rule": rule, "error": "invalid_rule_format"})

    return violations
