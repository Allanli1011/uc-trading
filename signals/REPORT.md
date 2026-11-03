# UC Paper-Trading Live Track

_Last update_: `2026-11-03 03:28 UTC`

## Latest signal

- **As-of close**: `2026-11-02 00:00:00` (close = `6.6610`)
- **Effective trading day**: `2026-11-03 00:00:00`
- **Composite signal**: `+0.7730`
- **Target position**: `+0.7163`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 97
- **Trading days observed**: 114 (since 2026-05-27)
- **Cumulative return**: `-0.96%`
- **Annualised return**: `-2.12%`
- **Annualised volatility**: `0.91%`
- **Sharpe ratio**: `-2.34`
- **Sortino ratio**: `-2.90`
- **Max drawdown**: `-1.40%`
- **Calmar**: `-1.51`
- **Win rate (non-flat days)**: `30.8%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1943%`
- **In-market fraction**: `87.7%`

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