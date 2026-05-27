"""Sweep the signal deadband threshold for both static and walk-forward modes.

Answers: does sitting out when the composite signal is weak improve risk-
adjusted performance, and at what threshold is the trade-off best?

For each (threshold, deadband_mode) combination this:
  1. applies the deadband to the composite signal
  2. runs the full risk → backtest pipeline
  3. records Sharpe, MDD, Calmar, turnover and *in-market %*

Outputs
-------
* console: comparison table for static and walk-forward
* ``output/sweep_threshold.csv``      raw results
* ``output/sweep_threshold.png``      Sharpe / MDD / in-market% vs threshold

Usage::

    python scripts/sweep_threshold.py
    python scripts/sweep_threshold.py --thresholds 0,0.1,0.15,0.2,0.3,0.4,0.5
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.backtest import compute_metrics, run_backtest  # noqa: E402
from src.config import load_config  # noqa: E402
from src.data import align_and_clean, load_all  # noqa: E402
from src.features import build_factors  # noqa: E402
from src.risk import apply_vix_filter, apply_vol_target  # noqa: E402
from src.signals import combine_signals, walk_forward_signal, zscore_factors  # noqa: E402
from src.signals.combine import signal_to_position  # noqa: E402


DEFAULT_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
DEFAULT_MODES = ["hard", "soft"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default=None)
    p.add_argument("--thresholds", default=None,
                   help="Comma-separated list of thresholds (default: %s)"
                        % ",".join(str(t) for t in DEFAULT_THRESHOLDS))
    p.add_argument("--modes", default="hard,soft",
                   help="Comma-separated deadband modes to evaluate")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--verbose", "-v", action="count", default=0)
    return p.parse_args()


def setup_logging(v: int) -> None:
    level = logging.WARNING if v == 0 else logging.INFO if v == 1 else logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")


def _run_one(signal, panel, risk_cfg, bt_cfg, threshold, mode):
    """Apply deadband -> risk overlay -> backtest -> metrics + in-market %."""
    pos = signal_to_position(signal, style="proportional",
                             threshold=threshold, deadband_mode=mode)
    sized = apply_vol_target(
        pos, panel["uc_proxy"],
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
    bt = run_backtest(
        prices=panel["uc_proxy"], positions=sized,
        cost_bps=bt_cfg.get("cost_bps", 1.0),
        signal_lag_days=bt_cfg.get("signal_lag_days", 1),
        start=bt_cfg.get("start_date"),
    )
    m = compute_metrics(bt)
    # In-market fraction: days where realised position is non-zero
    realised = bt["position"]
    in_market = float((realised.abs() > 1e-9).mean())
    m["in_market_pct"] = in_market
    m["avg_abs_position"] = float(realised.abs().mean())
    return m


def _format_table(df: pd.DataFrame, title: str) -> str:
    headers = ["thr", "mode", "Sharpe", "AnnRet", "MaxDD", "Calmar", "Turn", "InMkt%", "AvgPos"]
    widths = [5, 5, 6, 7, 7, 5, 5, 6, 6]
    lines = [f"\n{title}",
             "  " + "  ".join(h.ljust(w) for h, w in zip(headers, widths)),
             "  " + "  ".join("=" * w for w in widths)]
    for _, r in df.iterrows():
        cells = [
            f"{r['threshold']:>4.2f} ",
            f"{r['mode']:>4s} ",
            f"{r['sharpe']:>5.2f} ",
            f"{r['ann_return']:>+6.2%} ",
            f"{r['max_drawdown']:>+6.2%} ",
            f"{r['calmar']:>4.2f} ",
            f"{r['avg_annual_turnover']:>3.0f}x ",
            f"{r['in_market_pct']:>5.1%} ",
            f"{r['avg_abs_position']:>5.2f} ",
        ]
        lines.append("  " + "  ".join(cells))
    return "\n".join(lines)


def plot_sweep(static_df, wf_df, out_path: Path):
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5))

    panels = [
        ("sharpe",         "Sharpe",          axes[0][0]),
        ("max_drawdown",   "Max Drawdown",    axes[0][1]),
        ("in_market_pct",  "In-Market %",     axes[1][0]),
        ("avg_annual_turnover", "Avg Annual Turnover", axes[1][1]),
    ]
    colors = {"hard": "#1f77b4", "soft": "#ff7f0e"}
    line_styles = {"static": "-", "wf": "--"}

    for key, label, ax in panels:
        for src_name, df in [("static", static_df), ("wf", wf_df)]:
            if df is None:
                continue
            for mode in df["mode"].unique():
                sub = df[df["mode"] == mode].sort_values("threshold")
                ax.plot(sub["threshold"], sub[key],
                        marker="o", linestyle=line_styles[src_name],
                        color=colors[mode],
                        label=f"{src_name}/{mode}")
        ax.set_xlabel("threshold")
        ax.set_ylabel(label)
        ax.set_title(label + " vs threshold")
        if key in ("in_market_pct",):
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
        if key in ("max_drawdown",):
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1%}"))
        ax.legend(fontsize=8)

    fig.suptitle("Deadband threshold sweep — static and walk-forward signals", y=1.005)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=140)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    setup_logging(max(args.verbose, 1))
    log = logging.getLogger("sweep_threshold")

    cfg = load_config(args.config)
    out_dir = Path(args.output_dir) if args.output_dir else cfg.resolve(
        cfg.get("output", {}).get("dir", "output")
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    factor_cfg = cfg["factors"]
    risk_cfg = cfg["risk"]
    bt_cfg = cfg["backtest"]
    signal_cfg = cfg.get("signal", {}) or {}
    wf_enabled = bool(signal_cfg.get("walk_forward", {}).get("enabled", False))

    if args.thresholds:
        thresholds = [float(x) for x in args.thresholds.split(",")]
    else:
        thresholds = DEFAULT_THRESHOLDS
    modes = [m.strip() for m in args.modes.split(",")]

    log.warning("Loading data + factors…")
    raw = load_all(cfg)
    panel = align_and_clean(raw, start=cfg["data"]["start_date"], end=cfg["data"].get("end_date"))
    factors = build_factors(panel, factor_cfg)
    z = zscore_factors(factors, window=factor_cfg.get("zscore_window", 252))

    static_signal = combine_signals(z, factor_cfg)

    wf_signal = None
    if wf_enabled:
        wf_cfg = signal_cfg["walk_forward"]
        uc_log_ret = np.log(panel["uc_proxy"]).diff()
        wf_result = walk_forward_signal(
            z, uc_log_ret,
            window_days=wf_cfg.get("window_days", 504),
            refit_every=wf_cfg.get("refit_every", 21),
            alpha=wf_cfg.get("alpha", 1.0),
            normalize_window=wf_cfg.get("normalize_window", 252),
        )
        wf_signal = wf_result.signal

    static_rows, wf_rows = [], []
    log.warning("Sweeping %d thresholds × %d modes = %d configs per signal",
                len(thresholds), len(modes), len(thresholds) * len(modes))

    for th in thresholds:
        for mode in modes:
            if th == 0.0 and mode == "soft":
                continue  # equivalent to th=0,hard — skip duplicate
            m_static = _run_one(static_signal, panel, risk_cfg, bt_cfg, th, mode)
            static_rows.append({"threshold": th, "mode": mode, **m_static})
            if wf_signal is not None:
                m_wf = _run_one(wf_signal, panel, risk_cfg, bt_cfg, th, mode)
                wf_rows.append({"threshold": th, "mode": mode, **m_wf})

    static_df = pd.DataFrame(static_rows).sort_values(["mode", "threshold"])
    wf_df = pd.DataFrame(wf_rows).sort_values(["mode", "threshold"]) if wf_rows else None

    # Persist
    out_csv = out_dir / "sweep_threshold.csv"
    combined = pd.concat(
        [static_df.assign(signal="static"),
         (wf_df.assign(signal="wf") if wf_df is not None else pd.DataFrame())],
        ignore_index=True,
    )
    combined.to_csv(out_csv, index=False)

    # Report
    print("=" * 78)
    print("Signal-deadband threshold sweep")
    print(f"  factor set: {[c for c in z.columns]}")
    print(f"  thresholds: {thresholds}")
    print(f"  modes:      {modes}")
    print("=" * 78)
    print(_format_table(static_df, "STATIC composite — vary threshold"))
    if wf_df is not None:
        print(_format_table(wf_df, "WALK-FORWARD composite — vary threshold"))
    print("=" * 78)

    # Pick out the best Sharpe and best Calmar per signal/mode
    def _best(df, key):
        return df.sort_values(key, ascending=(key == "max_drawdown")).iloc[0]

    print("\nBest configurations:")
    for src_name, df in [("static", static_df), ("wf", wf_df)]:
        if df is None or len(df) == 0:
            continue
        bs = _best(df, "sharpe")
        bc = _best(df, "calmar")
        print(f"  [{src_name}]  best Sharpe  th={bs['threshold']:.2f}/{bs['mode']}: "
              f"Sh={bs['sharpe']:.2f}  MDD={bs['max_drawdown']:+.2%}  "
              f"InMkt={bs['in_market_pct']:.0%}")
        print(f"  [{src_name}]  best Calmar  th={bc['threshold']:.2f}/{bc['mode']}: "
              f"Sh={bc['sharpe']:.2f}  Cal={bc['calmar']:.2f}  "
              f"MDD={bc['max_drawdown']:+.2%}  InMkt={bc['in_market_pct']:.0%}")

    plot_sweep(static_df, wf_df, out_dir / "sweep_threshold.png")
    log.warning("Wrote %s", out_csv)
    log.warning("Wrote %s", out_dir / "sweep_threshold.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
