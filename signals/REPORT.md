# UC Paper-Trading Live Track

_Last update_: `2026-11-06 02:13 UTC`

## Latest signal

- **As-of close**: `2026-11-05 00:00:00` (close = `6.6731`)
- **Effective trading day**: `2026-11-06 00:00:00`
- **Composite signal**: `+1.0729`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 100
- **Trading days observed**: 117 (since 2026-05-27)
- **Cumulative return**: `-0.81%`
- **Annualised return**: `-1.73%`
- **Annualised volatility**: `1.02%`
- **Sharpe ratio**: `-1.70`
- **Sortino ratio**: `-2.29`
- **Max drawdown**: `-1.54%`
- **Calmar**: `-1.12`
- **Win rate (non-flat days)**: `31.9%`
- **Best day**: `+0.2917%`
- **Worst day**: `-0.1943%`
- **In-market fraction**: `88.0%`

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