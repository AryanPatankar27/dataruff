from __future__ import annotations

from dataruff.models import DriftReport, InvestigationReport, PIIReport

try:
    from rich.console import Console
    from rich.table import Table

    _RICH = True
except ImportError:
    _RICH = False


def print_audit_report(report: InvestigationReport) -> None:
    if _RICH:
        _rich_audit(report)
    else:
        _plain_audit(report)


def _rich_audit(report: InvestigationReport) -> None:
    from rich.console import Console

    console = Console(highlight=False, soft_wrap=True)
    score = report.score

    color = "green" if score.overall >= 80 else ("yellow" if score.overall >= 60 else "red")
    console.print(f"\n[bold {color}]Data Quality Score: {score.overall}/100[/bold {color}]")
    console.print(
        f"[dim]Completeness {score.completeness} | "
        f"Validity {score.validity} | "
        f"Consistency {score.consistency} | "
        f"Uniqueness {score.uniqueness}[/dim]"
    )

    if not report.issues:
        console.print("[green]\nNo issues found — dataset is clean![/green]\n")
        return

    console.print(f"\n[bold]Issues Found ({len(report.issues)}):[/bold]")
    _ICONS = {"high": "[red]![/red]", "medium": "[yellow]~[/yellow]", "low": "[green].[/green]"}
    for issue in report.issues:
        icon = _ICONS.get(issue.severity, ".")
        col_note = f"  [dim](column: {issue.column})[/dim]" if issue.column else ""
        label = issue.type.replace("_", " ")
        console.print(f"  {icon} {issue.count:>6} {label}{col_note}")

    console.print(
        f"\n[dim]Rows: {report.row_count:,} | Columns: {report.column_count}[/dim]\n"
    )


def _plain_audit(report: InvestigationReport) -> None:
    score = report.score
    print(f"\nData Quality Score: {score.overall}/100")
    print(
        f"  Completeness: {score.completeness} | Validity: {score.validity} | "
        f"Consistency: {score.consistency} | Uniqueness: {score.uniqueness}"
    )

    if not report.issues:
        print("\nNo issues found — dataset is clean!\n")
        return

    print(f"\nIssues Found ({len(report.issues)}):")
    for issue in report.issues:
        col_note = f"  (column: {issue.column})" if issue.column else ""
        label = issue.type.replace("_", " ")
        print(f"  * {issue.count:>6} {label}{col_note}")

    print(f"\nRows: {report.row_count:,} | Columns: {report.column_count}\n")


def print_pii_report(report: PIIReport) -> None:
    if not report.has_pii():
        print("\nNo PII detected.\n")
        return

    print("\nPotential PII Found:")
    for col, pii_types in report.columns_with_pii.items():
        print(f"  * {col}: {', '.join(pii_types)}")
    print()


def print_drift_report(report: DriftReport) -> None:
    print("\nDrift Analysis:")

    if not report.has_drift():
        print("  No significant drift detected.\n")
        return

    print(f"  Drifted columns ({len(report.drifted_columns)}): {', '.join(report.drifted_columns)}")

    significant_dist = {c: v for c, v in report.distribution_drift.items() if v > 0.1}
    if significant_dist:
        print("\n  Distribution drift (KS statistic > 0.10):")
        for col, stat in significant_dist.items():
            print(f"    * {col}: {stat:.4f}")

    if report.category_drift:
        print("\n  Category drift:")
        for col, changes in report.category_drift.items():
            print(f"    * {col}: {len(changes)} categories shifted")

    if report.missing_value_drift:
        significant_mv = {c: v for c, v in report.missing_value_drift.items() if v > 5}
        if significant_mv:
            print("\n  Missing-value drift (>5 pp change):")
            for col, change in significant_mv.items():
                print(f"    * {col}: {change:+.1f} pp")
    print()
