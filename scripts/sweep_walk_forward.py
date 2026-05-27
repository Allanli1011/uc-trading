"""Grid search over walk-forward Ridge hyperparameters.

Sweeps ``window_days × refit_every × alpha`` and evaluates each combination
on a fixed out-of-sample window so configs with longer warmup are not
penalised by leading flat days.

Outputs
-------
* ``output/sweep_walk_forward.csv``         — all combinations with metrics
* ``output/sweep_heatmap_window_*.png``     — Sharpe heat-maps (refit × alpha)
                                              per window length
* ``output/sweep_top_equity.png``           — equity curves of top-N configs
* console: top-10 table plus stability summary (1st half vs 2nd half Sharpe)

Usage::

    python scripts/sweep_walk_forward.py            # default grid + eval 2020+
    python scripts/sweep_walk_forward.py --eval-start 2021-01-01
    python scripts/sweep_walk_forward.py --top 15
"""
from __future__ import annotations

import argparse
import itertools
import logging
import sys
import time
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


# ---------------------------------------------------------------------------
# Default grid — modest size so a full sweep finishes in a few minutes
# ---------------------------------------------------------------------------
DEFAULT_GRID = {
    "window_days":  [252, 378, 504, 756, 1008],   # 12 / 18 / 24 / 36 / 48 months
    "refit_every":  [5, 21, 63, 126],              # weekly / monthly / quarterly / semi-annual
    "alpha":        [0.01, 0.1, 1.0, 10.0, 100.0],
}

DEFAULT_EVAL_START = "2020-01-01"
HALF_SPLIT = "2023-01-01"   # split point for first-half vs second-half Sharpe


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default=None)
    p.add_argument("--eval-start", default=DEFAULT_EVAL_START,
                   help=f"Start date for metric evaluation (default {DEFAULT_EVAL_START})")
    p.add_argument("--half-split", default=HALF_SPLIT,
                   help=f"Date splitting first/second halves (default {HALF_SPLIT})")
    p.add_argument("--top", type=int, default=10, help="Number of top configs to display")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--verbose", "-v", action="count", default=0)
    return p.parse_args()


def setup_logging(verbosity: int) -> None:
    level = logging.WARNING if verbosity == 0 else logging.INFO if verbosity == 1 else logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")


def _backtest_with_signal(
    composite: pd.Series, panel: pd.DataFrame, risk_cfg: dict, bt_cfg: dict,
) -> pd.DataFrame:
    """Replicates the full risk/backtest pipeline for one signal series."""
    position = signal_to_position(composite, style="proportional")
    sized = apply_vol_target(
        position, panel["uc_proxy"],
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
    return run_backtest(
        prices=panel["uc_proxy"], positions=sized,
        cost_bps=bt_cfg.get("cost_bps", 1.0),
        signal_lag_days=bt_cfg.get("signal_lag_days", 1),
        start=bt_cfg.get("start_date"),
    )


def _slice_metrics(bt: pd.DataFrame, start: str, end: str | None = None) -> dict:
    """Compute metrics on a date-sliced view of the backtest result."""
    view = bt[bt.index >= pd.Timestamp(start)]
    if end:
        view = view[view.index <= pd.Timestamp(end)]
    return compute_metrics(view)


def run_sweep(
    z_factors: pd.DataFrame,
    uc_log_ret: pd.Series,
    panel: pd.DataFrame,
    risk_cfg: dict,
    bt_cfg: dict,
    grid: dict,
    eval_start: str,
    half_split: str,
) -> tuple[pd.DataFrame, dict[tuple, pd.DataFrame]]:
    """Run grid and return (metrics_df, equity_curves_by_config)."""
    keys = list(grid.keys())
    values = list(grid.values())
    combos = list(itertools.product(*values))
    rows: list[dict] = []
    equities: dict[tuple, pd.Series] = {}

    log = logging.getLogger("sweep")
    log.warning("Running %d combinations...", len(combos))

    t_start = time.time()
    for i, combo in enumerate(combos, 1):
        params = dict(zip(keys, combo))
        wf = walk_forward_signal(z_factors, uc_log_ret, normalize_window=252, **params)
        bt = _backtest_with_signal(wf.signal, panel, risk_cfg, bt_cfg)

        m_full = _slice_metrics(bt, eval_start)
        m_first = _slice_metrics(bt, eval_start, half_split)
        m_second = _slice_metrics(bt, half_split)

        rows.append({
            **params,
            "n_refits": wf.n_refits,
            "sharpe": m_full["sharpe"],
            "ann_return": m_full["ann_return"],
            "ann_vol": m_full["ann_vol"],
            "max_drawdown": m_full["max_drawdown"],
            "calmar": m_full["calmar"],
            "turnover": m_full["avg_annual_turnover"],
            "sharpe_first": m_first["sharpe"],
            "sharpe_second": m_second["sharpe"],
        })
        equities[tuple(combo)] = bt[bt.index >= pd.Timestamp(eval_start)]["equity"]

        if i % 10 == 0 or i == len(combos):
            elapsed = time.time() - t_start
            log.warning("  %3d/%d  elapsed %.1fs  ETA %.1fs",
                        i, len(combos), elapsed, elapsed * (len(combos) - i) / i)

    df = pd.DataFrame(rows)
    return df, equities


def plot_heatmaps(df: pd.DataFrame, out_dir: Path) -> None:
    """One heatmap per window_days, showing Sharpe over refit × alpha."""
    windows = sorted(df["window_days"].unique())
    refits = sorted(df["refit_every"].unique())
    alphas = sorted(df["alpha"].unique())

    n = len(windows)
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 4.2 * rows), squeeze=False)
    vmin, vmax = df["sharpe"].min(), df["sharpe"].max()
    cmap = plt.get_cmap("RdYlGn")

    for i, w in enumerate(windows):
        ax = axes[i // cols][i % cols]
        sub = df[df["window_days"] == w]
        grid = sub.pivot(index="refit_every", columns="alpha", values="sharpe").reindex(
            index=refits, columns=alphas
        )
        im = ax.imshow(grid.values, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(alphas)))
        ax.set_xticklabels([f"{a:g}" for a in alphas])
        ax.set_yticks(range(len(refits)))
        ax.set_yticklabels(refits)
        ax.set_xlabel("alpha (Ridge L2)")
        ax.set_ylabel("refit_every (days)")
        ax.set_title(f"window_days = {w}")
        for ri, rfit in enumerate(refits):
            for ai, a in enumerate(alphas):
                v = grid.loc[rfit, a]
                if pd.notna(v):
                    ax.text(ai, ri, f"{v:.2f}", ha="center", va="center", fontsize=8)
    # Hide unused axes
    for j in range(len(windows), rows * cols):
        axes[j // cols][j % cols].set_visible(False)
    fig.suptitle("Walk-forward Sharpe — eval period only", y=1.005, fontsize=12)
    fig.colorbar(im, ax=axes, shrink=0.6, label="Sharpe")
    fig.savefig(out_dir / "sweep_heatmaps.png", bbox_inches="tight", dpi=140)
    plt.close(fig)


def plot_top_equities(
    df: pd.DataFrame, equities: dict[tuple, pd.Series], baseline_eq: pd.Series,
    top_n: int, out_dir: Path,
) -> None:
    top = df.nlargest(top_n, "sharpe")
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(baseline_eq.index, baseline_eq.values,
            label="Static baseline", color="k", linewidth=2.0)
    cmap = plt.get_cmap("viridis")
    for i, (_, row) in enumerate(top.iterrows()):
        key = (int(row["window_days"]), int(row["refit_every"]), float(row["alpha"]))
        eq = equities[key]
        ax.plot(eq.index, eq.values,
                label=f"w={key[0]} r={key[1]} a={key[2]:g}  Sh={row['sharpe']:.2f}",
                linewidth=1.1, alpha=0.85, color=cmap(i / max(top_n - 1, 1)))
    ax.set_title(f"Top-{top_n} walk-forward configs vs static baseline")
    ax.set_ylabel("Equity (×NAV, evaluation period only)")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out_dir / "sweep_top_equity.png", bbox_inches="tight", dpi=140)
    plt.close(fig)


def format_top_table(df: pd.DataFrame, top_n: int) -> str:
    top = df.nlargest(top_n, "sharpe")
    headers = ["window", "refit", "alpha", "Sharpe", "1stHalf", "2ndHalf",
               "AnnRet", "MaxDD", "Calmar", "Turn"]
    widths = [6, 5, 6, 6, 7, 7, 7, 7, 5, 5]
    lines = ["  " + "  ".join(h.ljust(w) for h, w in zip(headers, widths))]
    lines.append("  " + "  ".join("=" * w for w in widths))
    for _, r in top.iterrows():
        cells = [
            f"{int(r['window_days']):>5d} ",
            f"{int(r['refit_every']):>4d} ",
            f"{r['alpha']:>5.2g} ",
            f"{r['sharpe']:>5.2f} ",
            f"{r['sharpe_first']:>6.2f} ",
            f"{r['sharpe_second']:>6.2f} ",
            f"{r['ann_return']:>+6.2%} ",
            f"{r['max_drawdown']:>+6.2%} ",
            f"{r['calmar']:>4.2f} ",
            f"{r['turnover']:>4.0f}x",
        ]
        lines.append("  " + "  ".join(cells))
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    setup_logging(max(args.verbose, 1))
    log = logging.getLogger("sweep")

    cfg = load_config(args.config)
    out_dir = Path(args.output_dir) if args.output_dir else cfg.resolve(
        cfg.get("output", {}).get("dir", "output")
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    factor_cfg = cfg["factors"]
    risk_cfg = cfg["risk"]
    bt_cfg = cfg["backtest"]

    # Data + factors (load once, reuse for all configs)
    log.warning("Loading data + building factors…")
    raw = load_all(cfg)
    panel = align_and_clean(raw, start=cfg["data"]["start_date"], end=cfg["data"].get("end_date"))
    factors = build_factors(panel, factor_cfg)
    z = zscore_factors(factors, window=factor_cfg.get("zscore_window", 252))
    uc_log_ret = np.log(panel["uc_proxy"]).diff()

    # Static baseline for reference (on eval window)
    static_signal = combine_signals(z, factor_cfg)
    static_bt = _backtest_with_signal(static_signal, panel, risk_cfg, bt_cfg)
    static_eq = static_bt[static_bt.index >= pd.Timestamp(args.eval_start)]["equity"]
    static_eq = static_eq / static_eq.iloc[0]   # rebase to 1.0
    static_m = _slice_metrics(static_bt, args.eval_start)

    # Sweep
    sweep_df, equities = run_sweep(
        z, uc_log_ret, panel, risk_cfg, bt_cfg,
        DEFAULT_GRID, args.eval_start, args.half_split,
    )
    # Rebase equities to start at 1.0 within evaluation period for comparability
    equities = {k: (v / v.iloc[0]) for k, v in equities.items() if len(v) > 0}

    # Persist
    sweep_df.sort_values("sharpe", ascending=False).to_csv(
        out_dir / "sweep_walk_forward.csv", index=False
    )

    # Report
    print("\n" + "=" * 80)
    print(f"Walk-forward hyperparameter sweep — evaluated on {args.eval_start}+")
    print(f"Static baseline  Sharpe={static_m['sharpe']:.2f}  "
          f"AnnRet={static_m['ann_return']:+.2%}  "
          f"MDD={static_m['max_drawdown']:+.2%}  "
          f"Calmar={static_m['calmar']:.2f}")
    print("=" * 80)
    print(f"\nTop-{args.top} walk-forward configurations (sorted by full-period Sharpe):")
    print(format_top_table(sweep_df, args.top))

    # Stability summary
    stable = sweep_df.copy()
    stable["half_gap"] = (stable["sharpe_first"] - stable["sharpe_second"]).abs()
    stable_sorted = stable[stable["sharpe"] > stable["sharpe"].median()].nsmallest(args.top, "half_gap")
    print(f"\nMost stable configs (above-median Sharpe + smallest |1stHalf-2ndHalf|):")
    print(format_top_table(stable_sorted, args.top))

    print("\nSweep summary:")
    print(f"  Best Sharpe:        {sweep_df['sharpe'].max():.2f}")
    print(f"  Median Sharpe:      {sweep_df['sharpe'].median():.2f}")
    print(f"  Worst Sharpe:       {sweep_df['sharpe'].min():.2f}")
    print(f"  Default (504,21,1) Sharpe: {sweep_df[(sweep_df['window_days']==504)&(sweep_df['refit_every']==21)&(sweep_df['alpha']==1.0)]['sharpe'].iloc[0]:.2f}")
    print("=" * 80 + "\n")

    # Plots
    log.warning("Plotting…")
    plot_heatmaps(sweep_df, out_dir)
    plot_top_equities(sweep_df, equities, static_eq, args.top, out_dir)

    log.warning("Wrote %s", out_dir / "sweep_walk_forward.csv")
    log.warning("Wrote %s", out_dir / "sweep_heatmaps.png")
    log.warning("Wrote %s", out_dir / "sweep_top_equity.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
