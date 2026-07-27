# UC Paper-Trading Live Track

_Last update_: `2026-07-27 23:14 UTC`

## Latest signal

- **As-of close**: `2026-07-24 00:00:00` (close = `6.7725`)
- **Effective trading day**: `2026-07-27 00:00:00`
- **Composite signal**: `+0.3024`
- **Target position**: `+0.1280`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 35
- **Trading days observed**: 43 (since 2026-05-27)
- **Cumulative return**: `+0.10%`
- **Annualised return**: `+0.61%`
- **Annualised volatility**: `1.05%`
- **Sharpe ratio**: `0.58`
- **Sortino ratio**: `0.90`
- **Max drawdown**: `-0.35%`
- **Calmar**: `1.75`
- **Win rate (non-flat days)**: `37.8%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `93.0%`

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