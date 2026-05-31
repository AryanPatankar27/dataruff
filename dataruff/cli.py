from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dataruff",
        description="Data quality diagnostics for CSV and Excel files.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # audit
    p = sub.add_parser("audit", help="Audit dataset for data-quality issues")
    p.add_argument("file", help="CSV or XLSX file")
    p.add_argument("--json", action="store_true", help="Output as JSON")

    # fix
    p = sub.add_parser("fix", help="Fix data-quality issues and write cleaned file")
    p.add_argument("file", help="CSV or XLSX file")
    p.add_argument("--output", "-o", help="Output path (default: <stem>_clean.csv)")

    # compare
    p = sub.add_parser("compare", help="Compare two datasets")
    p.add_argument("old", help="Old CSV or XLSX file")
    p.add_argument("new", help="New CSV or XLSX file")

    # score
    p = sub.add_parser("score", help="Print quality score breakdown")
    p.add_argument("file", help="CSV or XLSX file")

    # detect-pii
    p = sub.add_parser("detect-pii", help="Detect PII columns")
    p.add_argument("file", help="CSV or XLSX file")

    # mask-pii
    p = sub.add_parser("mask-pii", help="Mask PII and write redacted file")
    p.add_argument("file", help="CSV or XLSX file")
    p.add_argument("--output", "-o", help="Output path (default: <stem>_masked.csv)")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "audit":
        from dataruff.audit import audit
        from dataruff.reporting.json_reporter import to_json

        report = audit(args.file)
        if args.json:
            print(to_json(report))

    elif args.command == "fix":
        from dataruff.fix import fix

        cleaned = fix(args.file)
        p = Path(args.file)
        out = args.output or str(p.parent / f"{p.stem}_clean{p.suffix}")
        cleaned.to_csv(out, index=False)
        print(f"Fixed dataset saved to: {out}")

    elif args.command == "compare":
        from dataruff.compare import compare

        report = compare(args.old, args.new)
        print("\nComparison Report:")
        print(f"  Rows added:   {report.rows_added:,}")
        print(f"  Rows deleted: {report.rows_deleted:,}")
        if report.columns_added:
            print(f"  Columns added:   {', '.join(report.columns_added)}")
        if report.columns_removed:
            print(f"  Columns removed: {', '.join(report.columns_removed)}")
        if report.type_changes:
            print("  Type changes:")
            for col, (old_t, new_t) in report.type_changes.items():
                print(f"    {col}: {old_t} → {new_t}")
        print()

    elif args.command == "score":
        from dataruff.score import score

        s = score(args.file)
        print(f"\nData Quality Score: {s.overall}/100")
        print(f"  Completeness:      {s.completeness}")
        print(f"  Validity:          {s.validity}")
        print(f"  Consistency:       {s.consistency}")
        print(f"  Uniqueness:        {s.uniqueness}")
        print(f"  Schema Compliance: {s.schema_compliance}")
        print()

    elif args.command == "detect-pii":
        from dataruff.pii import detect_pii
        from dataruff.reporting.terminal import print_pii_report

        report = detect_pii(args.file)
        print_pii_report(report)

    elif args.command == "mask-pii":
        from dataruff.pii import mask_pii

        masked = mask_pii(args.file)
        p = Path(args.file)
        out = args.output or str(p.parent / f"{p.stem}_masked{p.suffix}")
        masked.to_csv(out, index=False)
        print(f"Masked dataset saved to: {out}")


if __name__ == "__main__":
    main()
