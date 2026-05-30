from __future__ import annotations

from typing import Union
from pathlib import Path

import pandas as pd

from datadoctor.analyzers import (
    duplicate,
    format_analyzer,
    null_analyzer,
    outlier,
    type_analyzer,
)
from datadoctor.loader import load
from datadoctor.models import InvestigationReport
from datadoctor.scoring.engine import compute as _compute_score


def investigate(
    source: Union[str, Path, pd.DataFrame],
    schema: dict | None = None,
) -> InvestigationReport:
    df = load(source)

    issues = []
    issues.extend(duplicate.analyze(df))
    issues.extend(null_analyzer.analyze(df))
    issues.extend(type_analyzer.analyze(df))
    issues.extend(format_analyzer.analyze(df))
    issues.extend(outlier.analyze(df))

    score = _compute_score(df, issues, schema)

    return InvestigationReport(
        row_count=len(df),
        column_count=len(df.columns),
        issues=issues,
        score=score,
    )
