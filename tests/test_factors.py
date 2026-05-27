"""Tests for factor construction."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.factors import (
    build_factors,
    cnh_mean_revert,
    dxy_momentum,
    rate_diff_level,
    us_curve_slope,
)


def test_build_factors_shape(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    assert set(factors.columns) == {
        "rate_diff_momentum", "dxy_momentum", "vix_change",
        "copper_momentum", "cnh_mean_revert",
    }
    assert len(factors) == len(synthetic_panel)


def test_factors_no_lookahead(synthetic_panel, factor_config):
    """Factor at time t may only depend on data ≤ t.  Perturbing future data
    must not change the factor at time t.
    """
    factors_orig = build_factors(synthetic_panel, factor_config)
    panel_mod = synthetic_panel.copy()
    # Perturb the last 50 rows of dxy
    panel_mod.iloc[-50:, panel_mod.columns.get_loc("dxy")] *= 1.5
    factors_mod = build_factors(panel_mod, factor_config)
    # First 400 rows should be unaffected
    pd.testing.assert_frame_equal(
        factors_orig.iloc[:-50], factors_mod.iloc[:-50],
        check_exact=False,
    )


def test_dxy_momentum_sign():
    """A monotonically rising DXY must produce a positive momentum factor."""
    idx = pd.bdate_range("2020-01-01", periods=100)
    panel = pd.DataFrame({"dxy": np.linspace(90, 110, 100)}, index=idx)
    f = dxy_momentum(panel, lookback=20)
    assert (f.dropna() > 0).all()


def test_cnh_mean_revert_zscore_bounds():
    """A flat series produces NaN z-scores (zero std)."""
    idx = pd.bdate_range("2020-01-01", periods=200)
    panel = pd.DataFrame({"uc_proxy": np.ones(200) * 7.0}, index=idx)
    f = cnh_mean_revert(panel, lookback=60)
    # All values should be NaN (zero std → divide by NaN)
    assert f.dropna().empty


def test_rate_diff_level_equals_spread():
    """rate_diff_level is the raw UST10Y - CGB10Y spread (z-scored downstream)."""
    idx = pd.bdate_range("2020-01-01", periods=10)
    panel = pd.DataFrame(
        {
            "treasury_10y": np.linspace(2.0, 4.5, 10),
            "cgb_10y": np.linspace(3.0, 2.5, 10),
        },
        index=idx,
    )
    f = rate_diff_level(panel)
    expected = panel["treasury_10y"] - panel["cgb_10y"]
    pd.testing.assert_series_equal(f.rename(None), expected.rename(None))


def test_rate_diff_level_returns_nan_when_missing():
    """Missing CGB column produces an all-NaN series, no crash."""
    idx = pd.bdate_range("2020-01-01", periods=10)
    panel = pd.DataFrame({"treasury_10y": np.linspace(2, 4, 10)}, index=idx)
    f = rate_diff_level(panel)
    assert f.isna().all()


def test_us_curve_slope_momentum_sign():
    """A monotonically steepening curve produces a positive slope momentum."""
    idx = pd.bdate_range("2020-01-01", periods=50)
    panel = pd.DataFrame(
        {
            "treasury_10y": np.linspace(3.0, 5.0, 50),
            "treasury_2y": np.linspace(2.5, 2.5, 50),  # flat at 2.5
        },
        index=idx,
    )
    f = us_curve_slope(panel, lookback=20)
    # slope went from 0.5 to ~2.5; momentum (20-day diff) must be positive
    assert (f.dropna() > 0).all()


def test_factor_registry_has_new_entries():
    """New factor functions should be registered for build_factors."""
    from src.features.factors import _FACTOR_FUNCS
    assert "rate_diff_level" in _FACTOR_FUNCS
    assert "us_curve_slope" in _FACTOR_FUNCS
