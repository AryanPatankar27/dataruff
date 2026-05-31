from __future__ import annotations

import pandas as pd
import pytest

from dataruff.investigate import investigate
from dataruff.models import InvestigationReport, ScoreBreakdown


def test_returns_investigation_report(clean_df):
    report = investigate(clean_df)
    assert isinstance(report, InvestigationReport)


def test_row_and_column_count(clean_df):
    report = investigate(clean_df)
    assert report.row_count == len(clean_df)
    assert report.column_count == len(clean_df.columns)


def test_score_is_score_breakdown(clean_df):
    report = investigate(clean_df)
    assert isinstance(report.score, ScoreBreakdown)
    assert 0 <= report.score.overall <= 100


def test_clean_df_has_no_duplicate_issues(clean_df):
    report = investigate(clean_df)
    dups = report.issues_by_type("duplicate_rows")
    assert dups == []


def test_dirty_df_detects_duplicates(dirty_df):
    report = investigate(dirty_df)
    dups = report.issues_by_type("duplicate_rows")
    assert len(dups) == 1
    assert dups[0].count >= 1


def test_dirty_df_detects_nulls(dirty_df):
    report = investigate(dirty_df)
    nulls = report.issues_by_type("null_values")
    assert len(nulls) > 0


def test_dirty_df_detects_invalid_email(dirty_df):
    report = investigate(dirty_df)
    email_issues = report.issues_by_type("invalid_email")
    assert len(email_issues) == 1
    assert email_issues[0].count >= 2  # "not-an-email" and "bad" (+ duplicate)


def test_dirty_df_detects_outlier(dirty_df):
    report = investigate(dirty_df)
    outlier_issues = report.issues_by_type("outlier")
    assert len(outlier_issues) >= 1


def test_issue_count_method(dirty_df):
    report = investigate(dirty_df)
    assert report.issue_count() == len(report.issues)


def test_issues_by_severity(dirty_df):
    report = investigate(dirty_df)
    high = report.issues_by_severity("high")
    medium = report.issues_by_severity("medium")
    assert all(i.severity == "high" for i in high)
    assert all(i.severity == "medium" for i in medium)


def test_schema_passed_to_scoring(clean_df):
    schema = {"email": "email"}
    report = investigate(clean_df, schema=schema)
    assert report.score.schema_compliance == 100.0


def test_schema_violation_lowers_score(dirty_df):
    schema = {"email": "email"}
    report = investigate(dirty_df, schema=schema)
    assert report.score.schema_compliance < 100.0


def test_accepts_csv_path(sample_csv):
    report = investigate(sample_csv)
    assert isinstance(report, InvestigationReport)
