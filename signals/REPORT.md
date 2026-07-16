# UC Paper-Trading Live Track

_Last update_: `2026-07-16 23:06 UTC`

## Latest signal

- **As-of close**: `2026-07-15 00:00:00` (close = `6.7700`)
- **Effective trading day**: `2026-07-16 00:00:00`
- **Composite signal**: `+0.4840`
- **Target position**: `+0.3550`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 30
- **Trading days observed**: 36 (since 2026-05-27)
- **Cumulative return**: `+0.11%`
- **Annualised return**: `+0.76%`
- **Annualised volatility**: `1.15%`
- **Sharpe ratio**: `0.67`
- **Sortino ratio**: `1.09`
- **Max drawdown**: `-0.33%`
- **Calmar**: `2.28`
- **Win rate (non-flat days)**: `40.6%`
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