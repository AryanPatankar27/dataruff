from __future__ import annotations

from typing import Union
from pathlib import Path

import pandas as pd

from dataruff.investigate import investigate
from dataruff.models import InvestigationReport
from dataruff.reporting.terminal import print_audit_report


def audit(
    source: Union[str, Path, pd.DataFrame],
    schema: dict | None = None,
) -> InvestigationReport:
    report = investigate(source, schema=schema)
    print_audit_report(report)
    return report
