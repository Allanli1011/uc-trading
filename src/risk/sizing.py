"""Position sizing and risk overlays.

Two overlays available:

1. **Vol targeting** — scales the raw position so the strategy's realised
   volatility lines up with a configured annualised target.  Sizing uses
   trailing volatility of the *underlying* (UC), not the strategy, since the
   raw position is already direction-only.

2. **VIX filter** — reduces gross exposure when the equity-vol regime
   indicates risk-off.  Useful because USD/CNH is asymmetrically volatile
   in such regimes.

Both overlays are vectorized and lag-aware: the scaling at time t uses
data up to and including t-1, mirroring the position lag in the engine.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def realized_volatility(prices: pd.Series, lookback: int = 60) -> pd.Series:
    """Annualized realized volatility from daily simple returns."""
    rets = prices.pct_change()
    return rets.rolling(lookback, min_periods=max(10, lookback // 4)).std() * np.sqrt(
        TRADING_DAYS
    )


def apply_vol_target(
    raw_position: pd.Series,
    prices: pd.Series,
    target_annual: float = 0.10,
    lookback: int = 60,
    max_gross: float = 1.0,
) -> pd.Series:
    """Scale a raw position so that ``raw_position × underlying_vol`` lands
    at ``target_annual``.  The output is capped in [-max_gross, +max_gross].
    """
    vol = realized_volatility(prices, lookback)
    scale = target_annual / vol.replace(0, np.nan)
    # Shift by 1 so today's sizing uses yesterday's realised vol — no peek
    scale = scale.shift(1)

    sized = raw_position * scale
    sized = sized.clip(-max_gross, max_gross)
    return sized.rename("position_sized")


def apply_vix_filter(
    position: pd.Series,
    vix: pd.Series,
    threshold: float = 30.0,
    filter_scale: float = 0.5,
) -> pd.Series:
    """Scale position down when VIX (lagged 1 day) is above ``threshold``."""
    vix_lag = vix.shift(1)
    scale = pd.Series(1.0, index=position.index)
    scale.loc[vix_lag.reindex(position.index) > threshold] = filter_scale
    return (position * scale).rename(position.name or "position")
