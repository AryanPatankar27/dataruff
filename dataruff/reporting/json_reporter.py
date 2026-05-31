from __future__ import annotations

import json
from typing import Any

from dataruff.models import InvestigationReport


def report_to_dict(report: InvestigationReport) -> dict[str, Any]:
    return {
        "score": report.score.to_dict(),
        "row_count": report.row_count,
        "column_count": report.column_count,
        "issue_count": report.issue_count(),
        "issues": [
            {
                "type": issue.type,
                "severity": issue.severity,
                "count": issue.count,
                "column": issue.column,
                "details": issue.details,
            }
            for issue in report.issues
        ],
    }


def to_json(report: InvestigationReport, indent: int = 2) -> str:
    return json.dumps(report_to_dict(report), indent=indent, default=str)
