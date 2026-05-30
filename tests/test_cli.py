from __future__ import annotations

import json
import pytest

from datadoctor.cli import main, _build_parser


# ── parser smoke tests ────────────────────────────────────────────────────────

def test_parser_no_args_exits():
    with pytest.raises(SystemExit):
        _build_parser().parse_args([])


def test_parser_unknown_command_exits():
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["unknown"])


def test_parser_audit_command(clean_csv):
    args = _build_parser().parse_args(["audit", clean_csv])
    assert args.command == "audit"
    assert args.file == clean_csv
    assert args.json is False


def test_parser_audit_json_flag(clean_csv):
    args = _build_parser().parse_args(["audit", clean_csv, "--json"])
    assert args.json is True


def test_parser_fix_command(clean_csv):
    args = _build_parser().parse_args(["fix", clean_csv])
    assert args.command == "fix"


def test_parser_compare_command(clean_csv):
    args = _build_parser().parse_args(["compare", clean_csv, clean_csv])
    assert args.command == "compare"
    assert args.old == clean_csv
    assert args.new == clean_csv


# ── end-to-end CLI calls ──────────────────────────────────────────────────────

def test_cli_audit_runs(clean_csv, capsys):
    main(["audit", clean_csv])
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_cli_audit_json_output(clean_csv, capsys):
    main(["audit", clean_csv, "--json"])
    captured = capsys.readouterr()
    # The JSON block starts with a standalone '{' on its own line
    idx = captured.out.find("\n{")
    assert idx != -1, f"No JSON block found in output:\n{captured.out}"
    data = json.loads(captured.out[idx:].strip())
    assert "score" in data
    assert "overall" in data["score"]


def test_cli_fix_creates_output_file(tmp_path, sample_csv):
    out = str(tmp_path / "fixed.csv")
    main(["fix", sample_csv, "--output", out])
    import os
    assert os.path.exists(out)


def test_cli_fix_default_output_name(tmp_path):
    import pandas as pd
    df = pd.DataFrame({"id": [1, 1, 2], "val": ["a", "a", "b"]})
    path = tmp_path / "mydata.csv"
    df.to_csv(path, index=False)
    main(["fix", str(path)])
    clean_path = tmp_path / "mydata_clean.csv"
    assert clean_path.exists()


def test_cli_score_runs(clean_csv, capsys):
    main(["score", clean_csv])
    captured = capsys.readouterr()
    assert "Score" in captured.out


def test_cli_detect_pii_runs(pii_csv, capsys):
    main(["detect-pii", pii_csv])
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_cli_mask_pii_creates_file(tmp_path, pii_csv):
    out = str(tmp_path / "masked.csv")
    main(["mask-pii", pii_csv, "--output", out])
    import os
    assert os.path.exists(out)


def test_cli_compare_runs(clean_csv, capsys):
    main(["compare", clean_csv, clean_csv])
    captured = capsys.readouterr()
    assert "Comparison" in captured.out
