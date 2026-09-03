# UC Paper-Trading Live Track

_Last update_: `2026-09-03 23:57 UTC`

## Latest signal

- **As-of close**: `2026-09-02 00:00:00` (close = `6.7202`)
- **Effective trading day**: `2026-09-03 00:00:00`
- **Composite signal**: `+0.3949`
- **Target position**: `+0.2436`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 58
- **Trading days observed**: 71 (since 2026-05-27)
- **Cumulative return**: `-0.19%`
- **Annualised return**: `-0.67%`
- **Annualised volatility**: `0.88%`
- **Sharpe ratio**: `-0.76`
- **Sortino ratio**: `-1.13`
- **Max drawdown**: `-0.63%`
- **Calmar**: `-1.06`
- **Win rate (non-flat days)**: `33.9%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `83.1%`

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