from __future__ import annotations

import pandas as pd
import pytest

from datadoctor.compare import compare
from datadoctor.models import ComparisonReport


@pytest.fixture
def old_df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
    })


@pytest.fixture
def new_df_row_added():
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["Alice", "Bob", "Charlie", "Diana"],
        "age": [25, 30, 35, 28],
    })


@pytest.fixture
def new_df_row_removed():
    return pd.DataFrame({
        "id": [1, 3],
        "name": ["Alice", "Charlie"],
        "age": [25, 35],
    })


@pytest.fixture
def new_df_col_added():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "score": [90, 85, 92],
    })


def test_returns_comparison_report():
    old2 = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
    new2 = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
    report = compare(old2, new2)
    assert isinstance(report, ComparisonReport)


def test_no_changes_identical_dfs(old_df):
    report = compare(old_df, old_df.copy())
    assert report.rows_added == 0
    assert report.rows_deleted == 0
    assert report.columns_added == []
    assert report.columns_removed == []
    assert report.type_changes == {}


def test_row_added(old_df, new_df_row_added):
    report = compare(old_df, new_df_row_added)
    assert report.rows_added == 1
    assert report.rows_deleted == 0


def test_row_removed(old_df, new_df_row_removed):
    report = compare(old_df, new_df_row_removed)
    assert report.rows_deleted == 1


def test_column_added(old_df, new_df_col_added):
    report = compare(old_df, new_df_col_added)
    assert "score" in report.columns_added


def test_column_removed(old_df):
    new_df = old_df.drop(columns=["age"])
    report = compare(old_df, new_df)
    assert "age" in report.columns_removed


def test_type_change_detected():
    old_df = pd.DataFrame({"val": [1, 2, 3]})
    new_df = pd.DataFrame({"val": ["1", "2", "3"]})
    report = compare(old_df, new_df)
    assert "val" in report.type_changes


def test_value_changes_sum():
    old_df = pd.DataFrame({"id": [1, 2, 3], "val": [10, 20, 30]})
    new_df = pd.DataFrame({"id": [1, 2, 4], "val": [10, 20, 40]})
    report = compare(old_df, new_df)
    assert report.value_changes == report.rows_added + report.rows_deleted


def test_accepts_csv_paths(tmp_path):
    old_df = pd.DataFrame({"id": [1, 2], "val": ["a", "b"]})
    new_df = pd.DataFrame({"id": [1, 2, 3], "val": ["a", "b", "c"]})
    old_path = tmp_path / "old.csv"
    new_path = tmp_path / "new.csv"
    old_df.to_csv(old_path, index=False)
    new_df.to_csv(new_path, index=False)
    report = compare(str(old_path), str(new_path))
    assert isinstance(report, ComparisonReport)
    assert report.rows_added == 1
