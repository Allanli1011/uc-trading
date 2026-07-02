# UC Paper-Trading Live Track

_Last update_: `2026-07-02 23:18 UTC`

## Latest signal

- **As-of close**: `2026-07-01 00:00:00` (close = `6.7936`)
- **Effective trading day**: `2026-07-02 00:00:00`
- **Composite signal**: `+0.7740`
- **Target position**: `+0.7175`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 22
- **Trading days observed**: 26 (since 2026-05-27)
- **Cumulative return**: `+0.38%`
- **Annualised return**: `+3.72%`
- **Annualised volatility**: `1.14%`
- **Sharpe ratio**: `3.21`
- **Sortino ratio**: `6.40`
- **Max drawdown**: `-0.12%`
- **Calmar**: `31.41`
- **Win rate (non-flat days)**: `40.9%`
- **Best day**: `+0.2284%`
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