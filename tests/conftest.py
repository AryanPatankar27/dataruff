"""Shared fixtures for datadoctor tests."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def clean_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "email": [
            "alice@example.com",
            "bob@example.com",
            "charlie@example.com",
            "diana@example.com",
            "eve@example.com",
        ],
        "age": [25, 30, 35, 28, 32],
        "score": [85.0, 90.0, 78.0, 92.0, 88.0],
    })


@pytest.fixture
def dirty_df() -> pd.DataFrame:
    """DataFrame with duplicates, nulls, invalid emails, and an outlier."""
    return pd.DataFrame({
        "id":    [1,                     2,              3,                     4,     5,               2],
        "name":  ["Alice",               "Bob",          "Charlie",             None,  "  Eve  ",       "Bob"],
        "email": ["alice@example.com",   "not-an-email", "charlie@example.com", "bad", "eve@example.com", "not-an-email"],
        "age":   [25,                    30,             35,                    None,  32,              30],
        "score": [85.0,                  90.0,           78.0,                  500.0, 88.0,            90.0],
    })


@pytest.fixture
def pii_df() -> pd.DataFrame:
    return pd.DataFrame({
        "customer_id": [1, 2, 3],
        "email": ["john@example.com", "jane@test.org", "bob@email.net"],
        "phone": ["9876543210", "8765432109", "7654321098"],
        "aadhaar": ["2345 6789 0123", "9876 5432 1098", "5555 4444 3333"],
        "name": ["John Doe", "Jane Smith", "Bob Jones"],
    })


@pytest.fixture
def outlier_df() -> pd.DataFrame:
    base = list(range(50))
    base.append(500)  # extreme outlier
    return pd.DataFrame({"value": base})


@pytest.fixture
def sample_csv(tmp_path: pytest.TempPathFactory, dirty_df: pd.DataFrame) -> str:
    path = tmp_path / "test.csv"
    dirty_df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def clean_csv(tmp_path: pytest.TempPathFactory, clean_df: pd.DataFrame) -> str:
    path = tmp_path / "clean.csv"
    clean_df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def pii_csv(tmp_path: pytest.TempPathFactory, pii_df: pd.DataFrame) -> str:
    path = tmp_path / "pii.csv"
    pii_df.to_csv(path, index=False)
    return str(path)
