"""Tests for signal standardization and combination."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.factors import build_factors
from src.signals.combine import combine_signals, signal_to_position
from src.signals.model import zscore_factors


def test_zscore_clipping(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)
    # Flatten to non-NaN cells before asserting bound
    values = z.stack().dropna()
    assert values.abs().max() <= 3.0001


def test_zscore_no_lookahead():
    idx = pd.bdate_range("2020-01-01", periods=300)
    s = pd.DataFrame({"a": np.arange(300, dtype=float)}, index=idx)
    z_orig = zscore_factors(s, window=60, min_periods=20)
    s_mod = s.copy()
    s_mod.iloc[-50:] *= 100
    z_mod = zscore_factors(s_mod, window=60, min_periods=20)
    pd.testing.assert_frame_equal(
        z_orig.iloc[:-50], z_mod.iloc[:-50], check_exact=False,
    )


def test_combine_signals_returns_series(synthetic_panel, factor_config):
    factors = build_factors(synthetic_panel, factor_config)
    z = zscore_factors(factors, window=100, min_periods=20)
    composite = combine_signals(z, factor_config)
    assert isinstance(composite, pd.Series)
    assert composite.name == "signal"
    # After warmup the signal should be roughly bounded
    valid = composite.dropna()
    assert valid.abs().max() <= 3.0


def test_signal_to_position_proportional():
    s = pd.Series([0.5, -0.3, 2.0, -2.0, 0.0])
    p = signal_to_position(s, style="proportional")
    np.testing.assert_array_equal(p.values, [0.5, -0.3, 1.0, -1.0, 0.0])


def test_signal_to_position_sign_with_threshold():
    s = pd.Series([0.05, 0.5, -0.05, -0.5, 0.0])
    p = signal_to_position(s, style="sign", threshold=0.1)
    np.testing.assert_array_equal(p.values, [0.0, 1.0, 0.0, -1.0, 0.0])


def test_signal_to_position_proportional_hard_deadband():
    s = pd.Series([0.05, 0.15, 0.5, -0.25, -0.05, 0.0])
    p = signal_to_position(s, style="proportional", threshold=0.2, deadband_mode="hard")
    # |0.05| < 0.2 -> 0; |0.15| < 0.2 -> 0; 0.5 passes through; -0.25 passes through;
    np.testing.assert_array_equal(p.values, [0.0, 0.0, 0.5, -0.25, 0.0, 0.0])


def test_signal_to_position_proportional_soft_deadband():
    s = pd.Series([0.15, 0.2, 0.5, 1.0, -0.5, 0.0])
    p = signal_to_position(s, style="proportional", threshold=0.2, deadband_mode="soft")
    # below threshold => 0
    assert p.iloc[0] == 0.0
    # at threshold => 0
    assert p.iloc[1] == 0.0
    # 0.5 -> (0.5-0.2)/(1-0.2) = 0.375
    np.testing.assert_allclose(p.iloc[2], 0.375)
    # 1.0 -> (1-0.2)/(1-0.2) = 1.0
    np.testing.assert_allclose(p.iloc[3], 1.0)
    # -0.5 -> -(0.5-0.2)/(1-0.2) = -0.375
    np.testing.assert_allclose(p.iloc[4], -0.375)
    assert p.iloc[5] == 0.0


def test_signal_to_position_invalid_threshold():
    s = pd.Series([0.5])
    import pytest
    with pytest.raises(ValueError):
        signal_to_position(s, threshold=-0.1)
    with pytest.raises(ValueError):
        signal_to_position(s, threshold=1.0)


def test_signal_to_position_zero_threshold_unchanged():
    """threshold=0 must preserve legacy behavior exactly."""
    s = pd.Series([0.05, -0.3, 2.0, -2.0, 0.0])
    p_legacy = signal_to_position(s, style="proportional")
    p_zero = signal_to_position(s, style="proportional", threshold=0.0, deadband_mode="hard")
    p_zero_soft = signal_to_position(s, style="proportional", threshold=0.0, deadband_mode="soft")
    np.testing.assert_array_equal(p_legacy.values, p_zero.values)
    np.testing.assert_array_equal(p_legacy.values, p_zero_soft.values)
