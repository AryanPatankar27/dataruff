from __future__ import annotations

import pandas as pd
import pytest

from dataruff.analyzers.duplicate import analyze


def test_no_duplicates_returns_empty():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    assert analyze(df) == []


def test_single_duplicate_detected():
    df = pd.DataFrame({"a": [1, 2, 2], "b": ["x", "y", "y"]})
    issues = analyze(df)
    assert len(issues) == 1
    assert issues[0].type == "duplicate_rows"
    assert issues[0].count == 1


def test_duplicate_count_correct():
    df = pd.DataFrame({"a": [1, 1, 1, 2]})
    issues = analyze(df)
    assert issues[0].count == 2  # two rows are duplicates of the first


def test_high_severity_above_threshold():
    # >10% duplicates
    data = [1] * 11 + [2]
    df = pd.DataFrame({"a": data})
    issues = analyze(df)
    assert issues[0].severity == "high"


def test_medium_severity_below_threshold():
    # ≤10% duplicates: 1 dup in 101 rows
    data = list(range(100)) + [0]
    df = pd.DataFrame({"a": data})
    issues = analyze(df)
    assert issues[0].severity == "medium"


def test_details_contain_percentage_and_indices():
    df = pd.DataFrame({"a": [1, 2, 2]})
    issues = analyze(df)
    assert "percentage" in issues[0].details
    assert "duplicate_indices" in issues[0].details
    assert issues[0].details["percentage"] == pytest.approx(33.33, abs=0.01)


def test_empty_dataframe_returns_empty():
    df = pd.DataFrame({"a": []})
    assert analyze(df) == []


def test_all_duplicates_high_severity():
    df = pd.DataFrame({"a": [1, 1, 1, 1, 1]})
    issues = analyze(df)
    assert issues[0].severity == "high"
    assert issues[0].count == 4
