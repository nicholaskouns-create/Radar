"""Strict acquisition gate for Gao et al. raw ADC MATLAB frames.

Never synthesize missing IQ, infer labels from file names, or reshape ambiguous
arrays. Explicitly document the source's axis order before use.
"""
from pathlib import Path
import hashlib
import numpy as np
from scipy.io import loadmat

SHAPE = (128, 255, 4, 2)  # samples, chirps, receivers, transmitters


def inspect_frame(path, *, variable=None):
    """Return a verified ADC frame and its provenance, or fail closed.

    Gao's README gives axes (samples, chirps, receivers, transmitters).
    No TX combination or phase compensation is assumed here.
    """
    p = Path(path)
    raw = p.read_bytes()
    data = loadmat(p)
    candidates = [(k, v) for k, v in data.items()
                  if not k.startswith('__') and isinstance(v, np.ndarray)
                  and v.shape == SHAPE and np.iscomplexobj(v)]
    if variable is not None:
        candidates = [(k, v) for k, v in candidates if k == variable]
    if len(candidates) != 1:
        raise ValueError(f'Expected exactly one complex ADC tensor {SHAPE}; found {len(candidates)}')
    key, a = candidates[0]
    if not np.isfinite(a).all():
        raise ValueError('ADC contains non-finite samples')
    return a, {'sha256': hashlib.sha256(raw).hexdigest(), 'variable': key,
               'shape': list(a.shape), 'dtype': str(a.dtype),
               'phase_preserved': True, 'tx_handling': 'separate',
               'label_status': 'not_verified'}


def select_tx(cube, tx):
    """Use a single transmitter without unsupported TDM phase calibration."""
    a = np.asarray(cube)
    if a.shape != SHAPE or not np.iscomplexobj(a):
        raise ValueError('Expected verified complex Gao ADC tensor')
    if tx not in (0, 1):
        raise ValueError('Transmitter must be 0 or 1')
    return np.transpose(a[:, :, :, tx], (1, 0, 2))
