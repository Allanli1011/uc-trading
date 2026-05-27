"""Weighted composite signal from standardized factors."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def combine_signals(
    z_factors: pd.DataFrame,
    factor_config: dict,
) -> pd.Series:
    """Combine z-scored factors using configured weights.

    Composite at time t = sum(weight_i * z_i(t)) / sum(|weight_i| over
    available factors at t).  Normalizing by the absolute-weight sum keeps
    the composite in a roughly stable range even if some factors drop out
    on a given day (e.g. a data source temporarily missing).

    Returns
    -------
    Series
        Composite signal indexed by date.  Bounded roughly in [-3, 3] given
        the per-factor z-score clipping.
    """
    weights = {}
    for name, params in factor_config.items():
        if name == "zscore_window":
            continue
        if not isinstance(params, dict) or not params.get("enabled", True):
            continue
        if name not in z_factors.columns:
            continue
        weights[name] = float(params.get("weight", 1.0))

    if not weights:
        raise RuntimeError("No factor weights available to combine")

    logger.info("Combining factors with weights: %s", weights)

    # Build weighted sum, respecting per-row availability
    contrib = pd.DataFrame(index=z_factors.index)
    abs_weight_sum = pd.Series(0.0, index=z_factors.index)

    for name, w in weights.items():
        col = z_factors[name]
        contrib[name] = col * w
        abs_weight_sum = abs_weight_sum + col.notna().astype(float) * abs(w)

    raw = contrib.sum(axis=1, min_count=1)
    # Divide by the realized absolute-weight sum to normalize
    composite = raw / abs_weight_sum.where(abs_weight_sum > 0)
    composite.name = "signal"

    return composite


def signal_to_position(
    signal: pd.Series,
    style: str = "proportional",
    threshold: float = 0.0,
    deadband_mode: str = "hard",
) -> pd.Series:
    """Translate a composite signal into a raw target position in [-1, 1].

    Parameters
    ----------
    style : {"proportional", "sign"}
        - ``proportional`` returns ``clip(signal, -1, 1)`` — size scales with
          conviction.  Optionally pass ``threshold > 0`` to add a deadband.
        - ``sign`` returns ``+1``/``-1``/``0`` with a threshold-based deadband.
    threshold : float
        Absolute-value deadband on the signal/position.  Must be in [0, 1).
        ``threshold = 0`` (default) is the legacy behaviour: always positioned.
    deadband_mode : {"hard", "soft"}
        Only relevant for ``proportional`` style with ``threshold > 0``.

        - ``hard``: position is exactly 0 when ``|signal| < threshold``,
          otherwise ``clip(signal, -1, 1)``.  Creates a discrete jump at the
          boundary (entry size = threshold).
        - ``soft``: position is ``sign(signal) × clip((|signal| − threshold)
          / (1 − threshold), 0, 1)``.  Continuous: 0 at the boundary, ±1 at
          the extreme.  No whipsaw jumps but slightly smaller positions for
          mid-strength signals.
    """
    if not 0.0 <= threshold < 1.0:
        raise ValueError(f"threshold must be in [0, 1), got {threshold}")

    if style == "sign":
        pos = np.sign(signal)
        pos = pos.where(signal.abs() > threshold, 0.0)
        return pos.rename("position_raw")

    if style == "proportional":
        if threshold == 0.0:
            return signal.clip(-1.0, 1.0).rename("position_raw")
        if deadband_mode == "hard":
            pos = signal.clip(-1.0, 1.0)
            pos = pos.where(signal.abs() >= threshold, 0.0)
            return pos.rename("position_raw")
        if deadband_mode == "soft":
            sig_abs = signal.abs()
            scaled = ((sig_abs - threshold) / (1.0 - threshold)).clip(lower=0.0, upper=1.0)
            pos = np.sign(signal) * scaled
            return pos.rename("position_raw")
        raise ValueError(f"Unknown deadband_mode: {deadband_mode!r}")

    raise ValueError(f"Unknown signal style: {style!r}")
