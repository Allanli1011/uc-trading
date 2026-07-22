# UC Paper-Trading Live Track

_Last update_: `2026-07-22 23:13 UTC`

## Latest signal

- **As-of close**: `2026-07-21 00:00:00` (close = `6.7725`)
- **Effective trading day**: `2026-07-22 00:00:00`
- **Composite signal**: `+0.1641`
- **Target position**: `+0.0000`  (FLAT)
- **In market**: `False`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 33
- **Trading days observed**: 40 (since 2026-05-27)
- **Cumulative return**: `+0.11%`
- **Annualised return**: `+0.67%`
- **Annualised volatility**: `1.09%`
- **Sharpe ratio**: `0.62`
- **Sortino ratio**: `0.99`
- **Max drawdown**: `-0.35%`
- **Calmar**: `1.93`
- **Win rate (non-flat days)**: `38.9%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `100.0%`

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