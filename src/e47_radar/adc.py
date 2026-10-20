"""Physically indexed, phase-retaining fixed 5x5x5 radar feature map.

Input: complex radar cube (chirps, fast-time samples, receive channels).
Each axis is FFT transformed without discarding complex phase. A fixed
5x5x5 ROI in Doppler, range and receiver spatial-frequency bins is used.
This is an experimental encoding, not a proof of physical SU(2) spin-2.
"""
import numpy as np


def encode_cube(cube, *, range_start=1, doppler_center=0, antenna_start=0):
    a = np.asarray(cube)
    if a.ndim != 3 or not np.iscomplexobj(a):
        raise ValueError("Require complex ADC cube (chirps, samples, receivers)")
    if min(a.shape) < 5 or not np.isfinite(a).all():
        raise ValueError("At least five samples on each axis; finite data required")
    # FFT over fast-time and slow-time; antenna axis is spatial DFT.
    z = np.fft.fft(a, axis=1, norm="ortho")
    z = np.fft.fftshift(np.fft.fft(z, axis=0, norm="ortho"), axes=0)
    z = np.fft.fft(z, axis=2, norm="ortho")
    mid = z.shape[0] // 2 + doppler_center
    ds = slice(mid-2, mid+3)
    rs = slice(range_start, range_start+5)
    ants = slice(antenna_start, antenna_start+5)
    if ds.start < 0 or ds.stop > z.shape[0] or rs.start < 0 or rs.stop > z.shape[1] or ants.start < 0 or ants.stop > z.shape[2]:
        raise ValueError("Prespecified ROI outside radar cube")
    patch = z[ds, rs, ants]
    if patch.shape != (5, 5, 5):
        raise AssertionError("Incorrect ROI")
    return patch.reshape(125)


def baseline_scores(cube, *, guard=2, train=8):
    """Comparable same-frame unsupervised range power and CA-CFAR scores.

    Max range FFT power and maximum cell-to-averaged-training ratio.
    Both are frame-level proxy scores; not full target-localized CFAR.
    """
    a = np.asarray(cube)
    if a.ndim != 3 or not np.iscomplexobj(a):
        raise ValueError("Complex ADC cube required")
    p = np.abs(np.fft.fft(a, axis=1, norm="ortho"))**2
    power = p.mean(axis=(0, 2))
    n = len(power)
    if n < 2*(guard+train)+1:
        raise ValueError("Not enough range bins for CFAR window")
    ratio = []
    for k in range(train+guard, n-train-guard):
        reference = np.concatenate((power[k-guard-train:k-guard], power[k+guard+1:k+guard+train+1]))
        ratio.append(power[k]/max(reference.mean(), np.finfo(float).tiny))
    doppler = np.abs(np.fft.fftshift(np.fft.fft(a, axis=0, norm="ortho"), axes=0))**2
    return {
        "range_peak": float(np.max(power)),
        "ca_cfar_ratio": float(np.max(ratio)),
        "doppler_peak": float(np.max(doppler.mean(axis=(1, 2))))
    }
