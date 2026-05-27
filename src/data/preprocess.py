"""Align loaded series onto a common business-day index and apply scaling.

Series that come in as basis points or scaled percent (e.g. ``^TNX`` returns
the 10-year UST yield multiplied by 10) are normalized to percent here so
that downstream factor formulas can mix sources without unit surprises.
"""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


# Logical names that come from a Yahoo Finance treasury ticker (^TNX, ^FVX,
# ^TYX) which Yahoo quotes as yield × 10.  Update this set if you wire any
# new Yahoo treasury ticker into config.yaml.
_YAHOO_TREASURY_NAMES = {"treasury_10y"}

# Rate-like series that change slowly — forward-filled across non-trading days
_RATE_LIKE = _YAHOO_TREASURY_NAMES | {
    "cgb_10y", "shibor_1m", "sofr", "treasury_2y", "treasury_5y", "treasury_30y",
}


def align_and_clean(
    data: dict[str, pd.DataFrame],
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """Merge loaded DataFrames into a wide panel keyed by date.

    Parameters
    ----------
    data : dict[str, DataFrame]
        Output of ``loaders.load_all``.  Each value must have a ``close``
        column and a DatetimeIndex.
    start, end : str, optional
        ISO date strings to clip the output.

    Returns
    -------
    DataFrame
        Wide DataFrame indexed by business-day date with one column per
        input series.  Rate-like series are forward-filled; price-like
        series are NOT (to preserve real trading days for return calc).
    """
    if not data:
        raise ValueError("No data to align")

    # Build wide frame on the union of all dates
    frames: list[pd.Series] = []
    for name, df in data.items():
        if "close" not in df.columns:
            logger.warning("%s has no 'close' column, skipping", name)
            continue
        s = df["close"].copy()
        s.name = name
        # Normalize yield ×10 quoting to plain percent
        if name in _YAHOO_TREASURY_NAMES:
            s = s / 10.0
        frames.append(s)

    wide = pd.concat(frames, axis=1).sort_index()

    # Clip to requested window
    if start:
        wide = wide[wide.index >= pd.Timestamp(start)]
    if end:
        wide = wide[wide.index <= pd.Timestamp(end)]

    # Restrict to business days only (UC trades Mon-Fri)
    bdays = pd.bdate_range(wide.index.min(), wide.index.max())
    wide = wide.reindex(bdays)
    wide.index.name = "date"

    # Forward-fill rate-like series
    rate_cols = [c for c in wide.columns if c in _RATE_LIKE]
    if rate_cols:
        wide[rate_cols] = wide[rate_cols].ffill()

    # Drop rows where the UC proxy itself is missing — we cannot trade then
    if "uc_proxy" in wide.columns:
        wide = wide.dropna(subset=["uc_proxy"])

    logger.info(
        "Aligned panel: %d rows × %d cols, %s -> %s",
        len(wide), wide.shape[1],
        wide.index.min().date() if len(wide) else None,
        wide.index.max().date() if len(wide) else None,
    )
    return wide


def add_returns(panel: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Append log-return columns ``<col>_ret`` for the requested price columns."""
    out = panel.copy()
    cols = columns or [c for c in panel.columns if c not in _RATE_LIKE]
    import numpy as np

    for c in cols:
        out[f"{c}_ret"] = np.log(panel[c]).diff()
    return out
