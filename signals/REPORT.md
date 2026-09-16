# UC Paper-Trading Live Track

_Last update_: `2026-09-16 00:08 UTC`

## Latest signal

- **As-of close**: `2026-09-15 00:00:00` (close = `6.7082`)
- **Effective trading day**: `2026-09-16 00:00:00`
- **Composite signal**: `+0.8278`
- **Target position**: `+0.7848`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 64
- **Trading days observed**: 80 (since 2026-05-27)
- **Cumulative return**: `-0.33%`
- **Annualised return**: `-1.02%`
- **Annualised volatility**: `0.86%`
- **Sharpe ratio**: `-1.19`
- **Sortino ratio**: `-1.66`
- **Max drawdown**: `-0.78%`
- **Calmar**: `-1.32`
- **Win rate (non-flat days)**: `31.8%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `82.5%`

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