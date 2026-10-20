# UC Paper-Trading Live Track

_Last update_: `2026-10-20 01:03 UTC`

## Latest signal

- **As-of close**: `2026-10-19 00:00:00` (close = `6.6909`)
- **Effective trading day**: `2026-10-20 00:00:00`
- **Composite signal**: `+1.2666`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 87
- **Trading days observed**: 104 (since 2026-05-27)
- **Cumulative return**: `-0.60%`
- **Annualised return**: `-1.45%`
- **Annualised volatility**: `0.90%`
- **Sharpe ratio**: `-1.63`
- **Sortino ratio**: `-2.12`
- **Max drawdown**: `-1.04%`
- **Calmar**: `-1.40`
- **Win rate (non-flat days)**: `34.1%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `86.5%`

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