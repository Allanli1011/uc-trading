# UC Paper-Trading Live Track

_Last update_: `2026-06-12 23:27 UTC`

## Latest signal

- **As-of close**: `2026-06-12 00:00:00` (close = `6.7755`)
- **Effective trading day**: `2026-06-15 00:00:00`
- **Composite signal**: `+0.9930`
- **Target position**: `+0.9912`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 11
- **Trading days observed**: 13 (since 2026-05-27)
- **Cumulative return**: `+0.06%`
- **Annualised return**: `+1.09%`
- **Annualised volatility**: `0.97%`
- **Sharpe ratio**: `1.12`
- **Sortino ratio**: `1.60`
- **Max drawdown**: `-0.12%`
- **Calmar**: `9.21`
- **Win rate (non-flat days)**: `45.5%`
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