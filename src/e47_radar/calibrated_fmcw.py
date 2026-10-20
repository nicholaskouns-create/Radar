"""Calibrated FMCW range-Doppler CA-CFAR baseline and ground-truth gate.

This module never fabricates calibration, target labels or detection results.
"""
import numpy as np

C0 = 299792458.0


def validate_ground_truth(targets, *, sample_rate_hz, slope_hz_s, chirp_interval_s,
                          wavelength_m, n_samples, n_chirps, range_tolerance_m,
                          velocity_tolerance_m):
    """Require independently measured range/velocity, recording ID, and calibration."""
    calibration = (sample_rate_hz, slope_hz_s, chirp_interval_s, wavelength_m,
                   range_tolerance_m, velocity_tolerance_m)
    if not all(np.isfinite(v) and v > 0 for v in calibration):
        raise ValueError("Positive, finite physical calibration and tolerances required")
    if n_samples < 32 or n_chirps < 8:
        raise ValueError("Insufficient fast/slow-time samples")
    if not targets:
        raise ValueError("Independent physical ground truth required")
    for target in targets:
        required = ("recording_id", "range_m", "radial_velocity_m_s", "source")
        if not all(k in target for k in required):
            raise ValueError("Ground truth requires recording ID, range, radial velocity, source")
        if not str(target["source"]).strip() or not str(target["recording_id"]).strip():
            raise ValueError("Ground-truth provenance and recording identity required")
        if not np.isfinite(target["range_m"]) or target["range_m"] < 0 or not np.isfinite(target["radial_velocity_m_s"]):
            raise ValueError("Nonfinite or negative physical ground truth")
    return True


def range_doppler(cube, *, sample_rate_hz, slope_hz_s, chirp_interval_s, wavelength_m):
    """Windowed, coherent FFT; cube axes: chirps, ADC samples, receivers.

    No clutter removal, antenna beamforming, range migration, or TDM-MIMO correction.
    """
    a = np.asarray(cube)
    if a.ndim != 3 or not np.iscomplexobj(a) or min(a.shape) < 2 or not np.isfinite(a).all():
        raise ValueError("Finite complex ADC cube (chirps,samples,receivers) required")
    if not all(np.isfinite(v) and v > 0 for v in (sample_rate_hz,slope_hz_s,chirp_interval_s,wavelength_m)):
        raise ValueError("Physical calibration required")
    nc,ns,_ = a.shape
    window = np.hanning(nc)[:,None,None] * np.hanning(ns)[None,:,None]
    spectrum = np.fft.fftshift(np.fft.fft(np.fft.fft(a*window,axis=1),axis=0),axes=0)
    spectrum = spectrum[:, :ns//2, :]
    power = np.mean(np.abs(spectrum)**2,axis=2)
    ranges = np.arange(ns//2) * sample_rate_hz / ns * C0 / (2*slope_hz_s)
    velocities = np.fft.fftshift(np.fft.fftfreq(nc,d=chirp_interval_s)) * wavelength_m/2
    return power,ranges,velocities


def cfar_2d(power, *, guard=(1,1), train=(4,4), pfa=1e-3):
    """Cell-averaging CFAR, rectangular training ring, exponential-noise alpha."""
    p=np.asarray(power,dtype=float)
    if p.ndim!=2 or not np.isfinite(p).all() or np.any(p<0):
        raise ValueError("Nonnegative finite range-Doppler power required")
    if not (0<pfa<1) or any(not isinstance(v,int) or v<0 for v in (*guard,*train)) or not all(v>0 for v in train):
        raise ValueError("Invalid CFAR configuration")
    gy,gx=guard;ty,tx=train
    hy,hx=gy+ty,gx+tx
    if p.shape[0]<=2*hy or p.shape[1]<=2*hx:
        raise ValueError("Insufficient cells for training")
    ring=np.ones((2*hy+1,2*hx+1),dtype=bool)
    ring[hy-gy:hy+gy+1,hx-gx:hx+gx+1]=False
    n=int(ring.sum())
    alpha=n*(pfa**(-1/n)-1)
    scores=np.full(p.shape,np.nan)
    detections=np.zeros(p.shape,dtype=bool)
    for y in range(hy,p.shape[0]-hy):
        for x in range(hx,p.shape[1]-hx):
            refs=p[y-hy:y+hy+1,x-hx:x+hx+1][ring]
            noise=refs.mean()
            ratio=p[y,x]/max(noise,np.finfo(float).tiny)
            scores[y,x]=ratio
            detections[y,x]=ratio>alpha
    return {"scores":scores,"detections":detections,"threshold_ratio":float(alpha),
            "training_cells":n,"pfa_design":pfa,
            "caveat":"Nominal Pfa assumes independent exponential reference cells; windowing and clutter may violate it."}


def match_targets(detections, ranges, velocities, targets, *, range_tolerance_m, velocity_tolerance_m):
    """Count physical target matches; report misses, without inferring negatives."""
    hits=[]
    for t in targets:
        within_r=np.abs(ranges-t["range_m"])<=range_tolerance_m
        within_v=np.abs(velocities-t["radial_velocity_m_s"])<=velocity_tolerance_m
        hits.append(bool(np.any(detections[np.ix_(within_v,within_r)])))
    return {"target_count":len(targets),"hits":int(sum(hits)),"misses":len(hits)-int(sum(hits)),
            "false_alarm_rate":"unavailable_without_independent_negative_regions"}
