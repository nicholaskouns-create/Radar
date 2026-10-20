import numpy as np
import pytest
from scipy.io import savemat
from src.e47_radar.gao import SHAPE, inspect_frame, select_tx


def test_real_mat_rejected(tmp_path):
    p = tmp_path/'frame.mat'
    savemat(p, {'adc': np.zeros(SHAPE, dtype=float)})
    with pytest.raises(ValueError):
        inspect_frame(p)


def test_complex_mat_phase_and_hash(tmp_path):
    p = tmp_path/'frame.mat'
    a = np.zeros(SHAPE, dtype=np.complex64)
    a[2, 3, 1, 0] = 3 + 4j
    savemat(p, {'adc': a})
    b, provenance = inspect_frame(p)
    assert provenance['phase_preserved'] and len(provenance['sha256']) == 64
    assert np.array_equal(a, b)
    c = select_tx(b, 0)
    assert c.shape == (255, 128, 4)
    assert c[3, 2, 1] == 3+4j


def test_ambiguous_variables_rejected(tmp_path):
    p = tmp_path/'frame.mat'
    a = np.zeros(SHAPE, dtype=np.complex64)
    savemat(p, {'adc': a, 'copy': a})
    with pytest.raises(ValueError):
        inspect_frame(p)
