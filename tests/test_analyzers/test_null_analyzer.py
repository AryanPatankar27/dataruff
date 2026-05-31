from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from dataruff.analyzers.null_analyzer import analyze


def test_clean_df_no_issues(clean_df):
    issues = analyze(clean_df)
    assert issues == []


def test_empty_column_detected():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [None, None, None]})
    issues = analyze(df)
    empty = [i for i in issues if i.type == "empty_columns"]
    assert len(empty) == 1
    assert empty[0].count == 1
    assert "b" in empty[0].details["columns"]


def test_null_values_detected_per_column():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", "z"]})
    issues = analyze(df)
    null_issues = [i for i in issues if i.type == "null_values"]
    assert len(null_issues) == 1
    assert null_issues[0].column == "a"
    assert null_issues[0].count == 1


def test_high_severity_above_30_pct():
    df = pd.DataFrame({"a": [None] * 4 + [1] * 6})  # 40% null
    issues = analyze(df)
    null_issues = [i for i in issues if i.type == "null_values"]
    assert null_issues[0].severity == "high"


def test_medium_severity_between_5_and_30_pct():
    nulls = [None] * 10 + [1] * 90  # 10% null
    df = pd.DataFrame({"a": nulls})
    issues = analyze(df)
    null_issues = [i for i in issues if i.type == "null_values"]
    assert null_issues[0].severity == "medium"


def test_low_severity_below_5_pct():
    nulls = [None] + [1] * 99  # 1% null
    df = pd.DataFrame({"a": nulls})
    issues = analyze(df)
    null_issues = [i for i in issues if i.type == "null_values"]
    assert null_issues[0].severity == "low"


def test_null_percentage_in_details():
    df = pd.DataFrame({"a": [None, None, 3, 4]})
    issues = analyze(df)
    null_issues = [i for i in issues if i.column == "a"]
    assert null_issues[0].details["percentage"] == 50.0


def test_empty_dataframe_returns_empty():
    df = pd.DataFrame({"a": []})
    assert analyze(df) == []


def test_multiple_null_columns():
    df = pd.DataFrame({"a": [None, 1], "b": [None, None], "c": [1, 2]})
    issues = analyze(df)
    empty = [i for i in issues if i.type == "empty_columns"]
    null = [i for i in issues if i.type == "null_values"]
    assert len(empty) == 1  # column b is fully empty
    assert len(null) == 1   # column a has partial nulls
