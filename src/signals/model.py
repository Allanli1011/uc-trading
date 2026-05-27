"""Factor standardization (rolling z-score)."""
from __future__ import annotations

import pandas as pd


def zscore_factors(
    factors: pd.DataFrame,
    window: int = 252,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Rolling z-score per factor.

    Uses a backward-looking window only, so the signal at time t depends only
    on factor values up to t — no look-ahead.

    Parameters
    ----------
    factors : DataFrame
        Wide DataFrame with one factor per column.
    window : int
        Rolling window length in trading days.
    min_periods : int, optional
        Minimum observations to compute z-score.  Defaults to ``window // 4``.

    Returns
    -------
    DataFrame
        Same shape as ``factors`` with rolling z-scores.  Early rows are NaN
        until ``min_periods`` is satisfied.
    """
    mp = min_periods if min_periods is not None else max(20, window // 4)
    mu = factors.rolling(window, min_periods=mp).mean()
    sd = factors.rolling(window, min_periods=mp).std()
    # Avoid divide-by-zero: where sd is 0 or NaN, z is NaN
    z = (factors - mu) / sd.where(sd > 0)
    # Clip extreme values to avoid one outlier dominating the composite
    z = z.clip(-3.0, 3.0)
    return z
