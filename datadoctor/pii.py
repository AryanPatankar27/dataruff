from __future__ import annotations

import re
from pathlib import Path
from typing import Union

import pandas as pd

from datadoctor._compat import is_str_col
from datadoctor.analyzers.pii_analyzer import analyze as _pii_analyze
from datadoctor.loader import load
from datadoctor.models import PIIReport


def detect_pii(source: Union[str, Path, pd.DataFrame]) -> PIIReport:
    df = load(source)
    columns_with_pii = _pii_analyze(df)
    return PIIReport(columns_with_pii=columns_with_pii)


def mask_pii(source: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
    df = load(source)
    pii_info = _pii_analyze(df)

    for col, pii_types in pii_info.items():
        if not is_str_col(df[col]):
            continue
        for pii_type in pii_types:
            df[col] = df[col].apply(lambda v, pt=pii_type: _mask_value(v, pt))

    return df


def _mask_value(value: object, pii_type: str) -> object:
    if not isinstance(value, str):
        return value

    if pii_type == "phone":
        digits = re.sub(r"\D", "", value)
        if len(digits) >= 4:
            return digits[:2] + "*" * (len(digits) - 4) + digits[-2:]
        return value

    if pii_type == "email":
        if "@" in value:
            local, domain = value.split("@", 1)
            masked = local[:2] + "*" * max(1, len(local) - 2)
            return f"{masked}@{domain}"
        return value

    if pii_type in ("aadhaar", "credit_card"):
        digits = re.sub(r"\D", "", value)
        if len(digits) > 4:
            return "*" * (len(digits) - 4) + digits[-4:]
        return value

    if pii_type == "ssn":
        # Format: XXX-XX-1234
        digits = re.sub(r"\D", "", value)
        if len(digits) == 9:
            return f"***-**-{digits[-4:]}"
        return value

    if pii_type == "pan":
        if len(value) >= 4:
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        return value

    return value
