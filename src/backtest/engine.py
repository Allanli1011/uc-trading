"""Vectorized daily backtest engine.

Conventions
-----------
* ``positions[t]`` is the target position set at the **close** of day t
  using data available up to and including day t.
* With ``signal_lag_days = 1`` (default), the position earning the day-t
  return is ``positions.shift(1)`` — i.e. set at the close of t-1 and held
  through the day-t move.
* Returns are simple percent changes on the price series.
* Cost is charged as ``turnover * cost_bps / 10000`` on the day the trade
  is *deemed* to settle (one day after the signal flips).
* Positions are *fractions of NAV*; the equity curve is geometric.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def run_backtest(
    prices: pd.Series,
    positions: pd.Series,
    cost_bps: float = 1.0,
    signal_lag_days: int = 1,
    start: str | None = None,
) -> pd.DataFrame:
    """Compute strategy returns and equity curve.

    Parameters
    ----------
    prices : Series
        UC daily close prices indexed by date.
    positions : Series
        Target fractional position in [-1, 1] indexed by date.  ``NaN`` is
        treated as flat (0).
    cost_bps : float
        Round-trip transaction cost expressed in basis points of NAV per
        unit of turnover.
    signal_lag_days : int
        Trading lag.  1 means today's position uses yesterday's signal.
    start : str, optional
        ISO date string to clip the backtest (e.g. to skip the factor
        warmup period).

    Returns
    -------
    DataFrame with columns:
        price, return, position, turnover, gross_return, cost,
        net_return, equity
    """
    # Align
    df = pd.concat(
        [prices.rename("price"), positions.rename("position_target")],
        axis=1,
    ).sort_index()
    df = df.dropna(subset=["price"])

    if start:
        df = df[df.index >= pd.Timestamp(start)]
    if df.empty:
        raise ValueError("No data left after clipping to start date")

    # Underlying returns (simple)
    df["return"] = df["price"].pct_change().fillna(0.0)

    # Lag positions and treat NaN as flat
    df["position"] = (
        df["position_target"].fillna(0.0).shift(signal_lag_days).fillna(0.0)
    )

    # Turnover: change in position from prior trading day
    df["turnover"] = df["position"].diff().abs().fillna(df["position"].abs())

    # Costs (in fraction of NAV, charged on the day the trade settles)
    df["cost"] = df["turnover"] * cost_bps / 10_000.0

    df["gross_return"] = df["position"] * df["return"]
    df["net_return"] = df["gross_return"] - df["cost"]

    df["equity"] = (1.0 + df["net_return"]).cumprod()

    # Tidy output: drop helper, reorder columns
    df = df.drop(columns=["position_target"])
    df = df[
        ["price", "return", "position", "turnover", "gross_return", "cost",
         "net_return", "equity"]
    ]

    logger.info(
        "Backtest: %d days, final equity %.4f, total turnover %.1fx",
        len(df), df["equity"].iloc[-1], df["turnover"].sum(),
    )
    return df
