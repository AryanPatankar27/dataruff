from __future__ import annotations

import re

import pandas as pd
from dateutil.parser import ParserError
from dateutil.parser import parse as parse_date

from datadoctor._compat import is_str_col
from datadoctor.models import Issue

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_EMAIL_HINTS = ("email", "mail", "e-mail", "e_mail")
_DATE_HINTS = ("date", "time", "dt", "created", "updated", "modified", "timestamp")


def _is_email_col(name: str) -> bool:
    low = name.lower()
    return any(h in low for h in _EMAIL_HINTS)


def _is_date_col(name: str) -> bool:
    low = name.lower()
    return any(h in low for h in _DATE_HINTS)


def analyze(df: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []

    for col in df.columns:
        if not is_str_col(df[col]):
            continue

        series = df[col].dropna().astype(str)
        if len(series) == 0:
            continue

        if _is_email_col(col):
            invalid = series[~series.str.match(_EMAIL_RE)]
            if len(invalid) > 0:
                issues.append(
                    Issue(
                        type="invalid_email",
                        severity="medium",
                        count=len(invalid),
                        column=col,
                        details={"examples": invalid.head(3).tolist()},
                    )
                )

        if _is_date_col(col):
            formats_seen: set[str] = set()
            parse_errors = 0

            for val in series:
                try:
                    parse_date(val, fuzzy=False)
                    if re.match(r"^\d{4}-\d{2}-\d{2}", val):
                        formats_seen.add("YYYY-MM-DD")
                    elif re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}", val):
                        formats_seen.add("MM/DD/YYYY")
                    elif re.match(r"^\d{1,2}-\d{1,2}-\d{2,4}", val):
                        formats_seen.add("DD-MM-YYYY")
                    else:
                        formats_seen.add("other")
                except (ParserError, ValueError, OverflowError):
                    parse_errors += 1

            if parse_errors > 0:
                issues.append(
                    Issue(
                        type="invalid_date",
                        severity="medium",
                        count=parse_errors,
                        column=col,
                        details={"unparseable_count": parse_errors},
                    )
                )

            if len(formats_seen) > 1:
                issues.append(
                    Issue(
                        type="inconsistent_date_format",
                        severity="low",
                        count=len(series),
                        column=col,
                        details={"formats_detected": sorted(formats_seen)},
                    )
                )

    return issues
