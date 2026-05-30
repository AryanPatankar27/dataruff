from __future__ import annotations

from typing import Union
from pathlib import Path

import pandas as pd

from datadoctor.investigate import investigate
from datadoctor.models import InvestigationReport
from datadoctor.reporting.terminal import print_audit_report


def audit(
    source: Union[str, Path, pd.DataFrame],
    schema: dict | None = None,
) -> InvestigationReport:
    report = investigate(source, schema=schema)
    print_audit_report(report)
    return report
