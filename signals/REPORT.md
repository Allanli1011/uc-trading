# UC Paper-Trading Live Track

_Last update_: `2026-09-03 00:01 UTC`

## Latest signal

- **As-of close**: `2026-09-01 00:00:00` (close = `6.7260`)
- **Effective trading day**: `2026-09-02 00:00:00`
- **Composite signal**: `+0.3384`
- **Target position**: `+0.1730`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 57
- **Trading days observed**: 70 (since 2026-05-27)
- **Cumulative return**: `-0.17%`
- **Annualised return**: `-0.62%`
- **Annualised volatility**: `0.89%`
- **Sharpe ratio**: `-0.70`
- **Sortino ratio**: `-1.03`
- **Max drawdown**: `-0.62%`
- **Calmar**: `-1.01`
- **Win rate (non-flat days)**: `34.5%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `82.9%`

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