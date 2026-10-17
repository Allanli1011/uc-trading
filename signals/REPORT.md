# UC Paper-Trading Live Track

_Last update_: `2026-10-17 00:18 UTC`

## Latest signal

- **As-of close**: `2026-10-16 00:00:00` (close = `6.6768`)
- **Effective trading day**: `2026-10-19 00:00:00`
- **Composite signal**: `+1.3628`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 86
- **Trading days observed**: 103 (since 2026-05-27)
- **Cumulative return**: `-0.81%`
- **Annualised return**: `-1.97%`
- **Annualised volatility**: `0.97%`
- **Sharpe ratio**: `-2.05`
- **Sortino ratio**: `-2.45`
- **Max drawdown**: `-1.25%`
- **Calmar**: `-1.58`
- **Win rate (non-flat days)**: `34.1%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.2361%`
- **In-market fraction**: `86.4%`

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