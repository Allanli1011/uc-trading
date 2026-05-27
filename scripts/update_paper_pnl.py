"""Update the paper-trading PnL series from the signal history.

This script is meant to run **after** ``daily_signal.py`` each day.  It:

1. Reads ``signals/history.csv`` (the append-only log of past signals).
2. Pulls fresh UC prices (same loader stack as the backtest).
3. Builds a paper-trading PnL series by holding the signalled position on
   the *effective date* (one business day after the signal was generated).
4. Computes rolling performance metrics (Sharpe, MDD, etc.).
5. Writes machine-readable outputs (``paper_pnl.csv``, ``stats.json``) and
   a human-readable ``REPORT.md`` summarising the live track-record.

Idempotent — re-running on the same data yields the same outputs.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.backtest.metrics import compute_metrics  # noqa: E402
from src.config import load_config  # noqa: E402
from src.data import align_and_clean, load_all  # noqa: E402
from src.viz import plot_paper_track  # noqa: E402


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def build_paper_pnl(history: pd.DataFrame, uc_close: pd.Series, cost_bps: float) -> pd.DataFrame:
    """Replay the historical signals against realised UC prices.

    Convention:
        signal generated at the close of *as_of_date* sets the position
        held from the open of *effective_date* through to its close.  So
        the realised PnL on day D = position_target(signal[D-1bd]) × UC_return(D).
    """
    if history.empty:
        return pd.DataFrame()

    history = history.copy()
    history["effective_date"] = pd.to_datetime(history["effective_date"])
    sig_by_eff = history.set_index("effective_date")["position_target"]
    # Keep the most recent record per effective_date in case of duplicates
    sig_by_eff = sig_by_eff[~sig_by_eff.index.duplicated(keep="last")]

    df = pd.DataFrame(index=uc_close.index)
    df["uc_close"] = uc_close
    df["uc_return"] = uc_close.pct_change()
    df["position_target"] = sig_by_eff.reindex(df.index)
    # Once a signal is set, we hold it until the next signal
    df["position_realized"] = df["position_target"].ffill().fillna(0.0)

    first_signal = sig_by_eff.index.min()
    df = df[df.index >= first_signal].copy()

    df["turnover"] = df["position_realized"].diff().abs().fillna(df["position_realized"].abs())
    df["gross_pnl"] = df["position_realized"] * df["uc_return"]
    df["cost"] = df["turnover"] * cost_bps / 10_000.0
    df["net_pnl"] = df["gross_pnl"] - df["cost"]
    df["equity"] = (1.0 + df["net_pnl"].fillna(0.0)).cumprod()

    return df


def render_report(history: pd.DataFrame, pnl: pd.DataFrame, metrics: dict, cfg) -> str:
    """Render a short Markdown summary of the live paper track."""
    latest = history.sort_values("as_of_date").iloc[-1] if not history.empty else None
    factor_cfg = cfg["factors"]
    active_factors = sorted(
        n for n, p in factor_cfg.items()
        if isinstance(p, dict) and p.get("enabled", True)
    )

    # Empty-PnL case: still emit a useful report so the chart shows up.
    if pnl.empty:
        lines = [
            "# UC Paper-Trading Live Track",
            "",
            f"_Last update_: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}`",
            "",
            "> First signal recorded; the underlying close for its **effective**",
            "> day hasn't arrived yet, so there is no realised PnL to display.",
            "",
        ]
        if latest is not None:
            lines.extend([
                "## Latest signal",
                "",
                f"- **As-of close**: `{pd.Timestamp(latest['as_of_date']).date()}` (close = `{latest['uc_proxy_close']:.4f}`)",
                f"- **Effective trading day**: `{pd.Timestamp(latest['effective_date']).date()}`",
                f"- **Composite signal**: `{latest['composite_signal']:+.4f}`",
                f"- **Target position**: `{latest['position_target']:+.4f}`  "
                f"({'LONG' if latest['position_target'] > 0 else 'SHORT' if latest['position_target'] < 0 else 'FLAT'})",
                f"- **In market**: `{bool(latest.get('in_market', False))}`",
                "",
            ])
        lines.extend([
            "## Track-record chart",
            "",
            "![Live track](track.png)",
            "",
            "## Active factor set",
            "",
            ", ".join(f"`{f}`" for f in active_factors),
            "",
        ])
        return "\n".join(lines)

    cum_ret = pnl["equity"].iloc[-1] - 1.0
    best_day = pnl["net_pnl"].max() if not pnl["net_pnl"].dropna().empty else 0.0
    worst_day = pnl["net_pnl"].min() if not pnl["net_pnl"].dropna().empty else 0.0
    in_mkt = (pnl["position_realized"].abs() > 1e-9).mean()

    lines = [
        "# UC Paper-Trading Live Track",
        "",
        f"_Last update_: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}`",
        "",
        "## Latest signal",
        "",
        f"- **As-of close**: `{latest['as_of_date']}` (close = `{latest['uc_proxy_close']:.4f}`)",
        f"- **Effective trading day**: `{latest['effective_date']}`",
        f"- **Composite signal**: `{latest['composite_signal']:+.4f}`",
        f"- **Target position**: `{latest['position_target']:+.4f}`  "
        f"({'LONG' if latest['position_target'] > 0 else 'SHORT' if latest['position_target'] < 0 else 'FLAT'})",
        f"- **In market**: `{bool(latest.get('in_market', False))}`",
        f"- **Deadband**: threshold=`{latest.get('signal_threshold', 0)}`, "
        f"mode=`{latest.get('deadband_mode', 'n/a')}`",
        "",
        "## Live performance",
        "",
        f"- **Signals recorded**: {len(history)}",
        f"- **Trading days observed**: {len(pnl)} (since {pnl.index[0].date()})",
        f"- **Cumulative return**: `{cum_ret:+.2%}`",
        f"- **Annualised return**: `{metrics.get('ann_return', float('nan')):+.2%}`",
        f"- **Annualised volatility**: `{metrics.get('ann_vol', float('nan')):.2%}`",
        f"- **Sharpe ratio**: `{metrics.get('sharpe', float('nan')):.2f}`",
        f"- **Sortino ratio**: `{metrics.get('sortino', float('nan')):.2f}`",
        f"- **Max drawdown**: `{metrics.get('max_drawdown', float('nan')):+.2%}`",
        f"- **Calmar**: `{metrics.get('calmar', float('nan')):.2f}`",
        f"- **Win rate (non-flat days)**: `{metrics.get('win_rate', float('nan')):.1%}`",
        f"- **Best day**: `{best_day:+.4%}`",
        f"- **Worst day**: `{worst_day:+.4%}`",
        f"- **In-market fraction**: `{in_mkt:.1%}`",
        "",
        "## Active factor set",
        "",
        ", ".join(f"`{f}`" for f in active_factors),
        "",
        "## Track-record chart",
        "",
        "![Live track](track.png)",
        "",
        "## Files",
        "",
        "- `signals/history.csv` — append-only signal log",
        "- `signals/latest.json` — latest signal in pretty form",
        "- `signals/paper_pnl.csv` — realised daily PnL series",
        "- `signals/stats.json` — machine-readable performance metrics",
        "- `signals/track.png` — live equity / drawdown / position chart",
        "",
        "---",
        "",
        "_Paper-trading only. Uses `CNY=X` (in-shore) as a proxy for SGX UC futures; "
        "real-life UC PnL will differ by the CNY/CNH basis._",
    ]
    return "\n".join(lines)


def main() -> int:
    setup_logging()
    log = logging.getLogger("paper_pnl")

    cfg = load_config()
    sig_dir = PROJECT_ROOT / "signals"
    history_path = sig_dir / "history.csv"

    if not history_path.exists():
        log.warning("No history yet at %s; nothing to do", history_path)
        return 0

    history = pd.read_csv(history_path)
    history["as_of_date"] = pd.to_datetime(history["as_of_date"])
    history["effective_date"] = pd.to_datetime(history["effective_date"])
    log.info("Loaded %d historical signals", len(history))

    log.info("Fetching prices to realise PnL…")
    raw = load_all(cfg)
    panel = align_and_clean(
        raw,
        start=cfg["data"]["start_date"],
        end=cfg["data"].get("end_date"),
    )
    uc_close = panel["uc_proxy"]

    cost_bps = float(cfg["backtest"].get("cost_bps", 1.0))
    pnl = build_paper_pnl(history, uc_close, cost_bps=cost_bps)

    metrics: dict = {}
    if not pnl.empty:
        # compute_metrics needs a "net_return" column
        as_metric = pnl.rename(columns={"net_pnl": "net_return"})
        metrics = compute_metrics(as_metric)

    # Persist
    pnl_path = sig_dir / "paper_pnl.csv"
    stats_path = sig_dir / "stats.json"
    report_path = sig_dir / "REPORT.md"

    if not pnl.empty:
        pnl.to_csv(pnl_path)
        log.info("Wrote %s (%d rows)", pnl_path, len(pnl))

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    log.info("Wrote %s", stats_path)

    report = render_report(history, pnl, metrics, cfg)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    log.info("Wrote %s", report_path)

    # Visual track-record chart (also writes a placeholder if pnl is empty)
    track_path = sig_dir / "track.png"
    plot_paper_track(pnl, signals=history, out_path=track_path, metrics=metrics)
    log.info("Wrote %s", track_path)

    if not pnl.empty:
        log.info(
            "Track-record: %d days, equity %.4f, Sharpe %.2f, MDD %+.2%%",
            len(pnl), pnl["equity"].iloc[-1],
            metrics.get("sharpe", float("nan")),
            metrics.get("max_drawdown", float("nan")) * 100,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
