"""Performance metrics for backtest results."""
from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def annualized_return(returns: pd.Series) -> float:
    """CAGR computed geometrically from a daily return series."""
    r = returns.dropna()
    if len(r) == 0:
        return float("nan")
    total = (1 + r).prod()
    years = len(r) / TRADING_DAYS
    return total ** (1 / years) - 1 if years > 0 else float("nan")


def annualized_volatility(returns: pd.Series) -> float:
    return returns.std() * np.sqrt(TRADING_DAYS)


def sharpe_ratio(returns: pd.Series, risk_free_annual: float = 0.0) -> float:
    r = returns.dropna()
    if len(r) < 2 or r.std() == 0:
        return float("nan")
    excess = r - risk_free_annual / TRADING_DAYS
    return excess.mean() / excess.std() * np.sqrt(TRADING_DAYS)


def sortino_ratio(returns: pd.Series, risk_free_annual: float = 0.0) -> float:
    r = returns.dropna()
    excess = r - risk_free_annual / TRADING_DAYS
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float("nan")
    return excess.mean() / downside.std() * np.sqrt(TRADING_DAYS)


def max_drawdown(equity: pd.Series) -> float:
    """Return the *minimum* (most negative) peak-to-trough drawdown."""
    eq = equity.dropna()
    if len(eq) == 0:
        return float("nan")
    peak = eq.cummax()
    dd = eq / peak - 1.0
    return dd.min()


def calmar_ratio(returns: pd.Series, equity: pd.Series) -> float:
    cagr = annualized_return(returns)
    mdd = abs(max_drawdown(equity))
    return cagr / mdd if mdd > 0 else float("nan")


def win_rate(returns: pd.Series) -> float:
    r = returns.dropna()
    nonzero = r[r != 0]
    if len(nonzero) == 0:
        return float("nan")
    return (nonzero > 0).mean()


def avg_annual_turnover(turnover: pd.Series) -> float:
    """Average annual turnover (sum over the year of |Δposition|)."""
    t = turnover.dropna()
    if len(t) == 0:
        return 0.0
    return t.mean() * TRADING_DAYS


def compute_metrics(backtest: pd.DataFrame) -> dict[str, float]:
    """One-shot summary metrics."""
    rets = backtest["net_return"]
    equity = backtest["equity"]
    turnover = backtest["turnover"]

    return {
        "ann_return": annualized_return(rets),
        "ann_vol": annualized_volatility(rets),
        "sharpe": sharpe_ratio(rets),
        "sortino": sortino_ratio(rets),
        "max_drawdown": max_drawdown(equity),
        "calmar": calmar_ratio(rets, equity),
        "win_rate": win_rate(rets),
        "avg_annual_turnover": avg_annual_turnover(turnover),
        "trading_days": int(rets.notna().sum()),
        "final_equity": float(equity.iloc[-1]) if len(equity) else float("nan"),
    }


def format_metrics(metrics: dict[str, float]) -> str:
    """Pretty-print metrics dict as an aligned table."""
    fmt = {
        "ann_return": ("Annualized return", "{:+.2%}"),
        "ann_vol": ("Annualized vol", "{:.2%}"),
        "sharpe": ("Sharpe", "{:.2f}"),
        "sortino": ("Sortino", "{:.2f}"),
        "max_drawdown": ("Max drawdown", "{:+.2%}"),
        "calmar": ("Calmar", "{:.2f}"),
        "win_rate": ("Win rate (non-flat days)", "{:.1%}"),
        "avg_annual_turnover": ("Avg annual turnover", "{:.1f}x"),
        "trading_days": ("Trading days", "{:d}"),
        "final_equity": ("Final equity (×NAV)", "{:.4f}"),
    }
    lines = []
    for k, (label, spec) in fmt.items():
        if k not in metrics:
            continue
        try:
            lines.append(f"  {label:30s} {spec.format(metrics[k])}")
        except Exception:
            lines.append(f"  {label:30s} {metrics[k]}")
    return "\n".join(lines)
