from __future__ import annotations

import numpy as np
import pandas as pd
from dateutil.parser import ParserError
from dateutil.parser import parse as parse_date

_BOOL_MAP: dict[str, bool] = {
    "yes": True, "no": False,
    "y": True,   "n": False,
    "1": True,   "0": False,
    "true": True, "false": False,
    "t": True,   "f": False,
    "on": True,  "off": False,
}
_DATE_HINTS = ("date", "time", "dt", "created", "updated", "modified", "timestamp", "at")


def fix_all(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = remove_duplicates(df)
    df = trim_whitespace(df)
    df = standardize_booleans(df)
    df = normalize_dates(df)
    df = fill_missing(df)
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()
    return df


def standardize_booleans(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().astype(str).str.lower()
        if len(sample) == 0:
            continue
        match_rate = sample.isin(_BOOL_MAP.keys()).mean()
        if match_rate >= 0.8:
            df[col] = df[col].astype(str).str.lower().map(_BOOL_MAP)
    return df


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object"]).columns:
        if not any(h in col.lower() for h in _DATE_HINTS):
            continue

        def _try_parse(v: object) -> object:
            if pd.isna(v):
                return v
            try:
                return parse_date(str(v)).strftime("%Y-%m-%d")
            except (ParserError, ValueError, OverflowError):
                return v

        df[col] = df[col].apply(_try_parse)
    return df


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            median = df[col].median()
            df[col] = df[col].fillna(median)
        elif df[col].dtype == object:
            mode = df[col].mode()
            if len(mode) > 0:
                df[col] = df[col].fillna(mode[0])

    return df
