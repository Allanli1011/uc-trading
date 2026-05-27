"""Walk-forward Ridge regression for adaptive factor weighting.

At each refit date t, fits ``next_day_return ~ sum(beta_i * z_factor_i)``
using the prior ``window_days`` of *standardized* factors and *realised*
next-day returns.  Predictions for dates between refits use the most
recent fitted weights.  Strictly no look-ahead.

Output is rolling-z-scored so the magnitude is comparable to the static
composite signal from ``combine.combine_signals``.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class WalkForwardResult:
    signal: pd.Series              # normalized prediction, comparable to static z-composite
    raw_prediction: pd.Series      # Ridge prediction in return units (untransformed)
    weights: pd.DataFrame          # one row per refit date: factor coefficients + intercept
    n_refits: int


def walk_forward_signal(
    z_factors: pd.DataFrame,
    target_returns: pd.Series,
    window_days: int = 504,
    refit_every: int = 21,
    alpha: float = 1.0,
    normalize_window: int = 252,
    min_train_obs: int | None = None,
) -> WalkForwardResult:
    """Ridge walk-forward predictor.

    Parameters
    ----------
    z_factors : DataFrame
        Standardized factor values (output of ``zscore_factors``).
    target_returns : Series
        Realised UC log-returns indexed by the **same** dates as the
        factors.  At fit time t, ``target_returns[t+1]`` (next day) is
        used as the regression target for ``z_factors[t]``.
    window_days : int
        Length of the rolling training window in trading days.
    refit_every : int
        Refit cadence.  21 ≈ monthly.  Smaller values track regime
        changes more closely but increase overfitting risk.
    alpha : float
        Ridge L2 penalty.
    normalize_window : int
        Rolling z-score window applied to the prediction so the output
        is in the same scale as the static composite signal.
    min_train_obs : int, optional
        Minimum non-NaN training observations to fit.  Defaults to
        ``window_days // 2``.

    Returns
    -------
    WalkForwardResult
    """
    from sklearn.linear_model import Ridge

    if min_train_obs is None:
        min_train_obs = window_days // 2

    # Align factors with the *next-day* return (shift target back by 1
    # so factors[t] is paired with returns[t+1])
    target_shifted = target_returns.shift(-1)
    df = pd.concat(
        [z_factors, target_shifted.rename("__y__")], axis=1
    ).sort_index()

    feature_cols = list(z_factors.columns)
    raw_prediction = pd.Series(np.nan, index=z_factors.index, name="raw_prediction")
    weights_log: list[dict] = []

    n = len(df)
    last_fit_pos = -1
    current_model: Ridge | None = None

    for pos in range(window_days, n):
        date = df.index[pos]

        # Refit cadence
        if last_fit_pos < 0 or (pos - last_fit_pos) >= refit_every:
            train = df.iloc[pos - window_days:pos].dropna(subset=feature_cols + ["__y__"])
            if len(train) < min_train_obs:
                continue
            X = train[feature_cols].values
            y = train["__y__"].values
            current_model = Ridge(alpha=alpha)
            current_model.fit(X, y)
            last_fit_pos = pos
            weights_log.append({
                "date": date,
                **{c: float(b) for c, b in zip(feature_cols, current_model.coef_)},
                "intercept": float(current_model.intercept_),
                "n_train": len(train),
            })

        if current_model is None:
            continue

        # Predict using *today's* factors (no look-ahead — factors[t] are
        # observable at close of t; the prediction targets return[t+1])
        row = df.iloc[pos][feature_cols]
        if row.isna().any():
            continue
        raw_prediction.iloc[pos] = float(current_model.predict(row.values.reshape(1, -1))[0])

    weights = (
        pd.DataFrame(weights_log).set_index("date").sort_index()
        if weights_log
        else pd.DataFrame(columns=feature_cols + ["intercept", "n_train"])
    )

    # Normalize so the output scale matches the static composite (~[-3, 3])
    mp = max(20, normalize_window // 4)
    mu = raw_prediction.rolling(normalize_window, min_periods=mp).mean()
    sd = raw_prediction.rolling(normalize_window, min_periods=mp).std()
    signal = (raw_prediction - mu) / sd.where(sd > 0)
    signal = signal.clip(-3.0, 3.0).rename("signal")

    logger.info(
        "Walk-forward Ridge: %d refits over %d days (window=%d, refit_every=%d, alpha=%.3f)",
        len(weights_log), n - window_days, window_days, refit_every, alpha,
    )

    return WalkForwardResult(
        signal=signal,
        raw_prediction=raw_prediction,
        weights=weights,
        n_refits=len(weights_log),
    )
