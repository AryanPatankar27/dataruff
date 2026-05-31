from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from dataruff.fixing.engine import fix_all
from dataruff.loader import load


def fix(source: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
    df = load(source)
    return fix_all(df)
