"""Generate today's UC trading signal and append it to ``signals/history.csv``.

Designed to be invoked daily from GitHub Actions (or any scheduler).  Reads
the latest available data, computes the composite signal + target position
using the production config, and persists one row per business day.

Outputs
-------
* ``signals/history.csv``  — full append-only log (one row per as-of date).
                             Idempotent: re-running the same day overwrites
                             that day's row.
* ``signals/latest.json``  — most recent signal in human-readable form.

The script is safe to run multiple times per day (e.g. via retries) — the
``as_of_date`` row is replaced, never duplicated.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.config import load_config  # noqa: E402
from src.data import align_and_clean, load_all  # noqa: E402
from src.features import build_factors  # noqa: E402
from src.signals import combine_signals, zscore_factors  # noqa: E402
from src.signals.combine import signal_to_position  # noqa: E402


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def compute_today_signal(cfg) -> dict:
    """Run the production pipeline and return the row for today's signal."""
    raw = load_all(cfg)
    panel = align_and_clean(
        raw,
        start=cfg["data"]["start_date"],
        end=cfg["data"].get("end_date"),
    )
    factor_cfg = cfg["factors"]
    factors = build_factors(panel, factor_cfg)
    z = zscore_factors(factors, window=factor_cfg.get("zscore_window", 252))
    composite = combine_signals(z, factor_cfg)

    signal_cfg = cfg.get("signal", {}) or {}
    threshold = float(signal_cfg.get("threshold", 0.0))
    deadband_mode = signal_cfg.get("deadband_mode", "hard")
    position_raw = signal_to_position(
        composite,
        style="proportional",
        threshold=threshold,
        deadband_mode=deadband_mode,
    )

    # Most recent valid row in the panel
    valid = composite.dropna()
    if valid.empty:
        raise RuntimeError("Composite signal is empty — check data fetch")
    as_of = valid.index[-1]
    next_bd = pd.bdate_range(start=as_of + pd.Timedelta(days=1), periods=1)[0]

    row: dict = {
        "as_of_date": as_of.strftime("%Y-%m-%d"),
        "effective_date": next_bd.strftime("%Y-%m-%d"),
        "uc_proxy_close": float(panel.loc[as_of, "uc_proxy"]),
        "composite_signal": float(composite.loc[as_of]),
        "position_target": float(position_raw.loc[as_of]),
        "signal_threshold": threshold,
        "deadband_mode": deadband_mode,
        "in_market": bool(abs(position_raw.loc[as_of]) > 1e-9),
        "computed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    for col in z.columns:
        v = z.loc[as_of, col] if as_of in z.index else np.nan
        row[f"z_{col}"] = None if pd.isna(v) else float(v)

    return row


def append_history(row: dict, history_path: Path) -> bool:
    """Append (or update-in-place) a row in the history CSV.

    Returns True if a new row was added, False if an existing row was
    updated (or no change).  Output is sorted by as_of_date.
    """
    history_path.parent.mkdir(parents=True, exist_ok=True)

    df_new = pd.DataFrame([row])
    if not history_path.exists():
        df_new.to_csv(history_path, index=False)
        return True

    history = pd.read_csv(history_path)
    # If as_of_date already there → replace
    mask = history["as_of_date"].astype(str) == row["as_of_date"]
    if mask.any():
        # Align columns (new columns become NaN in old rows)
        all_cols = sorted(set(history.columns).union(df_new.columns))
        history = history.reindex(columns=all_cols)
        df_new = df_new.reindex(columns=all_cols)
        history.loc[mask] = df_new.iloc[0].values
        added = False
    else:
        history = pd.concat([history, df_new], ignore_index=True)
        added = True

    history = history.sort_values("as_of_date").reset_index(drop=True)
    history.to_csv(history_path, index=False)
    return added


def main() -> int:
    setup_logging()
    log = logging.getLogger("daily_signal")

    cfg = load_config()
    log.info("Computing signal…")
    row = compute_today_signal(cfg)

    sig_dir = PROJECT_ROOT / "signals"
    history_path = sig_dir / "history.csv"
    latest_path = sig_dir / "latest.json"

    added = append_history(row, history_path)

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(row, f, indent=2, ensure_ascii=False)

    action = "Added" if added else "Updated"
    log.info(
        "%s signal for %s -> position %+.4f (composite %+.4f, in_market=%s)",
        action, row["as_of_date"], row["position_target"],
        row["composite_signal"], row["in_market"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
