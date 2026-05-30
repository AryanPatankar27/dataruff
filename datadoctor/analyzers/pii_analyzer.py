from __future__ import annotations

import re

import pandas as pd

_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
    ),
    "phone": re.compile(
        r"\b(?:\+?91[-.\s]?)?[6-9]\d{9}\b"
        r"|\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    ),
    "aadhaar": re.compile(r"\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b"),
    "pan": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(
        r"\b(?:4\d{3}|5[1-5]\d{2}|6011|3[47]\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
    ),
}

_COLUMN_HINTS: dict[str, list[str]] = {
    "email": ["email", "mail", "e-mail", "e_mail"],
    "phone": ["phone", "mobile", "cell", "tel", "contact", "phoneno", "phone_no"],
    "aadhaar": ["aadhaar", "aadhar", "uid", "uidai"],
    "pan": ["pan", "pan_number", "panno", "pan_no"],
    "ssn": ["ssn", "social_security", "social_security_number"],
    "credit_card": ["card", "cc_number", "credit_card", "creditcard", "cardno"],
}

_CONTENT_SCAN_SAMPLE = 200


def analyze(df: pd.DataFrame) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}

    for col in df.columns:
        pii_found: set[str] = set()
        col_lower = col.lower()

        for pii_type, hints in _COLUMN_HINTS.items():
            if any(h in col_lower for h in hints):
                pii_found.add(pii_type)

        if df[col].dtype == object:
            sample = df[col].dropna().astype(str).head(_CONTENT_SCAN_SAMPLE)
            for pii_type, pattern in _PATTERNS.items():
                if pii_type not in pii_found:
                    if any(pattern.search(val) for val in sample):
                        pii_found.add(pii_type)

        if pii_found:
            results[col] = sorted(pii_found)

    return results
