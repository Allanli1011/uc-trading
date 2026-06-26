# UC Paper-Trading Live Track

_Last update_: `2026-06-26 23:17 UTC`

## Latest signal

- **As-of close**: `2026-06-26 00:00:00` (close = `6.7900`)
- **Effective trading day**: `2026-06-29 00:00:00`
- **Composite signal**: `+1.2597`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 19
- **Trading days observed**: 23 (since 2026-05-27)
- **Cumulative return**: `+0.33%`
- **Annualised return**: `+3.63%`
- **Annualised volatility**: `1.13%`
- **Sharpe ratio**: `3.16`
- **Sortino ratio**: `6.11`
- **Max drawdown**: `-0.12%`
- **Calmar**: `30.60`
- **Win rate (non-flat days)**: `42.1%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1185%`
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