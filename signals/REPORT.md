# UC Paper-Trading Live Track

_Last update_: `2026-07-28 23:10 UTC`

## Latest signal

- **As-of close**: `2026-07-27 00:00:00` (close = `6.7718`)
- **Effective trading day**: `2026-07-28 00:00:00`
- **Composite signal**: `+0.3510`
- **Target position**: `+0.1888`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 36
- **Trading days observed**: 44 (since 2026-05-27)
- **Cumulative return**: `+0.10%`
- **Annualised return**: `+0.58%`
- **Annualised volatility**: `1.04%`
- **Sharpe ratio**: `0.56`
- **Sortino ratio**: `0.87`
- **Max drawdown**: `-0.35%`
- **Calmar**: `1.66`
- **Win rate (non-flat days)**: `36.8%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `93.2%`

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