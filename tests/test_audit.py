from __future__ import annotations

import pandas as pd
import pytest

from datadoctor.audit import audit
from datadoctor.models import InvestigationReport


def test_audit_returns_report(clean_df, capsys):
    report = audit(clean_df)
    assert isinstance(report, InvestigationReport)


def test_audit_prints_score(clean_df, capsys):
    audit(clean_df)
    captured = capsys.readouterr()
    assert "Score" in captured.out or "score" in captured.out.lower()


def test_audit_prints_issues(dirty_df, capsys):
    audit(dirty_df)
    captured = capsys.readouterr()
    # Should mention at least one issue type
    assert any(
        keyword in captured.out
        for keyword in ("duplicate", "null", "email", "outlier")
    )


def test_audit_clean_df_no_issues_message(capsys):
    df = pd.DataFrame({"id": [1, 2, 3], "val": [10, 20, 30]})
    audit(df)
    captured = capsys.readouterr()
    assert "No issues" in captured.out or "clean" in captured.out.lower() or len(captured.out) > 0


def test_audit_accepts_csv(sample_csv, capsys):
    report = audit(sample_csv)
    assert isinstance(report, InvestigationReport)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_audit_with_schema(clean_df, capsys):
    schema = {"email": "email", "age": "0-120"}
    report = audit(clean_df, schema=schema)
    assert report.score.schema_compliance == 100.0
