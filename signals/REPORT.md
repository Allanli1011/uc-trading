# UC Paper-Trading Live Track

_Last update_: `2026-08-28 06:06 UTC`

## Latest signal

- **As-of close**: `2026-08-27 00:00:00` (close = `6.7225`)
- **Effective trading day**: `2026-08-28 00:00:00`
- **Composite signal**: `+0.0653`
- **Target position**: `+0.0000`  (FLAT)
- **In market**: `False`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 54
- **Trading days observed**: 67 (since 2026-05-27)
- **Cumulative return**: `-0.18%`
- **Annualised return**: `-0.66%`
- **Annualised volatility**: `0.91%`
- **Sharpe ratio**: `-0.73`
- **Sortino ratio**: `-1.10`
- **Max drawdown**: `-0.62%`
- **Calmar**: `-1.07`
- **Win rate (non-flat days)**: `33.9%`
- **Best day**: `+0.2284%`
- **Worst day**: `-0.1510%`
- **In-market fraction**: `85.1%`

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