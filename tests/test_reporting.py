"""Tests for the reporting layer — both terminal and JSON."""
from __future__ import annotations

import json
from unittest.mock import patch

import pandas as pd
import pytest

from datadoctor.models import (
    DriftReport,
    InvestigationReport,
    Issue,
    PIIReport,
    ScoreBreakdown,
)
from datadoctor.reporting.json_reporter import report_to_dict, to_json
from datadoctor.reporting.terminal import (
    _plain_audit,
    print_audit_report,
    print_drift_report,
    print_pii_report,
)


def _make_report(issues=None, overall=85) -> InvestigationReport:
    score = ScoreBreakdown(
        overall=overall,
        completeness=90.0,
        validity=85.0,
        consistency=80.0,
        uniqueness=88.0,
        schema_compliance=100.0,
    )
    return InvestigationReport(
        row_count=100,
        column_count=5,
        issues=issues or [],
        score=score,
    )


# ── JSON reporter ─────────────────────────────────────────────────────────────

def test_report_to_dict_structure():
    report = _make_report()
    d = report_to_dict(report)
    assert "score" in d
    assert "issues" in d
    assert "row_count" in d
    assert "column_count" in d
    assert "issue_count" in d


def test_to_json_is_valid_json():
    report = _make_report()
    js = to_json(report)
    data = json.loads(js)
    assert data["score"]["overall"] == 85


def test_to_json_issues_serialized():
    issues = [
        Issue(type="duplicate_rows", severity="high", count=5),
        Issue(type="null_values", severity="medium", count=2, column="age"),
    ]
    report = _make_report(issues=issues)
    data = json.loads(to_json(report))
    assert len(data["issues"]) == 2
    assert data["issues"][0]["type"] == "duplicate_rows"
    assert data["issues"][1]["column"] == "age"


# ── terminal reporter — plain path ────────────────────────────────────────────

def test_plain_audit_prints_score(capsys):
    report = _make_report()
    _plain_audit(report)
    captured = capsys.readouterr()
    assert "85" in captured.out


def test_plain_audit_prints_no_issues_message(capsys):
    report = _make_report(issues=[])
    _plain_audit(report)
    captured = capsys.readouterr()
    assert "No issues" in captured.out or "clean" in captured.out.lower()


def test_plain_audit_prints_issue_details(capsys):
    issues = [Issue(type="duplicate_rows", severity="high", count=10)]
    report = _make_report(issues=issues)
    _plain_audit(report)
    captured = capsys.readouterr()
    assert "duplicate" in captured.out
    assert "10" in captured.out


def test_plain_audit_prints_column_note(capsys):
    issues = [Issue(type="null_values", severity="medium", count=3, column="age")]
    report = _make_report(issues=issues)
    _plain_audit(report)
    captured = capsys.readouterr()
    assert "age" in captured.out


def test_plain_audit_prints_row_count(capsys):
    report = _make_report()
    _plain_audit(report)
    captured = capsys.readouterr()
    assert "100" in captured.out  # row_count


# Force the plain path even if rich is installed
def test_print_audit_report_plain_fallback(capsys):
    report = _make_report()
    with patch("datadoctor.reporting.terminal._RICH", False):
        print_audit_report(report)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_print_audit_report_rich_path(capsys):
    report = _make_report()
    with patch("datadoctor.reporting.terminal._RICH", True):
        try:
            print_audit_report(report)
        except ImportError:
            pytest.skip("rich not installed")
    captured = capsys.readouterr()
    assert len(captured.out) > 0


# ── PII report ────────────────────────────────────────────────────────────────

def test_print_pii_report_no_pii(capsys):
    report = PIIReport(columns_with_pii={})
    print_pii_report(report)
    captured = capsys.readouterr()
    assert "No PII" in captured.out


def test_print_pii_report_with_pii(capsys):
    report = PIIReport(columns_with_pii={"email": ["email"], "phone": ["phone"]})
    print_pii_report(report)
    captured = capsys.readouterr()
    assert "email" in captured.out
    assert "phone" in captured.out


# ── Drift report ──────────────────────────────────────────────────────────────

def test_print_drift_report_no_drift(capsys):
    report = DriftReport(
        distribution_drift={},
        category_drift={},
        missing_value_drift={},
        drifted_columns=[],
    )
    print_drift_report(report)
    captured = capsys.readouterr()
    assert "No significant drift" in captured.out


def test_print_drift_report_with_drift(capsys):
    report = DriftReport(
        distribution_drift={"age": 0.45},
        category_drift={"dept": {"Eng": {"old_pct": 50.0, "new_pct": 80.0}}},
        missing_value_drift={"age": 15.0},
        drifted_columns=["age", "dept"],
    )
    print_drift_report(report)
    captured = capsys.readouterr()
    assert "age" in captured.out
    assert "dept" in captured.out
