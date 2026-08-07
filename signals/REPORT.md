# UC Paper-Trading Live Track

_Last update_: `2026-08-07 22:47 UTC`

## Latest signal

- **As-of close**: `2026-08-07 00:00:00` (close = `6.7488`)
- **Effective trading day**: `2026-08-10 00:00:00`
- **Composite signal**: `+1.9671`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 43
- **Trading days observed**: 53 (since 2026-05-27)
- **Cumulative return**: `-0.00%`
- **Annualised return**: `-0.00%`
- **Annualised volatility**: `0.95%`
- **Sharpe ratio**: `0.00`
- **Sortino ratio**: `0.01`
- **Max drawdown**: `-0.44%`
- **Calmar**: `-0.00`
- **Win rate (non-flat days)**: `34.1%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `86.8%`

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