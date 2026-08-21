# UC Paper-Trading Live Track

_Last update_: `2026-08-21 22:34 UTC`

## Latest signal

- **As-of close**: `2026-08-21 00:00:00` (close = `6.7225`)
- **Effective trading day**: `2026-08-24 00:00:00`
- **Composite signal**: `+2.1580`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 50
- **Trading days observed**: 63 (since 2026-05-27)
- **Cumulative return**: `-0.13%`
- **Annualised return**: `-0.53%`
- **Annualised volatility**: `0.93%`
- **Sharpe ratio**: `-0.57`
- **Sortino ratio**: `-0.85`
- **Max drawdown**: `-0.57%`
- **Calmar**: `-0.93`
- **Win rate (non-flat days)**: `34.6%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `85.7%`

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