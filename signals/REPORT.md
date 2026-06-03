# UC Paper-Trading Live Track

_Last update_: `2026-06-03 23:54 UTC`

## Latest signal

- **As-of close**: `2026-06-02 00:00:00` (close = `6.7650`)
- **Effective trading day**: `2026-06-03 00:00:00`
- **Composite signal**: `+0.5805`
- **Target position**: `+0.4757`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 5
- **Trading days observed**: 5 (since 2026-05-27)
- **Cumulative return**: `-0.11%`
- **Annualised return**: `-5.31%`
- **Annualised volatility**: `0.42%`
- **Sharpe ratio**: `-13.05`
- **Sortino ratio**: `-13.02`
- **Max drawdown**: `-0.09%`
- **Calmar**: `-58.91`
- **Win rate (non-flat days)**: `20.0%`
- **Best day**: `+0.0017%`
- **Worst day**: `-0.0665%`
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