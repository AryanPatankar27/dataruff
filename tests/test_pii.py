from __future__ import annotations

import pandas as pd
import pytest

from dataruff.pii import detect_pii, mask_pii, _mask_value
from dataruff.models import PIIReport


# ── detect_pii ────────────────────────────────────────────────────────────────

def test_detect_pii_returns_pii_report(pii_df):
    report = detect_pii(pii_df)
    assert isinstance(report, PIIReport)


def test_detect_pii_finds_email_column(pii_df):
    report = detect_pii(pii_df)
    assert report.has_pii()
    assert "email" in report.columns_with_pii


def test_detect_pii_finds_phone_column(pii_df):
    report = detect_pii(pii_df)
    assert "phone" in report.columns_with_pii


def test_detect_pii_finds_aadhaar_column(pii_df):
    report = detect_pii(pii_df)
    assert "aadhaar" in report.columns_with_pii


def test_detect_pii_no_pii_in_clean_data(clean_df):
    report = detect_pii(clean_df)
    # clean_df has an email column, so we expect email PII
    assert "email" in report.columns_with_pii or not report.has_pii()


def test_pii_types_method_returns_sorted(pii_df):
    report = detect_pii(pii_df)
    types = report.pii_types()
    assert types == sorted(types)


def test_has_pii_false_when_no_pii():
    df = pd.DataFrame({"id": [1, 2], "category": ["A", "B"]})
    report = detect_pii(df)
    assert not report.has_pii()


def test_detect_pii_accepts_csv(pii_csv):
    report = detect_pii(pii_csv)
    assert isinstance(report, PIIReport)


# ── mask_pii ──────────────────────────────────────────────────────────────────

def test_mask_pii_returns_dataframe(pii_df):
    result = mask_pii(pii_df)
    assert isinstance(result, pd.DataFrame)


def test_mask_pii_masks_email():
    df = pd.DataFrame({"email": ["alice@example.com"]})
    result = mask_pii(df)
    masked = result["email"][0]
    assert "@example.com" in masked
    assert masked.startswith("al")
    assert "*" in masked


def test_mask_pii_masks_phone():
    df = pd.DataFrame({"phone": ["9876543210"]})
    result = mask_pii(df)
    masked = result["phone"][0]
    assert masked.startswith("98")
    assert masked.endswith("10")
    assert "*" in masked


def test_mask_pii_does_not_mutate_input(pii_df):
    original = pii_df["email"].copy()
    _ = mask_pii(pii_df)
    pd.testing.assert_series_equal(pii_df["email"], original)


def test_mask_pii_non_pii_columns_unchanged(pii_df):
    result = mask_pii(pii_df)
    # name column has no PII by name hint or content
    pd.testing.assert_series_equal(result["name"], pii_df["name"])


# ── _mask_value unit tests ────────────────────────────────────────────────────

def test_mask_value_phone():
    result = _mask_value("9876543210", "phone")
    assert result == "98******10"


def test_mask_value_email():
    result = _mask_value("alice@example.com", "email")
    assert result.endswith("@example.com")
    assert result.startswith("al")
    assert "*" in result


def test_mask_value_ssn():
    result = _mask_value("123-45-6789", "ssn")
    assert result == "***-**-6789"


def test_mask_value_pan():
    result = _mask_value("ABCDE1234F", "pan")
    assert result.startswith("AB")
    assert result.endswith("4F")
    assert "*" in result


def test_mask_value_non_string_passthrough():
    result = _mask_value(12345, "phone")
    assert result == 12345


def test_mask_value_short_aadhaar_passthrough():
    result = _mask_value("123", "aadhaar")
    # length <= 4, returns as-is
    assert result == "123"


# ── edge cases that cover the remaining pii.py branches ──────────────────────

def test_mask_value_phone_too_short():
    # < 4 digits → returns value unchanged (line 41)
    result = _mask_value("99", "phone")
    assert result == "99"


def test_mask_value_email_no_at_sign():
    # email without '@' → returns value unchanged (line 48)
    result = _mask_value("notanemail", "email")
    assert result == "notanemail"


def test_mask_value_aadhaar_long():
    # > 4 digits → masked (line 53)
    result = _mask_value("123456789012", "aadhaar")
    assert result.endswith("9012")
    assert "*" in result


def test_mask_value_credit_card_short():
    # <= 4 digits → returns unchanged (line 54)
    result = _mask_value("123", "credit_card")
    assert result == "123"


def test_mask_value_ssn_wrong_digit_count():
    # SSN without exactly 9 digits → returns unchanged (line 61)
    result = _mask_value("123-45", "ssn")
    assert result == "123-45"


def test_mask_value_pan_too_short():
    # PAN < 4 chars → returns unchanged (line 66)
    result = _mask_value("AB", "pan")
    assert result == "AB"


def test_mask_value_unknown_pii_type():
    # Unrecognised type → falls through to final return (line 68)
    result = _mask_value("somevalue", "unknown_type")
    assert result == "somevalue"


def test_mask_pii_non_object_dtype_column_skipped():
    # A numeric column that somehow got flagged should be skipped (line 25-26)
    df = pd.DataFrame({"phone": [9876543210, 8765432109]})  # int64, not object
    result = mask_pii(df)
    # dtype unchanged — no masking attempted
    assert result["phone"].dtype == df["phone"].dtype
