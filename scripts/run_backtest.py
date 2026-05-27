"""End-to-end pipeline: data → factors → signal(s) → backtest → report.

Runs up to three backtests in one pass for comparison:

* **static**         — factor weights from ``config.yaml`` (baseline).
* **walk_forward**   — adaptive weights from rolling Ridge regression.
* **attribution**    — one backtest per individual factor.

Use ``signal.mode`` in the config to select which backtest is *primary*
(determines the saved equity report).  Other modes are still computed
when enabled and shown in the comparison table.

Examples::

    python scripts/run_backtest.py                # use config defaults
    python scripts/run_backtest.py --no-cache     # force refetch
    python scripts/run_backtest.py --no-plots
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.backtest import compute_metrics, run_backtest  # noqa: E402
from src.backtest.metrics import format_metrics  # noqa: E402
from src.config import load_config  # noqa: E402
from src.data import align_and_clean, load_all  # noqa: E402
from src.features import build_factors  # noqa: E402
from src.risk import apply_vix_filter, apply_vol_target  # noqa: E402
from src.signals import (  # noqa: E402
    attribution_table,
    combine_signals,
    format_attribution_table,
    per_factor_backtest,
    walk_forward_signal,
    zscore_factors,
)
from src.signals.combine import signal_to_position  # noqa: E402
from src.viz import plot_backtest_report  # noqa: E402
from src.viz.plots import (  # noqa: E402
    plot_attribution_equity,
    plot_walk_forward_weights,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default=None, help="Path to config.yaml")
    p.add_argument("--no-cache", action="store_true", help="Force refetch all data")
    p.add_argument("--no-plots", action="store_true", help="Skip plot generation")
    p.add_argument("--output-dir", default=None, help="Override config output dir")
    p.add_argument("--verbose", "-v", action="count", default=0)
    return p.parse_args()


def setup_logging(verbosity: int) -> None:
    level = logging.WARNING if verbosity == 0 else logging.INFO if verbosity == 1 else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _apply_risk_overlays(raw_position: pd.Series, panel: pd.DataFrame, risk_cfg: dict) -> pd.Series:
    sized = apply_vol_target(
        raw_position,
        panel["uc_proxy"],
        target_annual=risk_cfg["vol_target_annual"],
        lookback=risk_cfg.get("vol_lookback", 60),
        max_gross=risk_cfg.get("max_gross_position", 1.0),
    )
    if "vix" in panel.columns:
        sized = apply_vix_filter(
            sized, panel["vix"],
            threshold=risk_cfg.get("vix_filter_threshold", 30.0),
            filter_scale=risk_cfg.get("vix_filter_scale", 0.5),
        )
    return sized


def _full_pipeline(
    composite: pd.Series,
    panel: pd.DataFrame,
    risk_cfg: dict,
    bt_cfg: dict,
    threshold: float = 0.0,
    deadband_mode: str = "hard",
) -> tuple[pd.DataFrame, dict]:
    position = signal_to_position(
        composite,
        style="proportional",
        threshold=threshold,
        deadband_mode=deadband_mode,
    )
    sized = _apply_risk_overlays(position, panel, risk_cfg)
    bt = run_backtest(
        prices=panel["uc_proxy"],
        positions=sized,
        cost_bps=bt_cfg.get("cost_bps", 1.0),
        signal_lag_days=bt_cfg.get("signal_lag_days", 1),
        start=bt_cfg.get("start_date"),
    )
    return bt, compute_metrics(bt)


def _format_comparison(rows: list[dict]) -> str:
    headers = ["Mode", "Sharpe", "AnnRet", "AnnVol", "MaxDD", "Calmar", "WinRate", "Turnover"]
    widths = [22, 6, 7, 6, 7, 5, 5, 7]
    lines = ["  " + "  ".join(h.ljust(w) for h, w in zip(headers, widths))]
    lines.append("  " + "  ".join("=" * w for w in widths))
    for r in rows:
        m = r["metrics"]
        cells = [
            r["name"].ljust(22),
            f"{m['sharpe']:>6.2f}",
            f"{m['ann_return']:>+7.2%}",
            f"{m['ann_vol']:>6.2%}",
            f"{m['max_drawdown']:>+7.2%}",
            f"{m['calmar']:>5.2f}",
            f"{m['win_rate']:>5.1%}",
            f"{m['avg_annual_turnover']:>6.1f}x",
        ]
        lines.append("  " + "  ".join(cells))
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    setup_logging(max(args.verbose, 1))
    log = logging.getLogger("run_backtest")

    cfg = load_config(args.config)
    if args.no_cache:
        cfg.raw.setdefault("data", {})["use_cache"] = False

    out_dir = Path(args.output_dir) if args.output_dir else cfg.resolve(
        cfg.get("output", {}).get("dir", "output")
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    factor_cfg = cfg["factors"]
    risk_cfg = cfg["risk"]
    bt_cfg = cfg["backtest"]
    signal_cfg = cfg.get("signal", {}) or {}
    attr_cfg = cfg.get("attribution", {}) or {}

    # ------------------------------------------------------------------
    # 1. Data
    # ------------------------------------------------------------------
    log.info("Loading data…")
    raw = load_all(cfg)
    panel = align_and_clean(
        raw,
        start=cfg["data"]["start_date"],
        end=cfg["data"].get("end_date"),
    )

    # ------------------------------------------------------------------
    # 2. Factors + z-score
    # ------------------------------------------------------------------
    log.info("Building factors…")
    factors = build_factors(panel, factor_cfg)
    z = zscore_factors(factors, window=factor_cfg.get("zscore_window", 252))

    # ------------------------------------------------------------------
    # 3. Static composite (always runs)
    # ------------------------------------------------------------------
    log.info("Running STATIC backtest…")
    static_signal = combine_signals(z, factor_cfg)
    sig_threshold = float(signal_cfg.get("threshold", 0.0))
    sig_mode = signal_cfg.get("deadband_mode", "hard")
    if sig_threshold > 0:
        log.info("Applying signal deadband threshold=%.2f mode=%s",
                 sig_threshold, sig_mode)
    static_bt, static_metrics = _full_pipeline(
        static_signal, panel, risk_cfg, bt_cfg,
        threshold=sig_threshold, deadband_mode=sig_mode,
    )

    # ------------------------------------------------------------------
    # 4. Walk-forward Ridge (optional)
    # ------------------------------------------------------------------
    wf_bt = None
    wf_metrics = None
    wf_weights = None
    wf_enabled = bool(signal_cfg.get("walk_forward", {}).get("enabled", False))
    if wf_enabled:
        log.info("Running WALK-FORWARD backtest…")
        wf_cfg = signal_cfg["walk_forward"]
        # UC log returns as target
        uc_log_ret = np.log(panel["uc_proxy"]).diff()
        wf_result = walk_forward_signal(
            z, uc_log_ret,
            window_days=wf_cfg.get("window_days", 504),
            refit_every=wf_cfg.get("refit_every", 21),
            alpha=wf_cfg.get("alpha", 1.0),
            normalize_window=wf_cfg.get("normalize_window", 252),
        )
        wf_bt, wf_metrics = _full_pipeline(
            wf_result.signal, panel, risk_cfg, bt_cfg,
            threshold=sig_threshold, deadband_mode=sig_mode,
        )
        wf_weights = wf_result.weights

    # ------------------------------------------------------------------
    # 5. Per-factor attribution (optional)
    # ------------------------------------------------------------------
    attr_results = None
    attr_tbl = None
    if attr_cfg.get("enabled", False):
        log.info("Running per-factor ATTRIBUTION…")
        attr_results = per_factor_backtest(z, panel, factor_cfg, risk_cfg, bt_cfg)
        attr_tbl = attribution_table(attr_results)

    # ------------------------------------------------------------------
    # 6. Comparison summary
    # ------------------------------------------------------------------
    comparison = [{"name": "Static (config weights)", "metrics": static_metrics}]
    if wf_metrics is not None:
        comparison.append({"name": "Walk-forward Ridge", "metrics": wf_metrics})

    print("\n" + "=" * 80)
    print("UC Macro Factor Strategy — Backtest Summary")
    print("=" * 80)
    print(_format_comparison(comparison))

    if attr_tbl is not None:
        print("\nPer-factor attribution (single-factor backtests, sorted by Sharpe):")
        print(format_attribution_table(attr_tbl))

    primary_mode = signal_cfg.get("mode", "static")
    primary_bt = wf_bt if primary_mode == "walk_forward" and wf_bt is not None else static_bt
    primary_metrics = wf_metrics if primary_mode == "walk_forward" and wf_metrics is not None else static_metrics
    print(f"\nPrimary mode for chart pack: {primary_mode}")
    print("Detailed metrics for primary mode:")
    print(format_metrics(primary_metrics))
    print("=" * 80 + "\n")

    # ------------------------------------------------------------------
    # 7. Persist artefacts
    # ------------------------------------------------------------------
    if cfg.get("output", {}).get("save_trades", True):
        static_bt.to_csv(out_dir / "backtest_static.csv")
        if wf_bt is not None:
            wf_bt.to_csv(out_dir / "backtest_walk_forward.csv")
            wf_weights.to_csv(out_dir / "walk_forward_weights.csv")
        if attr_tbl is not None:
            attr_tbl.to_csv(out_dir / "attribution_metrics.csv")
            for name, res in attr_results.items():
                res["backtest"][["price", "position", "net_return", "equity"]].to_csv(
                    out_dir / f"attribution_{name}.csv"
                )
        pd.concat({"raw": factors, "z": z}, axis=1).to_csv(out_dir / "factors.csv")
        pd.Series(primary_metrics).to_csv(out_dir / "metrics_primary.csv", header=["value"])
        log.info("Wrote CSV artefacts to %s", out_dir)

    if not args.no_plots and cfg.get("output", {}).get("save_plots", True):
        plot_backtest_report(primary_bt, z_factors=z, out_dir=out_dir)
        if attr_results is not None:
            plot_attribution_equity(attr_results, static_bt, wf_bt, out_dir=out_dir)
        if wf_weights is not None and not wf_weights.empty:
            plot_walk_forward_weights(wf_weights, out_dir=out_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
