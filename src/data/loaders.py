"""Data loaders for UC macro factor strategy.

Each fetcher returns a DataFrame with DatetimeIndex (tz-naive, daily) and a
single ``close`` column.  ``load_all`` orchestrates all sources and applies
disk caching with a TTL.

Sources
-------
* Yahoo Finance (no auth) — FX, equity indices, commodities, treasury yields.
* FRED via ``pandas_datareader`` (no auth) — SOFR, etc.
* AKShare (no auth) — CGB yield curve and SHIBOR (proxy for onshore CNY).
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------
def _safe_key(key: str) -> str:
    return key.replace("/", "_").replace("\\", "_").replace("^", "").replace("=", "_").replace(":", "_")


def _cache_path(cache_dir: Path, source: str, key: str) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{source}_{_safe_key(key)}.csv"


def _is_cache_fresh(path: Path, ttl_days: int) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < ttl_days * 86400


def _read_cache(path: Path) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        df.index.name = "date"
        return df
    except Exception as exc:
        logger.warning("Cache read failed for %s: %s", path, exc)
        return None


def _write_cache(path: Path, df: pd.DataFrame) -> None:
    try:
        df.to_csv(path)
    except Exception as exc:
        logger.warning("Cache write failed for %s: %s", path, exc)


def _cached_fetch(
    cache_dir: Path,
    source: str,
    key: str,
    ttl_days: int,
    fetcher: Callable[[], pd.DataFrame],
    use_cache: bool = True,
) -> Optional[pd.DataFrame]:
    path = _cache_path(cache_dir, source, key)
    if use_cache and _is_cache_fresh(path, ttl_days):
        df = _read_cache(path)
        if df is not None and len(df) > 0:
            return df
    try:
        df = fetcher()
    except Exception as exc:
        logger.error("Fetch failed for %s/%s: %s", source, key, exc)
        # Fall back to stale cache if available
        if path.exists():
            logger.warning("Falling back to stale cache for %s/%s", source, key)
            return _read_cache(path)
        return None
    if df is None or len(df) == 0:
        logger.warning("Empty result for %s/%s", source, key)
        return None
    _write_cache(path, df)
    return df


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------
def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)
    df.index.name = "date"
    return df.sort_index()


def fetch_yahoo(
    ticker: str,
    start: str,
    end: Optional[str] = None,
    retries: int = 3,
    backoff_seconds: float = 2.0,
) -> pd.DataFrame:
    """Yahoo Finance fetch with retry-on-empty.

    yfinance occasionally returns an empty frame for a perfectly valid
    ticker (rate-limited or transient network error).  We retry up to
    ``retries`` times with exponential backoff before giving up.
    """
    import yfinance as yf

    end = end or datetime.now().strftime("%Y-%m-%d")
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(
                ticker, start=start, end=end, progress=False, auto_adjust=False
            )
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                if "Close" not in df.columns:
                    return pd.DataFrame()
                out = df[["Close"]].rename(columns={"Close": "close"})
                return _normalize_index(out).dropna()
        except Exception as exc:
            last_err = exc
        if attempt < retries:
            time.sleep(backoff_seconds * attempt)
            logger.info("Retrying Yahoo fetch for %s (attempt %d)", ticker, attempt + 1)

    if last_err:
        logger.warning("Yahoo fetch for %s exhausted retries: %s", ticker, last_err)
    return pd.DataFrame()


def fetch_fred(series_id: str, start: str, end: Optional[str] = None) -> pd.DataFrame:
    import pandas_datareader.data as web

    # pandas_datareader expects tz-naive Timestamps
    start_dt = pd.Timestamp(start).tz_localize(None) if pd.Timestamp(start).tz else pd.Timestamp(start)
    end_dt = pd.Timestamp(end) if end else pd.Timestamp.now().normalize()
    if getattr(end_dt, "tz", None) is not None:
        end_dt = end_dt.tz_localize(None)
    s = web.DataReader(series_id, "fred", start_dt, end_dt)
    s.columns = ["close"]
    return _normalize_index(s).dropna()


def fetch_cgb_yield(
    start: str, end: Optional[str] = None, tenor: str = "10年"
) -> pd.DataFrame:
    """中债国债收益率曲线 via AKShare.

    The chinabond endpoint silently returns an empty response when the
    requested window exceeds ~500 working days *and* the end date is past
    a recent server-side cutoff.  We work around this by chunking the
    request into ≤ 9-month windows and concatenating.

    Returns ``close`` in percent (e.g. 2.55).
    """
    import akshare as ak

    end = end or datetime.now().strftime("%Y-%m-%d")
    start_dt = pd.Timestamp(start)
    end_dt = pd.Timestamp(end)

    chunks: list[pd.DataFrame] = []
    chunk_start = start_dt
    while chunk_start <= end_dt:
        chunk_end = min(chunk_start + pd.DateOffset(months=9), end_dt)
        try:
            part = ak.bond_china_yield(
                start_date=chunk_start.strftime("%Y%m%d"),
                end_date=chunk_end.strftime("%Y%m%d"),
            )
            if part is not None and len(part) > 0:
                chunks.append(part)
            else:
                logger.debug(
                    "CGB chunk %s..%s empty",
                    chunk_start.date(), chunk_end.date(),
                )
        except Exception as exc:
            logger.warning(
                "CGB chunk %s..%s failed: %s",
                chunk_start.date(), chunk_end.date(), exc,
            )
        chunk_start = chunk_end + pd.Timedelta(days=1)

    if not chunks:
        raise RuntimeError(f"No CGB data fetched for {start}..{end}")

    df = pd.concat(chunks, ignore_index=True)

    # Filter to government bond curve.  Name varies by AKShare version.
    curve_col = next((c for c in df.columns if "曲线" in c or "name" in c.lower()), None)
    if curve_col:
        mask = df[curve_col].astype(str).str.contains("国债")
        if mask.any():
            df = df[mask]

    date_col = next((c for c in ["日期", "date", "Date"] if c in df.columns), None)
    if date_col is None:
        raise ValueError(f"No date column in CGB data, columns={df.columns.tolist()}")
    if tenor not in df.columns:
        raise ValueError(f"Tenor {tenor!r} not in CGB columns: {df.columns.tolist()}")

    out = df[[date_col, tenor]].rename(columns={date_col: "date", tenor: "close"})
    out["date"] = pd.to_datetime(out["date"])
    out = (
        out.dropna(subset=["close"])
        .drop_duplicates(subset=["date"])
        .set_index("date")
        .sort_index()
    )
    return _normalize_index(out)


def fetch_shibor(
    start: str, end: Optional[str] = None, tenor: str = "1M"
) -> pd.DataFrame:
    """SHIBOR via AKShare.  Best-effort across API versions.

    Returns ``close`` in percent.  Falls back to first available tenor column
    if requested tenor not found.
    """
    import akshare as ak

    df = None
    for fn_name in ("macro_china_shibor_all", "rate_interbank"):
        if hasattr(ak, fn_name):
            try:
                fn = getattr(ak, fn_name)
                if fn_name == "rate_interbank":
                    df = fn(
                        market="上海银行同业拆借市场",
                        symbol="Shibor人民币",
                        indicator=tenor.replace("M", "月"),
                    )
                else:
                    df = fn()
                if df is not None and len(df) > 0:
                    break
            except Exception as exc:
                logger.warning("SHIBOR fetch via %s failed: %s", fn_name, exc)
                df = None

    if df is None or len(df) == 0:
        raise RuntimeError("All SHIBOR endpoints unavailable")

    # Locate date column
    date_col = next((c for c in df.columns if c in ("日期", "date", "Date", "报告日")), None)
    if date_col is None:
        date_col = df.columns[0]

    # Locate value column
    tenor_aliases = [tenor, tenor.replace("M", "月"), tenor.replace("M", "m"), "利率"]
    value_col = next((c for c in tenor_aliases if c in df.columns), None)
    if value_col is None:
        value_col = [c for c in df.columns if c != date_col][0]

    out = df[[date_col, value_col]].rename(columns={date_col: "date", value_col: "close"})
    out["date"] = pd.to_datetime(out["date"])
    out["close"] = pd.to_numeric(out["close"], errors="coerce")
    out = out.dropna(subset=["close"]).set_index("date").sort_index()
    out = out[out.index >= pd.Timestamp(start)]
    if end:
        out = out[out.index <= pd.Timestamp(end)]
    return _normalize_index(out)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def load_all(config) -> dict[str, pd.DataFrame]:
    """Load every configured data source.

    Returns a dict mapping a logical name (e.g. ``uc_proxy``) to a single-
    column DataFrame with a ``close`` series.  Sources that fail are skipped
    with a logged warning so the pipeline can still run on partial data.
    """
    cfg = config["data"]
    cache_dir = Path(config.resolve(cfg["cache_dir"]))
    use_cache = cfg.get("use_cache", True)
    ttl = cfg.get("cache_ttl_days", 1)
    start = cfg["start_date"]
    end = cfg.get("end_date")

    out: dict[str, pd.DataFrame] = {}

    # Yahoo Finance
    for name, ticker in (cfg.get("tickers") or {}).items():
        df = _cached_fetch(
            cache_dir, "yahoo", ticker, ttl,
            lambda t=ticker: fetch_yahoo(t, start, end),
            use_cache,
        )
        if df is not None:
            out[name] = df
        else:
            logger.warning("Missing Yahoo data for %s (%s)", name, ticker)

    # FRED
    for name, series_id in (cfg.get("fred") or {}).items():
        df = _cached_fetch(
            cache_dir, "fred", series_id, ttl,
            lambda s=series_id: fetch_fred(s, start, end),
            use_cache,
        )
        if df is not None:
            out[name] = df

    # AKShare CGB
    if (cfg.get("akshare") or {}).get("cgb_yield"):
        df = _cached_fetch(
            cache_dir, "akshare", "cgb_10y", ttl,
            lambda: fetch_cgb_yield(start, end),
            use_cache,
        )
        if df is not None:
            out["cgb_10y"] = df

    # AKShare SHIBOR (best effort)
    if (cfg.get("akshare") or {}).get("shibor"):
        df = _cached_fetch(
            cache_dir, "akshare", "shibor_1m", ttl,
            lambda: fetch_shibor(start, end),
            use_cache,
        )
        if df is not None:
            out["shibor_1m"] = df

    if not out:
        raise RuntimeError("No data could be loaded from any source")

    logger.info("Loaded %d series: %s", len(out), sorted(out.keys()))
    return out


if __name__ == "__main__":
    # Smoke test
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.config import load_config

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    cfg = load_config()
    data = load_all(cfg)
    for k, v in data.items():
        print(f"{k:20s} {len(v):5d} rows  {v.index.min().date()} -> {v.index.max().date()}")
