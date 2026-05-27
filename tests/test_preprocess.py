"""Tests for the preprocessing step."""
from __future__ import annotations

import pandas as pd

from src.data.preprocess import align_and_clean


def _series(values: list[float], dates: list[str]) -> pd.DataFrame:
    s = pd.Series(values, index=pd.to_datetime(dates))
    return pd.DataFrame({"close": s})


def test_align_normalizes_tnx_scale():
    """Yahoo's ^TNX is quoted ×10; preprocess should divide by 10."""
    data = {
        "uc_proxy": _series([7.0, 7.1], ["2020-01-02", "2020-01-03"]),
        "treasury_10y": _series([45.0, 47.0], ["2020-01-02", "2020-01-03"]),
    }
    panel = align_and_clean(data)
    # 45 / 10 = 4.5
    assert panel["treasury_10y"].iloc[0] == 4.5
    assert panel["treasury_10y"].iloc[1] == 4.7


def test_align_forward_fills_rates_only():
    """Rate-like series get ffilled; UC proxy (price-like) does not."""
    data = {
        "uc_proxy": _series([7.0, 7.1, 7.2], ["2020-01-02", "2020-01-03", "2020-01-06"]),
        "cgb_10y": _series([3.0, 3.1], ["2020-01-02", "2020-01-06"]),
    }
    panel = align_and_clean(data)
    # 2020-01-03 falls between cgb observations -> ffill picks 3.0
    assert panel.loc["2020-01-03", "cgb_10y"] == 3.0
    assert panel.loc["2020-01-06", "cgb_10y"] == 3.1


def test_align_drops_rows_missing_uc():
    """If UC proxy is missing on a business day, that row is dropped."""
    data = {
        "uc_proxy": _series([7.0, 7.2], ["2020-01-02", "2020-01-06"]),
        "dxy": _series([100.0, 100.5, 101.0], ["2020-01-02", "2020-01-03", "2020-01-06"]),
    }
    panel = align_and_clean(data)
    assert pd.Timestamp("2020-01-03") not in panel.index
