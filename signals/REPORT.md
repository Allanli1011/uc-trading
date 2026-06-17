# UC Paper-Trading Live Track

_Last update_: `2026-06-17 23:47 UTC`

## Latest signal

- **As-of close**: `2026-06-16 00:00:00` (close = `6.7570`)
- **Effective trading day**: `2026-06-17 00:00:00`
- **Composite signal**: `+0.3635`
- **Target position**: `+0.2043`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 13
- **Trading days observed**: 15 (since 2026-05-27)
- **Cumulative return**: `-0.05%`
- **Annualised return**: `-0.91%`
- **Annualised volatility**: `0.96%`
- **Sharpe ratio**: `-0.95`
- **Sortino ratio**: `-1.54`
- **Max drawdown**: `-0.12%`
- **Calmar**: `-7.67`
- **Win rate (non-flat days)**: `38.5%`
- **Best day**: `+0.1035%`
- **Worst day**: `-0.1185%`
- **In-market fraction**: `100.0%`

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