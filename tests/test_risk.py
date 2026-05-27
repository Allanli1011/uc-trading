"""Tests for risk overlays."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.risk.sizing import apply_vix_filter, apply_vol_target, realized_volatility


def test_realized_vol_constant_prices():
    idx = pd.bdate_range("2020-01-01", periods=200)
    prices = pd.Series(100.0, index=idx)
    vol = realized_volatility(prices, lookback=20)
    # Constant prices => zero vol after warmup
    assert (vol.dropna() == 0).all()


def test_vol_target_caps_at_max_gross():
    idx = pd.bdate_range("2020-01-01", periods=200)
    # Very low underlying vol → scaling would explode without cap
    prices = pd.Series(100.0 + np.arange(200) * 0.001, index=idx)
    raw = pd.Series(1.0, index=idx)
    sized = apply_vol_target(raw, prices, target_annual=0.10, lookback=20, max_gross=2.0)
    assert sized.dropna().max() <= 2.0001
    assert sized.dropna().min() >= -2.0001


def test_vix_filter_scales_down():
    idx = pd.bdate_range("2020-01-01", periods=10)
    pos = pd.Series(1.0, index=idx)
    vix = pd.Series([10, 10, 10, 10, 35, 35, 10, 10, 10, 10], index=idx)
    filtered = apply_vix_filter(pos, vix, threshold=30.0, filter_scale=0.5)
    # Day 5 and 6: vix at t-1 is 35 -> position should be 0.5
    # Day 5 lag-1 vix = vix[4] = 35 -> scale = 0.5
    # Day 6 lag-1 vix = vix[5] = 35 -> scale = 0.5
    assert filtered.iloc[5] == 0.5
    assert filtered.iloc[6] == 0.5
    # Day 4 lag-1 vix = vix[3] = 10 -> scale = 1.0
    assert filtered.iloc[4] == 1.0
