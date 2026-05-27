"""Shared pytest fixtures.  Generates deterministic synthetic data so the
test suite does not depend on network access.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make ``src`` importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def synthetic_panel() -> pd.DataFrame:
    """Synthetic daily panel mimicking what ``preprocess.align_and_clean``
    produces.  500 business days starting 2020-01-01.
    """
    rng = np.random.default_rng(42)
    idx = pd.bdate_range("2020-01-01", periods=500)
    n = len(idx)

    # UC proxy as a random walk around 7.0
    uc = 7.0 + np.cumsum(rng.normal(0, 0.01, n))
    dxy = 100.0 + np.cumsum(rng.normal(0, 0.2, n))
    tnx = 2.0 + np.cumsum(rng.normal(0, 0.03, n)) * 0.1
    cgb = 3.0 + np.cumsum(rng.normal(0, 0.02, n)) * 0.1
    vix = np.clip(15.0 + np.cumsum(rng.normal(0, 0.5, n)) * 0.1, 8, 80)
    sp500 = 3000.0 + np.cumsum(rng.normal(0, 20, n))
    copper = 4.0 + np.cumsum(rng.normal(0, 0.05, n))

    return pd.DataFrame({
        "uc_proxy": uc,
        "dxy": dxy,
        "treasury_10y": tnx,
        "cgb_10y": cgb,
        "vix": vix,
        "sp500": sp500,
        "copper": copper,
    }, index=idx)


@pytest.fixture(scope="session")
def factor_config() -> dict:
    return {
        "zscore_window": 100,
        "rate_diff_momentum": {"enabled": True, "weight": 1.0, "lookback": 20},
        "dxy_momentum": {"enabled": True, "weight": 1.0, "lookback": 20},
        "vix_change": {"enabled": True, "weight": 0.5, "lookback": 5},
        "copper_momentum": {"enabled": True, "weight": -0.5, "lookback": 20},
        "cnh_mean_revert": {"enabled": True, "weight": -0.5, "lookback": 60},
    }
