from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from datadoctor.investigate import investigate
from datadoctor.models import ScoreBreakdown


def score(
    source: Union[str, Path, pd.DataFrame],
    schema: dict | None = None,
) -> ScoreBreakdown:
    report = investigate(source, schema=schema)
    return report.score
