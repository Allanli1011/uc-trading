"""Macro factor construction for the UC daily strategy.

Each factor produces a single time series with the convention:

    positive value  =>  bullish USD/CNH (UC long)
    negative value  =>  bearish USD/CNH (UC short)

Factor weights in ``config.yaml`` flip the sign for factors that economically
push the *opposite* way (e.g. copper momentum is bearish for UC, so its
weight is negative).
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _safe_get(panel: pd.DataFrame, col: str) -> pd.Series | None:
    if col not in panel.columns:
        logger.warning("Column %r not in panel; skipping dependent factor", col)
        return None
    return panel[col]


# ---------------------------------------------------------------------------
# Individual factor calculators
# ---------------------------------------------------------------------------
def rate_diff_momentum(panel: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Δ(UST10Y - CGB10Y) over ``lookback`` days.

    Widening US-CN spread typically pulls USD/CNH higher.
    """
    ust = _safe_get(panel, "treasury_10y")
    cgb = _safe_get(panel, "cgb_10y")
    if ust is None or cgb is None:
        return pd.Series(np.nan, index=panel.index, name="rate_diff_momentum")
    spread = ust - cgb
    return spread.diff(lookback).rename("rate_diff_momentum")


def dxy_momentum(panel: pd.DataFrame, lookback: int = 20) -> pd.Series:
    dxy = _safe_get(panel, "dxy")
    if dxy is None:
        return pd.Series(np.nan, index=panel.index, name="dxy_momentum")
    return np.log(dxy / dxy.shift(lookback)).rename("dxy_momentum")


def vix_change(panel: pd.DataFrame, lookback: int = 5) -> pd.Series:
    """Risk-off proxy.  Rising VIX -> CNH weakens -> bullish UC."""
    vix = _safe_get(panel, "vix")
    if vix is None:
        return pd.Series(np.nan, index=panel.index, name="vix_change")
    return vix.diff(lookback).rename("vix_change")


def copper_momentum(panel: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """China-growth proxy.  Copper up => CNH strong => UC down.

    The sign is left positive here; the *weight* in config.yaml carries the
    minus sign to keep the orientation contract uniform.
    """
    copper = _safe_get(panel, "copper")
    if copper is None:
        # Fallback to CSI300 if copper unavailable
        copper = _safe_get(panel, "csi300")
        if copper is None:
            return pd.Series(np.nan, index=panel.index, name="copper_momentum")
    return np.log(copper / copper.shift(lookback)).rename("copper_momentum")


def cnh_mean_revert(panel: pd.DataFrame, lookback: int = 60) -> pd.Series:
    """Rolling z-score of UC price.  High z => overextended => fade."""
    uc = _safe_get(panel, "uc_proxy")
    if uc is None:
        return pd.Series(np.nan, index=panel.index, name="cnh_mean_revert")
    mu = uc.rolling(lookback, min_periods=max(10, lookback // 4)).mean()
    sd = uc.rolling(lookback, min_periods=max(10, lookback // 4)).std()
    z = (uc - mu) / sd
    return z.rename("cnh_mean_revert")


def rate_diff_level(panel: pd.DataFrame, lookback: int | None = None) -> pd.Series:
    """**Level** of the US-China 10Y rate spread (carry signal).

    A high spread makes long USD/CNH a positive-carry position, which
    historically attracts inflows and pushes UC higher.  Standardization
    is handled downstream by ``zscore_factors`` so ``lookback`` is
    unused here.
    """
    ust = _safe_get(panel, "treasury_10y")
    cgb = _safe_get(panel, "cgb_10y")
    if ust is None or cgb is None:
        return pd.Series(np.nan, index=panel.index, name="rate_diff_level")
    return (ust - cgb).rename("rate_diff_level")


def us_curve_slope(panel: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Momentum of the US 2s10s yield curve slope.

    Sign is left ambiguous (bull- vs bear-steepening have opposite USD
    implications); the configured weight or walk-forward Ridge picks the
    direction empirically.
    """
    ust10 = _safe_get(panel, "treasury_10y")
    ust2 = _safe_get(panel, "treasury_2y")
    if ust10 is None or ust2 is None:
        return pd.Series(np.nan, index=panel.index, name="us_curve_slope")
    slope = ust10 - ust2
    return slope.diff(lookback).rename("us_curve_slope")


def gold_momentum(panel: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Gold price momentum.

    Gold has historically been inversely correlated with the USD trade-
    weighted basket: rising gold tends to coincide with a softer USD,
    which is bearish for UC.  We expose the raw log-return here; the
    configured weight in ``config.yaml`` carries the sign.
    """
    gold = _safe_get(panel, "gold")
    if gold is None:
        return pd.Series(np.nan, index=panel.index, name="gold_momentum")
    return np.log(gold / gold.shift(lookback)).rename("gold_momentum")


def bitcoin_momentum(panel: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Bitcoin price momentum as a risk-on / liquidity proxy.

    Since ~2020 BTC has co-moved with broad risk assets (NASDAQ-like
    behaviour).  Rising BTC → risk-on regime → CNH strength → UC down.
    Direction is left to the configured weight; volatility is large so
    the rolling z-score downstream will dampen extreme moves.
    """
    btc = _safe_get(panel, "bitcoin")
    if btc is None:
        return pd.Series(np.nan, index=panel.index, name="bitcoin_momentum")
    return np.log(btc / btc.shift(lookback)).rename("bitcoin_momentum")


# ---------------------------------------------------------------------------
# Registry & builder
# ---------------------------------------------------------------------------
_FACTOR_FUNCS = {
    "rate_diff_momentum": rate_diff_momentum,
    "dxy_momentum": dxy_momentum,
    "vix_change": vix_change,
    "copper_momentum": copper_momentum,
    "cnh_mean_revert": cnh_mean_revert,
    "rate_diff_level": rate_diff_level,
    "us_curve_slope": us_curve_slope,
    "gold_momentum": gold_momentum,
    "bitcoin_momentum": bitcoin_momentum,
}


def build_factors(panel: pd.DataFrame, factor_config: dict) -> pd.DataFrame:
    """Compute every enabled factor and return as a wide DataFrame.

    Parameters
    ----------
    panel : DataFrame
        Output of ``preprocess.align_and_clean``.
    factor_config : dict
        ``factors`` block from config.yaml.  Each key maps to
        ``{enabled, weight, lookback, ...}``.

    Returns
    -------
    DataFrame
        Columns are factor names, rows are dates.  NaNs are preserved so
        downstream z-scoring can decide how to handle warmup.
    """
    out = {}
    for name, params in factor_config.items():
        if name == "zscore_window":
            continue
        if not isinstance(params, dict) or not params.get("enabled", True):
            continue
        fn = _FACTOR_FUNCS.get(name)
        if fn is None:
            logger.warning("Unknown factor %r in config — skipping", name)
            continue
        lookback = params.get("lookback", 20)
        try:
            out[name] = fn(panel, lookback=lookback)
        except Exception as exc:
            logger.error("Factor %s failed: %s", name, exc)

    if not out:
        raise RuntimeError("No factors could be built; check data availability")

    factors = pd.concat(out.values(), axis=1)
    factors.index.name = "date"
    logger.info("Built %d factors: %s", factors.shape[1], factors.columns.tolist())
    return factors
