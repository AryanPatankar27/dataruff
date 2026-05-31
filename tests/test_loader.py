from __future__ import annotations

import pandas as pd
import pytest

from dataruff.loader import load


def test_load_dataframe_returns_copy(clean_df):
    loaded = load(clean_df)
    assert loaded is not clean_df
    pd.testing.assert_frame_equal(loaded, clean_df)


def test_load_csv(sample_csv):
    df = load(sample_csv)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_load_xlsx(tmp_path, clean_df):
    path = tmp_path / "test.xlsx"
    clean_df.to_excel(path, index=False)
    df = load(str(path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(clean_df)


def test_load_unsupported_format(tmp_path):
    path = tmp_path / "file.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load(str(path))


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load("nonexistent_file.csv")


def test_load_pathlib_path(tmp_path, clean_df):
    from pathlib import Path
    path = tmp_path / "data.csv"
    clean_df.to_csv(path, index=False)
    df = load(path)
    assert isinstance(df, pd.DataFrame)
