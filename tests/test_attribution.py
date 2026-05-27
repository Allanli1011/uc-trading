"""Tests for per-factor attribution."""
from __future__ import annotations

import pandas as pd

from src.features.factors import build_factors
from src.signals.attribution import (
    attribution_table,
    format_attribution_table,
    per_factor_backtest,
)
from src.signals.model import zscore_factors


def test_attribution_returns_one_entry_per_factor(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)

    risk_cfg = {
        "vol_target_annual": 0.10,
        "vol_lookback": 60,
        "max_gross_position": 1.0,
    }
    bt_cfg = {"signal_lag_days": 1, "cost_bps": 0.0, "start_date": None}

    results = per_factor_backtest(z, synthetic_panel, factor_config, risk_cfg, bt_cfg)
    assert set(results.keys()) == set(z.columns)
    for name, res in results.items():
        assert "metrics" in res
        assert "backtest" in res
        assert isinstance(res["backtest"], pd.DataFrame)
        assert {"price", "position", "equity", "net_return"} <= set(res["backtest"].columns)


def test_attribution_table_sorted_by_sharpe(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)
    risk_cfg = {"vol_target_annual": 0.10, "vol_lookback": 60, "max_gross_position": 1.0}
    bt_cfg = {"signal_lag_days": 1, "cost_bps": 0.0, "start_date": None}

    results = per_factor_backtest(z, synthetic_panel, factor_config, risk_cfg, bt_cfg)
    tbl = attribution_table(results)
    # Sharpe column should be monotonic non-increasing (sorted desc)
    sharpes = tbl["sharpe"].values
    for i in range(len(sharpes) - 1):
        assert sharpes[i] >= sharpes[i + 1] or pd.isna(sharpes[i + 1])


def test_format_attribution_table_returns_string(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)
    risk_cfg = {"vol_target_annual": 0.10, "vol_lookback": 60, "max_gross_position": 1.0}
    bt_cfg = {"signal_lag_days": 1, "cost_bps": 0.0, "start_date": None}
    results = per_factor_backtest(z, synthetic_panel, factor_config, risk_cfg, bt_cfg)
    tbl = attribution_table(results)
    s = format_attribution_table(tbl)
    assert isinstance(s, str)
    assert "Sharpe" in s
    for name in z.columns:
        assert name in s
