from __future__ import annotations

import pandas as pd
import pytest

from dataruff.analyzers.format_analyzer import analyze


def test_valid_emails_no_issues():
    df = pd.DataFrame({"email": ["alice@ex.com", "bob@test.org", "c@d.io"]})
    issues = analyze(df)
    assert all(i.type != "invalid_email" for i in issues)


def test_invalid_emails_detected():
    df = pd.DataFrame({"email": ["alice@ex.com", "not-an-email", "bad"]})
    issues = analyze(df)
    email_issues = [i for i in issues if i.type == "invalid_email"]
    assert len(email_issues) == 1
    assert email_issues[0].count == 2
    assert email_issues[0].column == "email"


def test_invalid_email_examples_in_details():
    df = pd.DataFrame({"email": ["good@test.com", "bad1", "bad2", "bad3", "bad4"]})
    issues = analyze(df)
    email_issues = [i for i in issues if i.type == "invalid_email"]
    assert "examples" in email_issues[0].details
    assert len(email_issues[0].details["examples"]) <= 3


def test_date_column_valid_dates_no_issues():
    df = pd.DataFrame({"created_date": ["2024-01-01", "2024-02-15", "2024-03-20"]})
    issues = analyze(df)
    assert all(i.type != "invalid_date" for i in issues)


def test_inconsistent_date_formats_detected():
    df = pd.DataFrame({
        "created_date": ["2024-01-01", "01/15/2024", "2024-03-20"]
    })
    issues = analyze(df)
    inconsistent = [i for i in issues if i.type == "inconsistent_date_format"]
    assert len(inconsistent) == 1
    assert len(inconsistent[0].details["formats_detected"]) > 1


def test_unparseable_dates_flagged():
    df = pd.DataFrame({"updated_at": ["2024-01-01", "not-a-date", "2024-03-20"]})
    issues = analyze(df)
    invalid = [i for i in issues if i.type == "invalid_date"]
    assert len(invalid) == 1
    assert invalid[0].count == 1


def test_non_date_non_email_column_skipped():
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
    issues = analyze(df)
    assert issues == []


def test_non_object_column_skipped():
    df = pd.DataFrame({"age": [25, 30, 35]})
    issues = analyze(df)
    assert issues == []


def test_email_column_name_variants():
    for col_name in ("user_email", "e-mail", "mail", "Email"):
        df = pd.DataFrame({col_name: ["bad", "also_bad"]})
        issues = analyze(df)
        assert any(i.type == "invalid_email" for i in issues), f"Failed for column name: {col_name}"
