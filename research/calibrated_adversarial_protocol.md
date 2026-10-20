# E47 versus calibrated FMCW: adversarial evaluation protocol

**Status:** protocol and baseline code implemented; calibrated labeled physical ADC not yet obtained. No measured detection threshold, Pd, Pfa, ROC or AUC is claimed.

## 1. Freeze the conventional baseline

Input must be raw complex FMCW ADC with axes (chirps, fast-time samples, receivers) and authoritative sample rate, chirp slope, chirp interval, carrier wavelength, antenna configuration and hardware calibration. The implementation in `src/e47_radar/calibrated_fmcw.py` computes windowed range-Doppler power and 2-D CA-CFAR with predeclared guard/training cells and design Pfa. This is an initial baseline, **not** a complete production radar chain: interference rejection, clutter suppression, TDM-MIMO corrections, angle estimation, peak consolidation, and empirical calibration remain outstanding. Verify range/velocity sign conventions on a known reflector. Lock threshold and all hyperparameters using calibration/training recordings only. Measure empirical false alarms on independent negative scenes.

## 2. Independent physical ground truth

Require per-target independently measured range (m), radial velocity (m/s), recording ID and source; also independently defined tolerances, acquisition timestamps and time alignment. Source annotations alone are not automatically independent physical metrology. Enforce train/test split by physical recording/session and prohibit adjacent-frame leakage. For multiple targets, establish one-to-one matching and explicit clutter-only negative regions before computing Pd or Pfa.

## 3. Adversarial, paired E47 evaluation

Apply the fixed `encode_cube` ROI only if it is physically justified, specified **before** labels are examined, and remains identical across groups. Use fixed `P=P6+P30`, `Gamma=I-K²/99144`, occupancy `eta` and residual `r_n`. Do not tune E47 basis or depth on held-out test data. For each SNR stratum, feed **identical** phase-preserving noisy ADC realizations to conventional and E47 processing. Use the same physical detections, target matching, split, SNR bins and test recordings. Thresholds and any logistic combination are fitted on training/validation only. Compare empirical Pd at matched Pfa, ROC/PR curves, range and velocity error, and recording-cluster bootstrap uncertainty. Include occupancy-only, residual-only, joint and conventional baselines, plus a conventional+E47 incremental model. Log counterexamples and negative results.

### Hard gates

- Missing calibrated FMCW ADC => no conventional physical threshold.
- Missing independent range/velocity => no verified detection benchmark.
- Missing target-negative regions => no empirical Pfa.
- Missing prespecified phase-preserving 125-feature map => no physical E47 comparison.
- Missing matched held-out SNR trials => no incremental detection claim.

**Reproducibility:** preserve source URL/license/checksum, acquisition settings, instrument calibration, preprocessing code SHA, physical label provenance, recording-level split, fixed hyperparameters, result JSON and private raw-data pointers. Never publish raw ADC to GitHub or the public metadata API.
