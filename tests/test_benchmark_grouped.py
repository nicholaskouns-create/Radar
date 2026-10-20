import numpy as np
import pytest
from scripts.benchmark_grouped import evaluate
from src.e47_radar.spectral import operators


def _synthetic(seed=3):
    """Constructed spectral populations, not measured radar data."""
    rng = np.random.default_rng(seed)
    _, _, p, _, shells = operators()
    w, v = np.linalg.eigh(p)
    u = v[:, np.argmax(w)]
    w, v = np.linalg.eigh(shells[0])
    u0 = v[:, np.argmax(w)]
    w, v = np.linalg.eigh(shells[12])
    u12 = v[:, np.argmax(w)]
    # Both classes have the exact same occupancy.
    x = np.stack([np.sqrt(.376)*u + np.sqrt(.624)*(u12 if i % 2 else u0)
                  for i in range(80)])
    y = np.arange(80) % 2
    groups = np.arange(80) // 4
    # Groups each contain both classes, unlike a class-correlated grouping.
    return x, y, groups


def test_group_isolation_and_residual_information():
    x, y, groups = _synthetic()
    r = evaluate(x, y, groups, seed=47)
    assert r["group_overlap_count"] == 0
    assert abs(r["auc_occupancy"] - .5) < .05
    assert r["auc_residual"] > .99
    assert r["auc_joint_logistic"] > .99
    assert r["evidence"] == "unverified_dataset_provenance"


def test_insufficient_groups_refused():
    x, y, _ = _synthetic()
    with pytest.raises(ValueError):
        evaluate(x, y, np.zeros(len(y), dtype=int))


def test_missing_test_class_refused():
    x, y, g = _synthetic()
    with pytest.raises(ValueError):
        evaluate(x, np.zeros(len(y), dtype=int), g)
