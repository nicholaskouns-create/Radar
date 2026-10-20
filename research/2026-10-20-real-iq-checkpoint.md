# Real I/Q acquisition checkpoint (2026-10-20)

## Verified
- Source: ACICULA/mocap2radar, `raw/v3/radar/DiagonalLong2Fast.csv`
- Acquisition run: https://github.com/nicholaskouns-create/Radar/actions/runs/39442077582
- Complex-value audit: https://github.com/nicholaskouns-create/Radar/actions/runs/39442317995
- SHA256: `197905b5ec4c4b8eaeb291ead3e9847a9696be2b6f5726047c7e18789dbcb00d`
- 229403 bytes, 14337 CSV rows including header, 14336 measured I/Q pairs.
- Columns: `Beacon`, ` I_payload`, `Q_payload`; 74 unique beacon values.
- Mean I = 2022.5772879464287; mean Q = 2014.0291573660713; RMS magnitude = 2869.3882380692385.
- Complex linearity / phase equivariance numerical error: 4.547473508864641e-13.

## Not yet verified
- I/Q offsets and signed-ADC calibration.
- Whether beacon groups identify repeated recordings or packets.
- Fast-time, chirp, antenna and transmit dimensions.
- Detection labels and recording-level group identities.
- A physically prespecified 125-coordinate encoding, range/Doppler/CFAR baseline comparability, or E47 ROC.

## Decision
This acquisition **does establish access to actual radar I/Q measurements**, a meaningful advance over metadata-only HDF5. It **does not** establish a calibrated FMCW cube or supervised radar detection dataset. Preserve Gate 1 as partially satisfied, Gates 2–5 empirically pending. Never use this sequence to claim measured object-detection AUC without labels.

Next single experiment: verify `Beacon` semantics and ADC calibration from authoritative dataset documentation, then either construct an appropriate phase-preserving mapping or acquire a labeled raw FMCW cube.
