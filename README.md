# dataruff

[![CI](https://github.com/AryanPatankar27/dataruff/actions/workflows/ci.yml/badge.svg)](https://github.com/AryanPatankar27/dataruff/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/AryanPatankar27/dataruff/branch/main/graph/badge.svg)](https://codecov.io/gh/AryanPatankar27/dataruff)
[![PyPI version](https://img.shields.io/pypi/v/dataruff)](https://pypi.org/project/dataruff/)
[![Python](https://img.shields.io/pypi/pyversions/dataruff)](https://pypi.org/project/dataruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The Ruff of datasets.** One command to discover, explain, score, and fix data quality problems in Pandas DataFrames and CSV/Excel files.

```python
from dataruff import audit

audit(df)
```

```
Data Quality Score: 81/100

Issues Found (5):
  !      42 duplicate rows
  ~      13 invalid email  (column: email)
  !       3 empty columns
  ~       7 outlier  (column: salary)
  .       2 inconsistent date format  (column: created_at)

Rows: 10,000 | Columns: 12
```

---

## Install

```bash
pip install dataruff
```

Optionally install [rich](https://github.com/Textualize/rich) for prettier terminal output:

```bash
pip install dataruff[rich]
```

---

## Quick start

```python
import pandas as pd
from dataruff import audit, fix, score, validate, detect_pii

df = pd.read_csv("customers.csv")

# Full health report
audit(df)

# Get numeric score
s = score(df)
print(s.overall)   # 81
print(s.to_dict()) # {'overall': 81, 'completeness': 92, ...}

# Auto-fix common issues
clean_df = fix(df)

# Validate against a schema
result = validate(df, schema={
    "email": "email",
    "age":   "0-120",
    "id":    "unique",
})

# PII detection
report = detect_pii(df)
print(report.columns_with_pii)
# {'email': ['email'], 'phone': ['phone'], 'uid': ['aadhaar']}
```

---

## API reference

| Function | Description | Returns |
|---|---|---|
| `audit(df)` | Print full health report | `InvestigationReport` |
| `investigate(df)` | Structured issue breakdown | `InvestigationReport` |
| `score(df)` | Data quality score | `ScoreBreakdown` |
| `fix(df)` | Auto-repair common issues | `pd.DataFrame` |
| `validate(df, schema)` | Check schema constraints | `dict` |
| `compare(old, new)` | Diff two datasets | `ComparisonReport` |
| `detect_pii(df)` | Find PII columns | `PIIReport` |
| `mask_pii(df)` | Redact PII values | `pd.DataFrame` |
| `detect_drift(old, new)` | Distribution drift analysis | `DriftReport` |
| `find_anomalies(df)` | Anomaly / outlier detection | `dict` |

All functions accept a **DataFrame, CSV path, or XLSX path** as input.

---

## Scoring formula

| Dimension | Weight | Measures |
|---|---|---|
| Completeness | 25% | Non-null ratio across all cells |
| Validity | 25% | Format correctness (emails, dates, types) |
| Consistency | 20% | Uniform types and formats per column |
| Uniqueness | 20% | Absence of duplicate rows |
| Schema compliance | 10% | Adherence to user-provided schema |

---

## `fix()` — what gets repaired

| Issue | Fix applied |
|---|---|
| Duplicate rows | Removed |
| Leading/trailing whitespace | Stripped |
| Boolean strings (`yes/no/true/false`) | Converted to `bool` |
| Mixed date formats | Normalized to `YYYY-MM-DD` |
| Missing numeric values | Filled with column median |
| Missing string values | Filled with column mode |

---

## `validate()` — schema rules

```python
validate(df, schema={
    "email":   "email",          # valid email format
    "age":     "0-120",          # numeric range
    "user_id": "unique",         # no duplicates
    "price":   "positive",       # > 0
    "code":    "not_null",       # no missing values
    "ref":     "regex:[A-Z]{3}", # custom regex
})
```

---

## `detect_pii()` — supported PII types

| Type | Example |
|---|---|
| `email` | `alice@example.com` |
| `phone` | `9876543210` |
| `aadhaar` | `2345 6789 0123` |
| `pan` | `ABCDE1234F` |
| `ssn` | `123-45-6789` |
| `credit_card` | `4111 1111 1111 1111` |

---

## CLI

```bash
# Audit a CSV file
dataruff audit customers.csv

# Output as JSON
dataruff audit customers.csv --json

# Fix issues and write cleaned file
dataruff fix customers.csv
# -> customers_clean.csv

# Compare two datasets
dataruff compare old.csv new.csv

# Data quality score
dataruff score customers.csv

# PII detection
dataruff detect-pii customers.csv

# Mask PII
dataruff mask-pii customers.csv
# -> customers_masked.csv
```

---

## Architecture

```
dataruff/
├── analyzers/       # DuplicateAnalyzer, NullAnalyzer, TypeAnalyzer,
│                    # FormatAnalyzer, OutlierAnalyzer, PIIAnalyzer, DriftAnalyzer
├── scoring/         # Weighted scoring engine
├── fixing/          # Auto-remediation rules
└── reporting/       # Terminal (rich + plain fallback) and JSON output
```

No LLMs. No API calls. Everything deterministic and offline.

---

## Requirements

- Python 3.10+
- pandas, numpy, scipy, scikit-learn, openpyxl, python-dateutil

---

## License

MIT
