"""Tests for the backtest engine and metrics."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import run_backtest
from src.backtest.metrics import (
    annualized_return,
    annualized_volatility,
    compute_metrics,
    max_drawdown,
    sharpe_ratio,
)


def _trending_prices(n=300, drift=0.0005, vol=0.005, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    rets = rng.normal(drift, vol, n)
    prices = 100.0 * np.exp(np.cumsum(rets))
    return pd.Series(prices, index=idx, name="price")


def test_flat_position_returns_flat_equity():
    prices = _trending_prices()
    pos = pd.Series(0.0, index=prices.index)
    bt = run_backtest(prices, pos, cost_bps=0.0)
    assert np.allclose(bt["equity"], 1.0)
    assert bt["turnover"].sum() == 0


def test_long_position_matches_underlying():
    prices = _trending_prices()
    pos = pd.Series(1.0, index=prices.index)
    bt = run_backtest(prices, pos, cost_bps=0.0, signal_lag_days=0)
    # With lag=0 and full-long, strategy return == underlying return
    np.testing.assert_allclose(
        bt["net_return"].iloc[1:].values,
        prices.pct_change().iloc[1:].values,
    )


def test_signal_lag_shifts_position():
    """With lag=N, the realized position on day t must equal target on day t-N."""
    prices = _trending_prices(seed=1)
    pos = pd.Series(
        np.linspace(-1, 1, len(prices)), index=prices.index, name="target"
    )
    bt = run_backtest(prices, pos, cost_bps=0.0, signal_lag_days=1)
    # Row 0 is filled with 0 (no prior signal); subsequent rows are pos.shift(1)
    assert bt["position"].iloc[0] == 0.0
    np.testing.assert_allclose(bt["position"].iloc[1:].values, pos.iloc[:-1].values)


def test_cost_reduces_return():
    prices = _trending_prices()
    # Alternating position to force turnover
    pos = pd.Series(
        np.where(np.arange(len(prices)) % 2 == 0, 1.0, -1.0),
        index=prices.index,
    )
    bt_no_cost = run_backtest(prices, pos, cost_bps=0.0)
    bt_with_cost = run_backtest(prices, pos, cost_bps=10.0)
    assert bt_with_cost["equity"].iloc[-1] < bt_no_cost["equity"].iloc[-1]
    # Turnover should be roughly 2 per day (flip ±1)
    assert bt_with_cost["turnover"].mean() > 1.5


def test_metrics_finite():
    prices = _trending_prices()
    pos = pd.Series(0.5, index=prices.index)
    bt = run_backtest(prices, pos)
    metrics = compute_metrics(bt)
    for key in ("sharpe", "ann_return", "max_drawdown", "calmar"):
        v = metrics[key]
        assert v == v or v is None  # NaN-tolerant
    assert isinstance(metrics["trading_days"], int)


def test_max_drawdown_negative_or_zero():
    eq = pd.Series([1.0, 1.1, 1.05, 1.2, 0.9, 1.0])
    mdd = max_drawdown(eq)
    assert mdd < 0
    assert mdd == pytest.approx((0.9 - 1.2) / 1.2)


def test_annualized_vol_scale():
    rng = np.random.default_rng(0)
    daily = pd.Series(rng.normal(0, 0.01, 252))  # 1% daily vol
    ann = annualized_volatility(daily)
    assert 0.10 < ann < 0.20  # ~0.01 * sqrt(252) ≈ 0.159
