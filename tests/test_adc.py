import numpy as np
import pytest
from src.e47_radar.adc import encode_cube, baseline_scores


def test_complex_fft_phase_preserved():
    rng = np.random.default_rng(123)
    x = rng.normal(size=(16, 48, 8)) + 1j*rng.normal(size=(16, 48, 8))
    a = encode_cube(x)
    assert a.shape == (125,)
    assert np.iscomplexobj(a)
    # Complex linearity / phase equivariance of the complete map.
    phase = np.exp(1j*.73)
    assert np.allclose(encode_cube(phase*x), phase*a, atol=1e-12)
    assert np.max(np.abs(a.imag)) > 0


def test_phase_destruction_refused():
    with pytest.raises(ValueError):
        encode_cube(np.ones((16, 48, 8)))


def test_baseline_finite():
    rng = np.random.default_rng(7)
    x = rng.normal(size=(16, 48, 8)) + 1j*rng.normal(size=(16, 48, 8))
    s = baseline_scores(x)
    assert set(s) == {"range_peak", "ca_cfar_ratio", "doppler_peak"}
    assert all(np.isfinite(list(s.values())))


def test_roi_bounds_refused():
    with pytest.raises(ValueError):
        encode_cube(np.ones((16,48,8), dtype=complex), range_start=46)
