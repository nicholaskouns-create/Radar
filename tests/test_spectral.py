import numpy as np
import pytest
from src.e47_radar.spectral import operators, statistics

def test_fixed_operator():
    C, K, P, Gamma, shells = operators()
    assert C.shape == (125, 125)
    assert abs(np.trace(P).real - 47) < 1e-8
    assert np.linalg.norm(P @ P - P) < 1e-10
    assert np.linalg.norm(K @ P) < 1e-8
    assert np.linalg.norm(Gamma @ P - P) < 1e-8
    assert abs(np.linalg.norm(Gamma - P, 2) - 15/17) < 1e-8
    assert [round(np.trace(shells[c]).real) for c in (0,2,6,12,20,30,42)] == [1,9,25,28,27,22,13]

def test_fixed_occupancy_separation():
    _, _, P, _, shells = operators()
    def unit_in_projector(p):
        w, v = np.linalg.eigh(p)
        return v[:, np.argmax(w)]
    v = unit_in_projector(P)
    u0 = unit_in_projector(shells[0])
    u12 = unit_in_projector(shells[12])
    eta = 47/125
    a = np.sqrt(eta)*v + np.sqrt(1-eta)*u12
    b = np.sqrt(eta)*v + np.sqrt(1-eta)*u0
    out = statistics(np.stack([a,b]), (0,1,2))
    assert np.allclose(out["eta"], eta, atol=1e-10)
    assert np.allclose(out["r0"], 1-eta, atol=1e-10)
    assert out["r1"][0] > out["r1"][1]
    assert out["r2"][0] > out["r2"][1]

def test_reject_real_inputs():
    with pytest.raises(ValueError):
        statistics(np.ones((2,125)))
