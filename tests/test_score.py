from __future__ import annotations

import pandas as pd
import pytest

from dataruff.score import score
from dataruff.models import ScoreBreakdown
from dataruff.scoring.engine import compute, _completeness, _validity, _consistency, _uniqueness


# ── score() public API ────────────────────────────────────────────────────────

def test_returns_score_breakdown(clean_df):
    s = score(clean_df)
    assert isinstance(s, ScoreBreakdown)


def test_overall_in_0_100_range(clean_df):
    s = score(clean_df)
    assert 0 <= s.overall <= 100


def test_clean_df_high_score(clean_df):
    s = score(clean_df)
    assert s.overall >= 70  # clean data should score well


def test_dirty_df_lower_score(dirty_df):
    s_clean = score(pd.DataFrame({
        "id": [1, 2, 3], "val": [10, 20, 30], "name": ["A", "B", "C"]
    }))
    s_dirty = score(dirty_df)
    assert s_dirty.overall < s_clean.overall


def test_score_breakdown_fields(clean_df):
    s = score(clean_df)
    assert 0 <= s.completeness <= 100
    assert 0 <= s.validity <= 100
    assert 0 <= s.consistency <= 100
    assert 0 <= s.uniqueness <= 100
    assert 0 <= s.schema_compliance <= 100


def test_to_dict(clean_df):
    s = score(clean_df)
    d = s.to_dict()
    assert set(d.keys()) == {
        "overall", "completeness", "validity", "consistency", "uniqueness", "schema_compliance"
    }


def test_accepts_csv(sample_csv):
    s = score(sample_csv)
    assert isinstance(s, ScoreBreakdown)


# ── completeness sub-score ────────────────────────────────────────────────────

def test_completeness_100_for_no_nulls():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    assert _completeness(df) == 100.0


def test_completeness_50_for_half_nulls():
    df = pd.DataFrame({"a": [1, None], "b": [None, 2]})
    assert _completeness(df) == pytest.approx(50.0)


def test_completeness_empty_df():
    df = pd.DataFrame()
    assert _completeness(df) == 100.0


# ── uniqueness sub-score ──────────────────────────────────────────────────────

def test_uniqueness_100_no_duplicates():
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert _uniqueness(df, []) == 100.0


def test_uniqueness_decreases_with_duplicates():
    from dataruff.models import Issue
    df = pd.DataFrame({"a": [1, 1, 2]})
    issue = Issue(type="duplicate_rows", severity="medium", count=1)
    u = _uniqueness(df, [issue])
    assert u < 100.0


# ── weighted scoring ──────────────────────────────────────────────────────────

def test_overall_is_weighted_average():
    from dataruff.scoring.engine import _WEIGHTS
    # weights should sum to 1.0
    assert sum(_WEIGHTS.values()) == pytest.approx(1.0)
