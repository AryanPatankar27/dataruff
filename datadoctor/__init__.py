"""
datadoctor — One-command dataset health diagnostics.

Usage:
    from datadoctor import audit, fix, score, detect_pii

    audit(df)                    # Print quality report
    fix(df)                      # Return cleaned DataFrame
    score(df)                    # Return ScoreBreakdown
    detect_pii(df)               # Return PIIReport
"""

from datadoctor.audit import audit
from datadoctor.investigate import investigate
from datadoctor.fix import fix
from datadoctor.validate import validate
from datadoctor.compare import compare
from datadoctor.pii import detect_pii, mask_pii
from datadoctor.drift import detect_drift
from datadoctor.anomalies import find_anomalies
from datadoctor.score import score

__version__ = "0.1.0"

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
