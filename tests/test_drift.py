from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from dataruff.drift import detect_drift
from dataruff.models import DriftReport


@pytest.fixture
def base_df():
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "age": rng.integers(20, 60, 100).astype(float),
        "salary": rng.normal(50000, 10000, 100),
        "dept": rng.choice(["Engineering", "Sales", "HR"], 100).tolist(),
    })


@pytest.fixture
def same_df(base_df):
    return base_df.copy()


@pytest.fixture
def shifted_df(base_df):
    df = base_df.copy()
    df["salary"] = df["salary"] + 30000  # massive shift
    return df


@pytest.fixture
def category_shifted_df(base_df):
    df = base_df.copy()
    df["dept"] = "Engineering"  # all Engineering now
    return df


def test_returns_drift_report(base_df, same_df):
    report = detect_drift(base_df, same_df)
    assert isinstance(report, DriftReport)


def test_no_drift_on_identical_dfs(base_df, same_df):
    report = detect_drift(base_df, same_df)
    assert not report.has_drift()


def test_numeric_drift_detected(base_df, shifted_df):
    report = detect_drift(base_df, shifted_df)
    assert "salary" in report.drifted_columns


def test_category_drift_detected(base_df, category_shifted_df):
    report = detect_drift(base_df, category_shifted_df)
    assert "dept" in report.drifted_columns


def test_distribution_drift_has_scores(base_df, shifted_df):
    report = detect_drift(base_df, shifted_df)
    assert "salary" in report.distribution_drift
    assert 0 <= report.distribution_drift["salary"] <= 1


def test_missing_value_drift_tracked(base_df):
    new_df = base_df.copy()
    new_df.loc[:30, "age"] = np.nan  # introduce 30% missing values
    report = detect_drift(base_df, new_df)
    assert "age" in report.missing_value_drift
    assert report.missing_value_drift["age"] > 0


def test_category_drift_details_structure(base_df, category_shifted_df):
    report = detect_drift(base_df, category_shifted_df)
    for col, changes in report.category_drift.items():
        for cat, info in changes.items():
            assert "old_pct" in info
            assert "new_pct" in info


def test_has_drift_false_when_no_drift(base_df, same_df):
    report = detect_drift(base_df, same_df)
    assert not report.has_drift()


def test_accepts_csv_paths(tmp_path, base_df, shifted_df):
    old_path = tmp_path / "old.csv"
    new_path = tmp_path / "new.csv"
    base_df.to_csv(old_path, index=False)
    shifted_df.to_csv(new_path, index=False)
    report = detect_drift(str(old_path), str(new_path))
    assert isinstance(report, DriftReport)
