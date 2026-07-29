# UC Paper-Trading Live Track

_Last update_: `2026-07-29 23:06 UTC`

## Latest signal

- **As-of close**: `2026-07-28 00:00:00` (close = `6.7657`)
- **Effective trading day**: `2026-07-29 00:00:00`
- **Composite signal**: `+0.3079`
- **Target position**: `+0.1349`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 37
- **Trading days observed**: 45 (since 2026-05-27)
- **Cumulative return**: `+0.08%`
- **Annualised return**: `+0.47%`
- **Annualised volatility**: `1.03%`
- **Sharpe ratio**: `0.46`
- **Sortino ratio**: `0.71`
- **Max drawdown**: `-0.36%`
- **Calmar**: `1.30`
- **Win rate (non-flat days)**: `35.9%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `93.3%`

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