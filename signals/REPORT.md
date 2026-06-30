# UC Paper-Trading Live Track

_Last update_: `2026-06-30 23:22 UTC`

## Latest signal

- **As-of close**: `2026-06-29 00:00:00` (close = `6.7980`)
- **Effective trading day**: `2026-06-30 00:00:00`
- **Composite signal**: `+1.1702`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 20
- **Trading days observed**: 24 (since 2026-05-27)
- **Cumulative return**: `+0.44%`
- **Annualised return**: `+4.76%`
- **Annualised volatility**: `1.16%`
- **Sharpe ratio**: `4.03`
- **Sortino ratio**: `7.97`
- **Max drawdown**: `-0.12%`
- **Calmar**: `40.16`
- **Win rate (non-flat days)**: `45.0%`
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