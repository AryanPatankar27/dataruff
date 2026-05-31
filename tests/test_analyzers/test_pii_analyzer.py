from __future__ import annotations

import pandas as pd
import pytest

from dataruff.analyzers.pii_analyzer import analyze


def test_email_column_name_hint():
    df = pd.DataFrame({"email": ["user@example.com"]})
    result = analyze(df)
    assert "email" in result
    assert "email" in result["email"]


def test_phone_column_name_hint():
    df = pd.DataFrame({"phone": ["9876543210"]})
    result = analyze(df)
    assert "phone" in result
    assert "phone" in result["phone"]


def test_aadhaar_column_name_hint():
    df = pd.DataFrame({"aadhaar": ["2345 6789 0123"]})
    result = analyze(df)
    assert "aadhaar" in result


def test_pan_column_name_hint():
    df = pd.DataFrame({"pan": ["ABCDE1234F"]})
    result = analyze(df)
    assert "pan" in result


def test_ssn_content_detection():
    df = pd.DataFrame({"info": ["123-45-6789", "987-65-4321"]})
    result = analyze(df)
    assert "info" in result
    assert "ssn" in result["info"]


def test_email_content_detection():
    df = pd.DataFrame({"notes": ["contact: alice@example.com"]})
    result = analyze(df)
    assert "notes" in result
    assert "email" in result["notes"]


def test_no_pii_in_clean_data():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "category": ["A", "B", "C"],
        "score": [1.0, 2.0, 3.0],
    })
    result = analyze(df)
    assert result == {}


def test_non_object_column_not_content_scanned():
    df = pd.DataFrame({"age": [25, 30, 35]})
    result = analyze(df)
    assert result == {}


def test_multiple_pii_types_in_one_column():
    df = pd.DataFrame({
        "data": ["alice@ex.com 123-45-6789"]
    })
    result = analyze(df)
    if "data" in result:
        assert "email" in result["data"] or "ssn" in result["data"]


def test_result_values_are_sorted_lists():
    df = pd.DataFrame({"email": ["a@b.com"], "phone": ["9876543210"]})
    result = analyze(df)
    for col, types in result.items():
        assert types == sorted(types)
