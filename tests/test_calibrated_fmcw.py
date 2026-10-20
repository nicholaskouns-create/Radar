import numpy as np
import pytest
from src.e47_radar.calibrated_fmcw import (
    validate_ground_truth,range_doppler,cfar_2d,match_targets
)

CAL=dict(sample_rate_hz=2e6,slope_hz_s=2e12,chirp_interval_s=1e-3,wavelength_m=.004)

def test_unverified_truth_rejected():
    with pytest.raises(ValueError):
        validate_ground_truth([],n_samples=64,n_chirps=32,
                              range_tolerance_m=2,velocity_tolerance_m=.5,**CAL)
    with pytest.raises(ValueError):
        validate_ground_truth([dict(range_m=10,radial_velocity_m_s=1)],
                              n_samples=64,n_chirps=32,
                              range_tolerance_m=2,velocity_tolerance_m=.5,**CAL)

def test_fft_axes_and_nominal_threshold():
    cube=np.zeros((32,64,5),dtype=complex)
    cube[:, :, :]=np.exp(2j*np.pi*(4*np.arange(64)[None,:,None]/64+
                                    3*np.arange(32)[:,None,None]/32))
    power,r,v=range_doppler(cube,**CAL)
    assert power.shape==(32,32)
    assert np.unravel_index(np.argmax(power),power.shape)==(19,4)
    assert np.isclose(r[4],4*CAL["sample_rate_hz"]/64*299792458/(2*CAL["slope_hz_s"]))
    assert np.isclose(v[19],3/32/CAL["chirp_interval_s"]*CAL["wavelength_m"]/2)
    out=cfar_2d(power,guard=(1,1),train=(2,2),pfa=.001)
    assert out["threshold_ratio"]>1
    assert out["detections"].shape==power.shape

def test_target_match_is_not_false_alarm_claim():
    det=np.zeros((32,32),bool);det[19,4]=True
    truth=[dict(recording_id="physical-001",range_m=4*CAL["sample_rate_hz"]/64*299792458/(2*CAL["slope_hz_s"]),
                radial_velocity_m_s=3/32/CAL["chirp_interval_s"]*CAL["wavelength_m"]/2,
                source="independent_calibration")]
    assert validate_ground_truth(truth,n_samples=64,n_chirps=32,range_tolerance_m=1,velocity_tolerance_m=.1,**CAL)
    rr=np.arange(32)*CAL["sample_rate_hz"]/64*299792458/(2*CAL["slope_hz_s"])
    vv=np.fft.fftshift(np.fft.fftfreq(32,d=CAL["chirp_interval_s"]))*CAL["wavelength_m"]/2
    result=match_targets(det,rr,vv,truth,range_tolerance_m=1,velocity_tolerance_m=.1)
    assert result["hits"]==1
    assert isinstance(result["false_alarm_rate"],str)
