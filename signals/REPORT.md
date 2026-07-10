# UC Paper-Trading Live Track

_Last update_: `2026-07-10 23:07 UTC`

## Latest signal

- **As-of close**: `2026-07-10 00:00:00` (close = `6.7921`)
- **Effective trading day**: `2026-07-13 00:00:00`
- **Composite signal**: `+1.4128`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 27
- **Trading days observed**: 33 (since 2026-05-27)
- **Cumulative return**: `+0.32%`
- **Annualised return**: `+2.49%`
- **Annualised volatility**: `1.07%`
- **Sharpe ratio**: `2.30`
- **Sortino ratio**: `4.49`
- **Max drawdown**: `-0.12%`
- **Calmar**: `20.28`
- **Win rate (non-flat days)**: `41.4%`
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