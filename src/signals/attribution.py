"""Per-factor performance attribution.

For every standardized factor we run the *same* downstream pipeline
(``signal -> vol-target -> VIX filter -> backtest``) using only that
factor as the composite signal.  This isolates each factor's
contribution to risk-adjusted PnL and exposes which inputs are real
alpha versus noise riding on the others.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.backtest.engine import run_backtest
from src.backtest.metrics import compute_metrics
from src.risk.sizing import apply_vix_filter, apply_vol_target

logger = logging.getLogger(__name__)


def per_factor_backtest(
    z_factors: pd.DataFrame,
    panel: pd.DataFrame,
    factor_config: dict,
    risk_config: dict,
    backtest_config: dict,
) -> dict[str, dict]:
    """Run a single-factor backtest for every column of ``z_factors``.

    Direction is taken from ``factor_config[name]['weight']`` (positive or
    negative) so each isolated signal points the economically-expected way.

    Returns
    -------
    dict
        ``{factor_name: {"metrics": dict, "backtest": DataFrame}}``
    """
    results: dict[str, dict] = {}
    uc_prices = panel["uc_proxy"]
    vix = panel["vix"] if "vix" in panel.columns else None

    for name in z_factors.columns:
        params = factor_config.get(name, {})
        if not isinstance(params, dict):
            continue
        weight = float(params.get("weight", 1.0))
        sign = np.sign(weight) if weight != 0 else 1.0

        # Use unit-magnitude signal, sign carries direction
        raw_signal = z_factors[name] * sign
        position = raw_signal.clip(-1.0, 1.0).rename("position_raw")

        sized = apply_vol_target(
            position,
            uc_prices,
            target_annual=risk_config["vol_target_annual"],
            lookback=risk_config.get("vol_lookback", 60),
            max_gross=risk_config.get("max_gross_position", 1.0),
        )
        if vix is not None:
            sized = apply_vix_filter(
                sized,
                vix,
                threshold=risk_config.get("vix_filter_threshold", 30.0),
                filter_scale=risk_config.get("vix_filter_scale", 0.5),
            )

        bt = run_backtest(
            prices=uc_prices,
            positions=sized,
            cost_bps=backtest_config.get("cost_bps", 1.0),
            signal_lag_days=backtest_config.get("signal_lag_days", 1),
            start=backtest_config.get("start_date"),
        )
        metrics = compute_metrics(bt)
        results[name] = {"metrics": metrics, "backtest": bt}

        logger.info(
            "Factor %-22s Sharpe=%.2f  AnnRet=%+.2f%%  MDD=%+.2f%%",
            name, metrics["sharpe"],
            metrics["ann_return"] * 100, metrics["max_drawdown"] * 100,
        )

    return results


def attribution_table(per_factor: dict[str, dict]) -> pd.DataFrame:
    """Flatten attribution results to a metrics table sorted by Sharpe."""
    rows = []
    for name, res in per_factor.items():
        m = res["metrics"]
        rows.append({
            "factor": name,
            "sharpe": m["sharpe"],
            "ann_return": m["ann_return"],
            "ann_vol": m["ann_vol"],
            "max_drawdown": m["max_drawdown"],
            "calmar": m["calmar"],
            "win_rate": m["win_rate"],
            "turnover": m["avg_annual_turnover"],
        })
    table = pd.DataFrame(rows).set_index("factor")
    table = table.sort_values("sharpe", ascending=False)
    return table


def format_attribution_table(table: pd.DataFrame) -> str:
    """Pretty print as monospaced table."""
    fmt = {
        "sharpe": "{:>6.2f}",
        "ann_return": "{:>+7.2%}",
        "ann_vol": "{:>6.2%}",
        "max_drawdown": "{:>+7.2%}",
        "calmar": "{:>5.2f}",
        "win_rate": "{:>5.1%}",
        "turnover": "{:>6.1f}x",
    }
    headers = ["Factor", "Sharpe", "AnnRet", "AnnVol", "MaxDD", "Calmar", "WinRate", "Turnover"]
    widths = [22, 6, 7, 6, 7, 5, 5, 7]
    lines = ["  " + "  ".join(h.ljust(w) for h, w in zip(headers, widths))]
    lines.append("  " + "  ".join("-" * w for w in widths))
    for name, row in table.iterrows():
        cells = [
            name.ljust(22),
            fmt["sharpe"].format(row["sharpe"]),
            fmt["ann_return"].format(row["ann_return"]),
            fmt["ann_vol"].format(row["ann_vol"]),
            fmt["max_drawdown"].format(row["max_drawdown"]),
            fmt["calmar"].format(row["calmar"]),
            fmt["win_rate"].format(row["win_rate"]),
            fmt["turnover"].format(row["turnover"]),
        ]
        lines.append("  " + "  ".join(cells))
    return "\n".join(lines)
