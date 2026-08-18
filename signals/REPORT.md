# UC Paper-Trading Live Track

_Last update_: `2026-08-18 22:33 UTC`

## Latest signal

- **As-of close**: `2026-08-18 00:00:00` (close = `6.7399`)
- **Effective trading day**: `2026-08-19 00:00:00`
- **Composite signal**: `+2.2808`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 48
- **Trading days observed**: 59 (since 2026-05-27)
- **Cumulative return**: `-0.07%`
- **Annualised return**: `-0.29%`
- **Annualised volatility**: `0.91%`
- **Sharpe ratio**: `-0.31`
- **Sortino ratio**: `-0.47`
- **Max drawdown**: `-0.51%`
- **Calmar**: `-0.57`
- **Win rate (non-flat days)**: `36.7%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `88.1%`

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