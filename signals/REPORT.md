# UC Paper-Trading Live Track

_Last update_: `2026-09-23 00:17 UTC`

## Latest signal

- **As-of close**: `2026-09-22 00:00:00` (close = `6.6953`)
- **Effective trading day**: `2026-09-23 00:00:00`
- **Composite signal**: `+0.8920`
- **Target position**: `+0.8650`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 69
- **Trading days observed**: 85 (since 2026-05-27)
- **Cumulative return**: `-0.53%`
- **Annualised return**: `-1.57%`
- **Annualised volatility**: `0.88%`
- **Sharpe ratio**: `-1.79`
- **Sortino ratio**: `-2.38`
- **Max drawdown**: `-0.97%`
- **Calmar**: `-1.62`
- **Win rate (non-flat days)**: `32.4%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `83.5%`

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