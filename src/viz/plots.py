"""Backtest visualization (matplotlib only — no plotly dependency)."""
from __future__ import annotations

import logging
import os
from pathlib import Path

import matplotlib

# Use a non-interactive backend so the module works in CI / headless runners.
# Honour an explicit MPLBACKEND if the caller has set one.
if not os.environ.get("MPLBACKEND"):
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

logger = logging.getLogger(__name__)

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 140,
    "font.size": 9,
    "axes.grid": True,
    "grid.alpha": 0.3,
})


def _save_or_show(fig, out_path: Path | None, name: str) -> None:
    if out_path is None:
        plt.show()
        plt.close(fig)
        return
    out_path.mkdir(parents=True, exist_ok=True)
    p = out_path / f"{name}.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", p)


def plot_equity_and_drawdown(backtest: pd.DataFrame, ax_eq=None, ax_dd=None):
    if ax_eq is None or ax_dd is None:
        fig, (ax_eq, ax_dd) = plt.subplots(
            2, 1, sharex=True, figsize=(11, 5),
            gridspec_kw={"height_ratios": [2.5, 1]},
        )
    else:
        fig = ax_eq.figure

    equity = backtest["equity"]
    ax_eq.plot(equity.index, equity.values, color="#1f77b4", linewidth=1.4)
    ax_eq.set_ylabel("Equity (×NAV)")
    ax_eq.set_title("Strategy Equity Curve")

    peak = equity.cummax()
    dd = equity / peak - 1.0
    ax_dd.fill_between(dd.index, dd.values, 0, color="#d62728", alpha=0.5)
    ax_dd.set_ylabel("Drawdown")
    ax_dd.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    return fig


def plot_position(backtest: pd.DataFrame, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 2.5))
    else:
        fig = ax.figure
    pos = backtest["position"]
    ax.fill_between(pos.index, pos.values, 0, where=pos > 0, color="#2ca02c", alpha=0.5, label="Long")
    ax.fill_between(pos.index, pos.values, 0, where=pos < 0, color="#d62728", alpha=0.5, label="Short")
    ax.axhline(0, color="k", linewidth=0.6)
    ax.set_ylabel("Position")
    ax.set_title("Position over time")
    ax.legend(loc="upper right", fontsize=8)
    return fig


def plot_factor_zscores(z_factors: pd.DataFrame, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 3.5))
    else:
        fig = ax.figure
    for col in z_factors.columns:
        ax.plot(z_factors.index, z_factors[col].values, label=col, linewidth=0.9, alpha=0.85)
    ax.axhline(0, color="k", linewidth=0.5)
    ax.set_ylabel("z-score")
    ax.set_title("Factor z-scores")
    ax.legend(loc="upper left", fontsize=7, ncol=3)
    return fig


def plot_monthly_heatmap(backtest: pd.DataFrame, ax=None):
    """Year × month heatmap of monthly net returns."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 3.5))
    else:
        fig = ax.figure
    rets = backtest["net_return"].dropna()
    if rets.empty:
        return fig
    monthly = (1 + rets).resample("ME").prod() - 1
    table = (
        monthly.to_frame("ret")
        .assign(year=lambda d: d.index.year, month=lambda d: d.index.month)
        .pivot(index="year", columns="month", values="ret")
    )
    table = table.reindex(columns=range(1, 13))

    im = ax.imshow(table.values, cmap="RdYlGn", aspect="auto", vmin=-0.05, vmax=0.05)
    ax.set_xticks(range(12))
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Monthly returns (%)")
    fig.colorbar(im, ax=ax, format=plt.FuncFormatter(lambda x, _: f"{x:.1%}"), shrink=0.7)
    # Annotate cells
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            v = table.values[i, j]
            if pd.notna(v):
                ax.text(j, i, f"{v*100:.1f}", ha="center", va="center",
                        fontsize=7, color="black")
    return fig


def plot_backtest_report(
    backtest: pd.DataFrame,
    z_factors: pd.DataFrame | None = None,
    out_dir: Path | None = None,
) -> None:
    """Generate the full chart pack: equity, drawdown, position, factors, heatmap."""
    fig, axes = plt.subplots(
        4, 1, figsize=(11, 13),
        gridspec_kw={"height_ratios": [2.5, 1, 1.5, 1.5]},
    )
    plot_equity_and_drawdown(backtest, ax_eq=axes[0], ax_dd=axes[1])
    plot_position(backtest, ax=axes[2])
    if z_factors is not None and not z_factors.empty:
        plot_factor_zscores(z_factors, ax=axes[3])
    else:
        axes[3].set_visible(False)
    fig.tight_layout()
    _save_or_show(fig, out_dir, "report_main")

    fig2, ax = plt.subplots(figsize=(11, 4.5))
    plot_monthly_heatmap(backtest, ax=ax)
    fig2.tight_layout()
    _save_or_show(fig2, out_dir, "monthly_heatmap")


def plot_attribution_equity(
    attribution: dict[str, dict],
    static_backtest: pd.DataFrame,
    wf_backtest: pd.DataFrame | None = None,
    out_dir: Path | None = None,
) -> None:
    """Overlay equity curves for every single-factor backtest plus composites.

    Composites (static / walk-forward) are drawn thick; single-factor lines
    are thin so the composite advantage is visible.
    """
    fig, ax = plt.subplots(figsize=(11, 5.5))

    # Composites first (thick)
    ax.plot(
        static_backtest.index, static_backtest["equity"],
        label="Static composite", linewidth=2.2, color="#1f77b4",
    )
    if wf_backtest is not None:
        ax.plot(
            wf_backtest.index, wf_backtest["equity"],
            label="Walk-forward Ridge", linewidth=2.2, color="#d62728",
        )

    # Single-factor curves (thin)
    cmap = plt.get_cmap("tab10")
    for i, (name, res) in enumerate(attribution.items()):
        eq = res["backtest"]["equity"]
        sr = res["metrics"]["sharpe"]
        ax.plot(
            eq.index, eq.values,
            label=f"{name} (Sh={sr:.2f})",
            linewidth=0.9, alpha=0.75, color=cmap((i + 2) % 10),
        )

    ax.set_title("Equity curves — composite vs single-factor attribution")
    ax.set_ylabel("Equity (×NAV)")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    fig.tight_layout()
    _save_or_show(fig, out_dir, "attribution_equity")


def plot_walk_forward_weights(
    weights: pd.DataFrame, out_dir: Path | None = None
) -> None:
    """Plot Ridge regression coefficients over time."""
    factor_cols = [c for c in weights.columns if c not in {"intercept", "n_train"}]
    if not factor_cols:
        return

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for col in factor_cols:
        ax.plot(weights.index, weights[col].values, label=col, linewidth=1.1, alpha=0.9)
    ax.axhline(0, color="k", linewidth=0.6)
    ax.set_title("Walk-forward Ridge — factor coefficients over time")
    ax.set_ylabel("Coefficient")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    fig.tight_layout()
    _save_or_show(fig, out_dir, "walk_forward_weights")


# ---------------------------------------------------------------------------
# Paper-trading track-record chart (used by scripts/update_paper_pnl.py)
# ---------------------------------------------------------------------------
def _placeholder_chart(out_path: Path, message: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.text(0.5, 0.5, message, ha="center", va="center",
            fontsize=14, transform=ax.transAxes, color="#555555")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=140)
    plt.close(fig)
    logger.info("Saved placeholder chart to %s", out_path)


def plot_paper_track(
    pnl: pd.DataFrame,
    signals: pd.DataFrame | None = None,
    out_path: Path | None = None,
    metrics: dict | None = None,
) -> None:
    """3-panel live track-record chart: equity / drawdown / position.

    Parameters
    ----------
    pnl : DataFrame
        Output of ``scripts.update_paper_pnl.build_paper_pnl``.  Indexed by
        date, must contain columns ``equity``, ``net_pnl``,
        ``position_realized``.
    signals : DataFrame, optional
        Signal history (one row per as-of date).  If given, vertical
        markers are drawn at each signal-generation day on the position
        panel.
    out_path : Path
        Full path to the output PNG (e.g. ``signals/track.png``).
    metrics : dict, optional
        Pre-computed metrics dict; if given, key stats are stamped on the
        chart as an annotation.
    """
    if out_path is None:
        raise ValueError("out_path is required")
    out_path = Path(out_path)

    # Handle empty / too-short cases gracefully so the workflow can still
    # commit a (small) chart on day 1.
    if pnl is None or pnl.empty:
        _placeholder_chart(
            out_path,
            "Live track starts after the first signal's effective day.\n"
            "Come back tomorrow.",
        )
        return
    valid = pnl["net_pnl"].dropna()
    if len(valid) < 1:
        _placeholder_chart(
            out_path,
            "First signal recorded — waiting for the underlying close\n"
            "to realise day-1 PnL.",
        )
        return

    fig, axes = plt.subplots(
        3, 1, sharex=True, figsize=(11, 8.5),
        gridspec_kw={"height_ratios": [2.6, 1.0, 1.4]},
    )

    # --- Equity --------------------------------------------------------
    ax_eq = axes[0]
    equity = pnl["equity"]
    ax_eq.plot(equity.index, equity.values, color="#1f77b4", linewidth=1.6)
    ax_eq.scatter(equity.index, equity.values, s=18, color="#1f77b4", zorder=3,
                  edgecolor="white", linewidth=0.6)
    ax_eq.axhline(1.0, color="k", linewidth=0.6, linestyle="--", alpha=0.4)
    ax_eq.set_ylabel("Equity (×NAV)")
    ax_eq.set_title(f"UC paper-trading track — {len(pnl)} day(s) since "
                    f"{pnl.index[0].date()}")

    # Annotate latest equity
    last_eq = equity.iloc[-1]
    ax_eq.annotate(
        f"{last_eq:.4f}\n({(last_eq - 1) * 100:+.2f}%)",
        xy=(equity.index[-1], last_eq),
        xytext=(8, 8), textcoords="offset points",
        fontsize=9, color="#1f77b4",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#1f77b4", alpha=0.85),
    )

    # Stamp metrics in upper-left
    if metrics:
        stamp = (
            f"Days: {len(pnl)}\n"
            f"AnnRet: {metrics.get('ann_return', float('nan')):+.2%}\n"
            f"AnnVol: {metrics.get('ann_vol', float('nan')):.2%}\n"
            f"Sharpe: {metrics.get('sharpe', float('nan')):.2f}\n"
            f"MaxDD:  {metrics.get('max_drawdown', float('nan')):+.2%}"
        )
        ax_eq.text(
            0.01, 0.98, stamp, transform=ax_eq.transAxes,
            fontsize=8, va="top", family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="#f0f0f0", ec="#888", alpha=0.9),
        )

    # --- Drawdown ------------------------------------------------------
    ax_dd = axes[1]
    peak = equity.cummax()
    dd = equity / peak - 1.0
    ax_dd.fill_between(dd.index, dd.values, 0, color="#d62728", alpha=0.45)
    ax_dd.plot(dd.index, dd.values, color="#d62728", linewidth=0.8)
    ax_dd.set_ylabel("Drawdown")
    ax_dd.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1%}"))

    # --- Position ------------------------------------------------------
    ax_pos = axes[2]
    pos = pnl["position_realized"]
    ax_pos.fill_between(pos.index, pos.values, 0, where=(pos > 0),
                        color="#2ca02c", alpha=0.55, label="Long")
    ax_pos.fill_between(pos.index, pos.values, 0, where=(pos < 0),
                        color="#d62728", alpha=0.55, label="Short")
    ax_pos.axhline(0, color="k", linewidth=0.6)
    ax_pos.set_ylabel("Position")
    ax_pos.set_ylim(-1.05, 1.05)
    ax_pos.legend(loc="upper right", fontsize=8)

    # Vertical markers at signal-generation days
    if signals is not None and len(signals) > 0:
        sig_dates = pd.to_datetime(signals["as_of_date"])
        for d in sig_dates:
            ax_pos.axvline(d, color="#888888", linewidth=0.5,
                           linestyle="--", alpha=0.5, zorder=0)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=140)
    plt.close(fig)
    logger.info("Saved paper-track chart to %s", out_path)
