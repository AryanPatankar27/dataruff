from __future__ import annotations

import pandas as pd
import pytest

from dataruff.fix import fix
from dataruff.fixing.engine import (
    fill_missing,
    normalize_dates,
    remove_duplicates,
    standardize_booleans,
    trim_whitespace,
    fix_all,
)


# ── fix() public API ──────────────────────────────────────────────────────────

def test_fix_returns_dataframe(dirty_df):
    result = fix(dirty_df)
    assert isinstance(result, pd.DataFrame)


def test_fix_removes_duplicates(dirty_df):
    result = fix(dirty_df)
    assert result.duplicated().sum() == 0


def test_fix_does_not_mutate_input(dirty_df):
    original_len = len(dirty_df)
    _ = fix(dirty_df)
    assert len(dirty_df) == original_len


def test_fix_accepts_csv(sample_csv):
    result = fix(sample_csv)
    assert isinstance(result, pd.DataFrame)
    assert result.duplicated().sum() == 0


# ── remove_duplicates ─────────────────────────────────────────────────────────

def test_remove_duplicates():
    df = pd.DataFrame({"a": [1, 2, 2, 3]})
    result = remove_duplicates(df)
    assert len(result) == 3
    assert result.duplicated().sum() == 0


def test_remove_duplicates_resets_index():
    df = pd.DataFrame({"a": [1, 1, 2]})
    result = remove_duplicates(df)
    assert list(result.index) == list(range(len(result)))


# ── trim_whitespace ───────────────────────────────────────────────────────────

def test_trim_whitespace_strips_strings():
    df = pd.DataFrame({"name": ["  Alice  ", " Bob", "Charlie "]})
    result = trim_whitespace(df)
    assert list(result["name"]) == ["Alice", "Bob", "Charlie"]


def test_trim_whitespace_ignores_numeric():
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})
    result = trim_whitespace(df)
    assert list(result["val"]) == [1.0, 2.0, 3.0]


def test_trim_whitespace_preserves_nulls():
    df = pd.DataFrame({"name": [None, " Bob "]})
    result = trim_whitespace(df)
    assert result["name"][0] is None or pd.isna(result["name"][0])
    assert result["name"][1] == "Bob"


# ── standardize_booleans ──────────────────────────────────────────────────────

def test_standardize_booleans_converts_yes_no():
    df = pd.DataFrame({"flag": ["yes", "no", "yes", "no"]})
    result = standardize_booleans(df)
    assert set(result["flag"].dropna().unique()) <= {True, False}


def test_standardize_booleans_converts_true_false():
    df = pd.DataFrame({"active": ["true", "false", "TRUE", "FALSE"]})
    result = standardize_booleans(df)
    assert set(result["active"].dropna().unique()) <= {True, False}


def test_standardize_booleans_ignores_non_boolean():
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie", "Diana"]})
    result = standardize_booleans(df)
    assert list(result["name"]) == ["Alice", "Bob", "Charlie", "Diana"]


# ── normalize_dates ───────────────────────────────────────────────────────────

def test_normalize_dates_standardizes_format():
    df = pd.DataFrame({"created_date": ["01/15/2024", "2024-02-20", "March 3, 2024"]})
    result = normalize_dates(df)
    # All should become YYYY-MM-DD
    for val in result["created_date"].dropna():
        assert len(val) == 10
        assert val[4] == "-" and val[7] == "-"


def test_normalize_dates_preserves_nulls():
    df = pd.DataFrame({"updated_at": [None, "2024-01-01"]})
    result = normalize_dates(df)
    assert pd.isna(result["updated_at"][0])


def test_normalize_dates_ignores_non_date_columns():
    df = pd.DataFrame({"name": ["Alice", "Bob"]})
    result = normalize_dates(df)
    assert list(result["name"]) == ["Alice", "Bob"]


# ── fill_missing ──────────────────────────────────────────────────────────────

def test_fill_missing_numeric_with_median():
    df = pd.DataFrame({"val": [1.0, 2.0, None, 4.0, 5.0]})
    result = fill_missing(df)
    assert result["val"].isna().sum() == 0
    assert result["val"][2] == pytest.approx(3.0)  # median of [1,2,4,5]


def test_fill_missing_string_with_mode():
    df = pd.DataFrame({"cat": ["A", "A", None, "B"]})
    result = fill_missing(df)
    assert result["cat"].isna().sum() == 0
    assert result["cat"][2] == "A"  # mode


def test_fill_missing_no_nulls_unchanged():
    df = pd.DataFrame({"val": [1, 2, 3]})
    result = fill_missing(df)
    assert list(result["val"]) == [1, 2, 3]


# ── fix_all integration ───────────────────────────────────────────────────────

def test_fix_all_reduces_nulls(dirty_df):
    result = fix_all(dirty_df)
    assert result.isna().sum().sum() < dirty_df.isna().sum().sum()
