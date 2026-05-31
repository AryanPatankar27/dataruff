"""
dataruff — One-command dataset health diagnostics.

Usage:
    from dataruff import audit, fix, score, detect_pii

    audit(df)                    # Print quality report
    fix(df)                      # Return cleaned DataFrame
    score(df)                    # Return ScoreBreakdown
    detect_pii(df)               # Return PIIReport
"""

from dataruff.audit import audit
from dataruff.investigate import investigate
from dataruff.fix import fix
from dataruff.validate import validate
from dataruff.compare import compare
from dataruff.pii import detect_pii, mask_pii
from dataruff.drift import detect_drift
from dataruff.anomalies import find_anomalies
from dataruff.score import score

__version__ = "0.1.1"

__all__ = [
    "audit",
    "investigate",
    "fix",
    "validate",
    "compare",
    "detect_pii",
    "mask_pii",
    "detect_drift",
    "find_anomalies",
    "score",
]
