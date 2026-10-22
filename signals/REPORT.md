# UC Paper-Trading Live Track

_Last update_: `2026-10-22 00:36 UTC`

## Latest signal

- **As-of close**: `2026-10-21 00:00:00` (close = `6.6779`)
- **Effective trading day**: `2026-10-22 00:00:00`
- **Composite signal**: `+0.8696`
- **Target position**: `+0.8370`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 89
- **Trading days observed**: 106 (since 2026-05-27)
- **Cumulative return**: `-0.80%`
- **Annualised return**: `-1.88%`
- **Annualised volatility**: `0.93%`
- **Sharpe ratio**: `-2.03`
- **Sortino ratio**: `-2.49`
- **Max drawdown**: `-1.23%`
- **Calmar**: `-1.52`
- **Win rate (non-flat days)**: `33.7%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1943%`
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