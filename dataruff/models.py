from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Issue:
    type: str
    severity: str  # "high" | "medium" | "low"
    count: int
    column: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        loc = f" in '{self.column}'" if self.column else ""
        return f"[{self.severity}] {self.type}{loc}: {self.count}"


@dataclass
class ScoreBreakdown:
    overall: int
    completeness: float
    validity: float
    consistency: float
    uniqueness: float
    schema_compliance: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "overall": self.overall,
            "completeness": self.completeness,
            "validity": self.validity,
            "consistency": self.consistency,
            "uniqueness": self.uniqueness,
            "schema_compliance": self.schema_compliance,
        }


@dataclass
class InvestigationReport:
    row_count: int
    column_count: int
    issues: list[Issue]
    score: ScoreBreakdown

    def issue_count(self) -> int:
        return len(self.issues)

    def issues_by_type(self, issue_type: str) -> list[Issue]:
        return [i for i in self.issues if i.type == issue_type]

    def issues_by_severity(self, severity: str) -> list[Issue]:
        return [i for i in self.issues if i.severity == severity]


@dataclass
class ComparisonReport:
    rows_added: int
    rows_deleted: int
    columns_added: list[str]
    columns_removed: list[str]
    type_changes: dict[str, tuple[str, str]]
    value_changes: int


@dataclass
class PIIReport:
    columns_with_pii: dict[str, list[str]]

    def has_pii(self) -> bool:
        return bool(self.columns_with_pii)

    def pii_types(self) -> list[str]:
        types: set[str] = set()
        for pii_list in self.columns_with_pii.values():
            types.update(pii_list)
        return sorted(types)


@dataclass
class DriftReport:
    distribution_drift: dict[str, float]
    category_drift: dict[str, dict[str, Any]]
    missing_value_drift: dict[str, float]
    drifted_columns: list[str]

    def has_drift(self) -> bool:
        return bool(self.drifted_columns)
