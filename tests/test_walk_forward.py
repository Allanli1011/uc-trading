"""Tests for walk-forward Ridge signal — no look-ahead, shape, refit cadence."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.factors import build_factors
from src.signals.model import zscore_factors
from src.signals.walk_forward import walk_forward_signal


def test_walk_forward_no_lookahead(synthetic_panel, factor_config):
    """Perturbing factor values in the future must not change the signal at t."""
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)
    uc_log_ret = np.log(synthetic_panel["uc_proxy"]).diff()

    res_orig = walk_forward_signal(
        z, uc_log_ret, window_days=200, refit_every=21, alpha=1.0,
    )
    # Perturb the last 50 rows of z-factors
    z_mod = z.copy()
    z_mod.iloc[-50:] *= 3.0
    res_mod = walk_forward_signal(
        z_mod, uc_log_ret, window_days=200, refit_every=21, alpha=1.0,
    )

    # Raw prediction up to (and including) position window_days+ should
    # be deterministic given training data — the perturbation only affects
    # later positions.  Check first 80% of overlap is identical.
    n = len(z) - 50
    pd.testing.assert_series_equal(
        res_orig.raw_prediction.iloc[:n],
        res_mod.raw_prediction.iloc[:n],
        check_exact=False,
    )


def test_walk_forward_no_target_lookahead():
    """If we shuffle FUTURE target returns, signal at t must be unchanged.

    Target at training position p uses returns[p+1].  So perturbing
    returns *after* the most-recent fit window should not affect any
    prediction.  Here we verify by training on a small window and then
    perturbing returns past the last refit.
    """
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2020-01-01", periods=400)
    z = pd.DataFrame({
        "f1": rng.normal(size=400),
        "f2": rng.normal(size=400),
    }, index=idx)
    ret = pd.Series(rng.normal(0, 0.005, size=400), index=idx)

    res_orig = walk_forward_signal(z, ret, window_days=100, refit_every=21, alpha=1.0)
    ret_mod = ret.copy()
    # Perturb only the very last day's return — it cannot influence any
    # training because targets are shifted -1 (factors[t] paired with ret[t+1])
    # and the last refit cannot use future returns past its window.
    ret_mod.iloc[-1] *= 10
    res_mod = walk_forward_signal(z, ret_mod, window_days=100, refit_every=21, alpha=1.0)

    # Predictions before the last refit must be identical
    last_fit = res_orig.weights.index.max()
    mask = res_orig.raw_prediction.index < last_fit
    pd.testing.assert_series_equal(
        res_orig.raw_prediction[mask], res_mod.raw_prediction[mask],
        check_exact=False,
    )


def test_walk_forward_outputs_shape(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)
    uc_log_ret = np.log(synthetic_panel["uc_proxy"]).diff()

    res = walk_forward_signal(z, uc_log_ret, window_days=200, refit_every=21)
    # Signal aligned with z-factors
    assert len(res.signal) == len(z)
    # Weights have one row per refit, columns include all factors + intercept + n_train
    assert set(z.columns).issubset(res.weights.columns)
    assert "intercept" in res.weights.columns
    assert "n_train" in res.weights.columns
    # First valid signal position is at least window_days
    assert res.signal.first_valid_index() >= z.index[200 + 19]  # warmup buffer


def test_walk_forward_signal_bounded(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)
    uc_log_ret = np.log(synthetic_panel["uc_proxy"]).diff()
    res = walk_forward_signal(z, uc_log_ret, window_days=200, refit_every=21)
    assert res.signal.abs().max() <= 3.0001
