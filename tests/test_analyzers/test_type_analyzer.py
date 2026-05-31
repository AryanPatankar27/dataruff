from __future__ import annotations

import pandas as pd
import pytest

from datadoctor.analyzers.type_analyzer import analyze


# ── mixed-type detection (lines 25-35) ───────────────────────────────────────

def test_mixed_types_int_and_str_detected():
    # Pandas object column containing actual Python ints and strs
    df = pd.DataFrame({"mixed": pd.array([1, "two", 3, "four"], dtype=object)})
    issues = analyze(df)
    mixed = [i for i in issues if i.type == "mixed_types"]
    assert len(mixed) == 1
    assert mixed[0].column == "mixed"
    assert mixed[0].severity == "medium"


def test_mixed_types_details_list_types():
    df = pd.DataFrame({"col": pd.array([1, "hello"], dtype=object)})
    issues = analyze(df)
    mixed = [i for i in issues if i.type == "mixed_types"]
    types_found = mixed[0].details["types_found"]
    assert "int" in types_found or "str" in types_found


def test_mixed_types_skips_numeric_as_string_check():
    # When mixed types are found, the numeric-as-string branch should be skipped
    df = pd.DataFrame({"col": pd.array([1, "two"], dtype=object)})
    issues = analyze(df)
    numeric_issues = [i for i in issues if i.type == "numeric_as_string"]
    assert len(numeric_issues) == 0


def test_str_and_bytes_not_flagged_as_mixed():
    # str + bytes is an acceptable mix — should NOT trigger mixed_types
    df = pd.DataFrame({"col": pd.array(["hello", b"world"], dtype=object)})
    issues = analyze(df)
    mixed = [i for i in issues if i.type == "mixed_types"]
    assert len(mixed) == 0


def test_uniform_str_column_not_flagged():
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
    issues = analyze(df)
    mixed = [i for i in issues if i.type == "mixed_types"]
    assert len(mixed) == 0


# ── numeric-as-string detection (lines 38-48) ─────────────────────────────────

def test_numeric_as_string_detected():
    df = pd.DataFrame({"amount": ["100", "200", "300", "400"]})
    issues = analyze(df)
    num_issues = [i for i in issues if i.type == "numeric_as_string"]
    assert len(num_issues) == 1
    assert num_issues[0].column == "amount"
    assert num_issues[0].severity == "low"


def test_numeric_as_string_with_commas():
    df = pd.DataFrame({"amount": ["1,000", "2,500", "3,750"]})
    issues = analyze(df)
    num_issues = [i for i in issues if i.type == "numeric_as_string"]
    assert len(num_issues) == 1


def test_numeric_as_string_details_has_suggestion():
    df = pd.DataFrame({"val": ["1", "2", "3"]})
    issues = analyze(df)
    num_issues = [i for i in issues if i.type == "numeric_as_string"]
    assert "suggestion" in num_issues[0].details


def test_mixed_str_and_text_not_flagged_as_numeric():
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
    issues = analyze(df)
    num_issues = [i for i in issues if i.type == "numeric_as_string"]
    assert len(num_issues) == 0


# ── general edge cases ────────────────────────────────────────────────────────

def test_non_object_dtype_skipped():
    df = pd.DataFrame({"age": [25, 30, 35]})
    issues = analyze(df)
    assert issues == []


def test_empty_column_after_dropna_skipped():
    df = pd.DataFrame({"col": [None, None, None]})
    # dtype becomes float64 for all-None, so object-check skips it
    issues = analyze(df)
    assert issues == []


def test_empty_dataframe():
    df = pd.DataFrame()
    assert analyze(df) == []
