# UC Paper-Trading Live Track

_Last update_: `2026-05-29 23:23 UTC`

## Latest signal

- **As-of close**: `2026-05-29 00:00:00` (close = `6.7795`)
- **Effective trading day**: `2026-06-01 00:00:00`
- **Composite signal**: `+1.3187`
- **Target position**: `+1.0000`  (LONG)
- **In market**: `True`
- **Deadband**: threshold=`0.2`, mode=`soft`

## Live performance

- **Signals recorded**: 3
- **Trading days observed**: 3 (since 2026-05-27)
- **Cumulative return**: `-0.03%`
- **Annualised return**: `-2.82%`
- **Annualised volatility**: `0.18%`
- **Sharpe ratio**: `-15.95`
- **Sortino ratio**: `-533.22`
- **Max drawdown**: `-0.02%`
- **Calmar**: `-159.96`
- **Win rate (non-flat days)**: `33.3%`
- **Best day**: `+0.0017%`
- **Worst day**: `-0.0181%`
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