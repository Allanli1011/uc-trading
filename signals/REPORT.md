# UC Paper-Trading Live Track

_Last update_: `2026-10-02 01:33 UTC`

## Latest signal

- **As-of close**: `2026-10-01 00:00:00` (close = `6.7045`)
- **Effective trading day**: `2026-10-02 00:00:00`
- **Composite signal**: `+1.5260`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 76
- **Trading days observed**: 92 (since 2026-05-27)
- **Cumulative return**: `-0.41%`
- **Annualised return**: `-1.11%`
- **Annualised volatility**: `0.92%`
- **Sharpe ratio**: `-1.20`
- **Sortino ratio**: `-1.66`
- **Max drawdown**: `-0.97%`
- **Calmar**: `-1.14`
- **Win rate (non-flat days)**: `35.1%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `84.8%`

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