from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from datadoctor.anomalies import find_anomalies


@pytest.fixture
def normal_df():
    return pd.DataFrame({"val": list(range(50))})


@pytest.fixture
def outlier_df():
    return pd.DataFrame({"val": list(range(50)) + [500]})


def test_returns_dict(normal_df):
    result = find_anomalies(normal_df)
    assert isinstance(result, dict)


def test_required_keys_present(outlier_df):
    result = find_anomalies(outlier_df)
    assert "total_anomalous_records" in result
    assert "method" in result
    assert "by_column" in result
    assert "anomalous_indices" in result


def test_no_anomalies_clean_data(normal_df):
    result = find_anomalies(normal_df)
    assert result["total_anomalous_records"] == 0
    assert result["by_column"] == []


def test_extreme_outlier_detected(outlier_df):
    result = find_anomalies(outlier_df)
    assert result["total_anomalous_records"] >= 1


def test_iqr_method(outlier_df):
    result = find_anomalies(outlier_df, method="iqr")
    assert result["method"] == "iqr"
    assert result["total_anomalous_records"] >= 1


def test_zscore_method(outlier_df):
    result = find_anomalies(outlier_df, method="zscore")
    assert result["method"] == "zscore"
    assert result["total_anomalous_records"] >= 1


def test_invalid_method_raises():
    df = pd.DataFrame({"val": [1, 2, 3]})
    with pytest.raises(ValueError, match="Unknown method"):
        find_anomalies(df, method="badmethod")


def test_by_column_structure(outlier_df):
    result = find_anomalies(outlier_df)
    for item in result["by_column"]:
        assert "column" in item
        assert "count" in item
        assert "severity" in item
        assert "percentage" in item


def test_anomalous_indices_are_valid(outlier_df):
    result = find_anomalies(outlier_df)
    for idx in result["anomalous_indices"]:
        assert idx in outlier_df.index


def test_non_numeric_columns_excluded():
    df = pd.DataFrame({"name": ["Alice"] * 50 + ["OUTLIER"], "val": list(range(51))})
    result = find_anomalies(df)
    col_names = [item["column"] for item in result["by_column"]]
    assert "name" not in col_names


def test_multiple_columns(outlier_df):
    df = pd.DataFrame({
        "a": list(range(50)) + [500],
        "b": list(range(50)) + [500],
    })
    result = find_anomalies(df)
    col_names = [item["column"] for item in result["by_column"]]
    assert "a" in col_names
    assert "b" in col_names


def test_accepts_csv(sample_csv):
    result = find_anomalies(sample_csv)
    assert isinstance(result, dict)
