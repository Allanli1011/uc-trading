# UC Paper-Trading Live Track

_Last update_: `2026-10-23 00:33 UTC`

## Latest signal

- **As-of close**: `2026-10-22 00:00:00` (close = `6.6779`)
- **Effective trading day**: `2026-10-23 00:00:00`
- **Composite signal**: `+1.0254`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 90
- **Trading days observed**: 107 (since 2026-05-27)
- **Cumulative return**: `-0.80%`
- **Annualised return**: `-1.87%`
- **Annualised volatility**: `0.93%`
- **Sharpe ratio**: `-2.02`
- **Sortino ratio**: `-2.48`
- **Max drawdown**: `-1.24%`
- **Calmar**: `-1.51`
- **Win rate (non-flat days)**: `33.3%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1943%`
- **In-market fraction**: `86.9%`

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