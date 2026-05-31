from __future__ import annotations

import pandas as pd
import pytest

from dataruff.validate import validate


def test_all_valid_emails_passes(clean_df):
    schema = {"email": "email"}
    result = validate(clean_df, schema)
    assert result["passed"] is True
    assert result["violations"] == []
    assert result["schema_compliance_score"] == 100.0


def test_invalid_emails_violation(dirty_df):
    schema = {"email": "email"}
    result = validate(dirty_df, schema)
    assert result["passed"] is False
    assert len(result["violations"]) >= 1
    v = result["violations"][0]
    assert v["column"] == "email"
    assert v["violation_count"] >= 1


def test_age_range_valid(clean_df):
    schema = {"age": "0-120"}
    result = validate(clean_df, schema)
    assert result["passed"] is True


def test_age_range_violation():
    df = pd.DataFrame({"age": [25, 150, -1, 30]})
    schema = {"age": "0-120"}
    result = validate(df, schema)
    assert result["passed"] is False
    v = result["violations"][0]
    assert v["column"] == "age"
    assert v["violation_count"] == 2


def test_not_null_rule_passes(clean_df):
    schema = {"name": "not_null"}
    result = validate(clean_df, schema)
    assert result["passed"] is True


def test_not_null_rule_violation(dirty_df):
    schema = {"name": "not_null"}
    result = validate(dirty_df, schema)
    assert result["passed"] is False


def test_unique_rule_passes(clean_df):
    schema = {"id": "unique"}
    result = validate(clean_df, schema)
    assert result["passed"] is True


def test_unique_rule_violation():
    df = pd.DataFrame({"id": [1, 2, 2, 3]})
    schema = {"id": "unique"}
    result = validate(df, schema)
    assert result["passed"] is False


def test_positive_rule_passes():
    df = pd.DataFrame({"price": [1.0, 5.0, 10.0]})
    schema = {"price": "positive"}
    result = validate(df, schema)
    assert result["passed"] is True


def test_positive_rule_violation():
    df = pd.DataFrame({"price": [1.0, -5.0, 0.0]})
    schema = {"price": "positive"}
    result = validate(df, schema)
    assert result["passed"] is False
    assert result["violations"][0]["violation_count"] == 2


def test_missing_column_reported():
    df = pd.DataFrame({"a": [1, 2]})
    schema = {"nonexistent": "not_null"}
    result = validate(df, schema)
    assert result["passed"] is False
    v = result["violations"][0]
    assert v["error"] == "column_not_found"


def test_regex_rule_passes():
    df = pd.DataFrame({"code": ["ABC123", "DEF456"]})
    schema = {"code": "regex:[A-Z]{3}[0-9]{3}"}
    result = validate(df, schema)
    assert result["passed"] is True


def test_regex_rule_violation():
    df = pd.DataFrame({"code": ["ABC123", "invalid"]})
    schema = {"code": "regex:[A-Z]{3}[0-9]{3}"}
    result = validate(df, schema)
    assert result["passed"] is False
    assert result["violations"][0]["violation_count"] == 1


def test_multiple_schema_rules(clean_df):
    schema = {"email": "email", "age": "0-120", "id": "unique"}
    result = validate(clean_df, schema)
    assert result["passed"] is True


def test_compliance_score_between_0_and_100(dirty_df):
    schema = {"email": "email"}
    result = validate(dirty_df, schema)
    assert 0 <= result["schema_compliance_score"] <= 100
