# UC Paper-Trading Live Track

_Last update_: `2026-09-18 00:05 UTC`

## Latest signal

- **As-of close**: `2026-09-17 00:00:00` (close = `6.7060`)
- **Effective trading day**: `2026-09-18 00:00:00`
- **Composite signal**: `+0.8214`
- **Target position**: `+0.7768`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 66
- **Trading days observed**: 82 (since 2026-05-27)
- **Cumulative return**: `-0.37%`
- **Annualised return**: `-1.14%`
- **Annualised volatility**: `0.86%`
- **Sharpe ratio**: `-1.32`
- **Sortino ratio**: `-1.83`
- **Max drawdown**: `-0.81%`
- **Calmar**: `-1.40`
- **Win rate (non-flat days)**: `32.4%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `82.9%`

## Active factor set

`bitcoin_momentum`, `copper_momentum`, `dxy_momentum`, `gold_momentum`, `rate_diff_level`, `vix_change`

## Track-record chart

![Live track](track.png)

## Files

- `signals/history.csv` — append-only signal log
- `signals/latest.json` — latest signal in pretty form
- `signals/paper_pnl.csv` — realised daily PnL series
- `signals/stats.json` — machine-readable performance metrics
- `signals/track.png` — live equity / drawdown / position chart

---

_Paper-trading only. Uses `CNY=X` (in-shore) as a proxy for SGX UC futures; real-life UC PnL will differ by the CNY/CNH basis._