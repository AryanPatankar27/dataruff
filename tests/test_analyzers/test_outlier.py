from __future__ import annotations

import pandas as pd
import pytest

from dataruff.analyzers.outlier import analyze, get_outlier_mask, _iqr_mask, _zscore_mask


def test_no_outliers_clean_data():
    df = pd.DataFrame({"value": list(range(20))})
    issues = analyze(df)
    assert issues == []


def test_extreme_outlier_detected_iqr():
    values = list(range(50)) + [500]
    df = pd.DataFrame({"value": values})
    issues = analyze(df, method="iqr")
    assert len(issues) == 1
    assert issues[0].type == "outlier"
    assert issues[0].column == "value"


def test_extreme_outlier_detected_zscore():
    values = list(range(50)) + [500]
    df = pd.DataFrame({"value": values})
    issues = analyze(df, method="zscore")
    assert len(issues) == 1
    assert issues[0].type == "outlier"


def test_high_severity_many_outliers():
    # Tight cluster + >10% extreme outliers so IQR clearly flags them
    normal = [10.0] * 15
    outliers = [10000.0, 20000.0]  # 2/17 ≈ 11.8% → high
    df = pd.DataFrame({"val": normal + outliers})
    issues = analyze(df)
    assert len(issues) > 0
    assert issues[0].severity == "high"


def test_medium_severity_few_outliers():
    # Tight cluster + single extreme outlier = ≤10% → medium
    normal = [10.0] * 100
    df = pd.DataFrame({"val": normal + [10000.0]})  # 1/101 ≈ 1% → medium
    issues = analyze(df)
    assert len(issues) > 0
    assert issues[0].severity == "medium"


def test_details_contain_stats():
    values = list(range(50)) + [500]
    df = pd.DataFrame({"value": values})
    issues = analyze(df)
    d = issues[0].details
    assert "percentage" in d
    assert "min" in d
    assert "max" in d
    assert "mean" in d
    assert "std" in d


def test_non_numeric_columns_ignored():
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"] * 20})
    issues = analyze(df)
    assert issues == []


def test_insufficient_rows_skipped():
    df = pd.DataFrame({"val": [1, 2, 3]})  # < 4 rows
    issues = analyze(df)
    assert issues == []


def test_constant_series_zscore_no_crash():
    df = pd.DataFrame({"val": [5] * 20})
    issues = analyze(df, method="zscore")
    assert issues == []


def test_get_outlier_mask_iqr():
    s = pd.Series(list(range(50)) + [500])
    mask = get_outlier_mask(s, method="iqr")
    assert mask.sum() == 1
    assert mask.iloc[-1]


def test_get_outlier_mask_zscore():
    s = pd.Series(list(range(50)) + [500])
    mask = get_outlier_mask(s, method="zscore")
    assert mask.sum() >= 1


def test_multiple_numeric_columns():
    df = pd.DataFrame({
        "a": list(range(50)) + [500],
        "b": list(range(50)) + [600],
    })
    issues = analyze(df)
    assert len(issues) == 2
    cols = {i.column for i in issues}
    assert cols == {"a", "b"}
