# Measured acquisition audit: Rad-R synced HDF5

Date: 2026-10-20. Evidence: GitHub Actions run [39440716562](https://github.com/nicholaskouns-create/Radar/actions/runs/39440716562), artifact `measured-radr-acquisition-report`.

- Source: `https://huggingface.co/datasets/radr-anon-2026/radr/resolve/main/synced_hdf5/degrade0.h5`
- Bytes downloaded on GitHub runner: **3,521,664**
- SHA256 verified: `f4db4bbd4f5c7796093783a777428eb34504ccd2bc8dae51453f64ddd50af525`
- HDF5 dataset paths inspected: **47**
- Actual contents: timestamp/synchronization indices, GPS, IMU, camera paths, environmental measurements, and radar frame timestamps.
- **No complex IQ or ADC tensor found in this file.** The acquisition succeeded, but this exemplar cannot support E47 phase-preserving radar detection, range/Doppler/CFAR baselines, or measured AUC.

**Evidence boundary:** successful acquisition of real sensor metadata ≠ acquisition of complex radar measurements. The raw ADC files must be obtained from an authoritative source before testing detection hypotheses.

**Next acquisition choice:** Xiangyu Gao et al., *Raw ADC Data of 77GHz MMWave radar for Automotive Object Detection*, available via the project GitHub README's Google Drive / IEEE Dataport release. Expected raw frame: 128 fast-time samples × 255 chirps × 4 receivers × 2 transmitters, with per-frame object labels. This format is a plausible source for the prespecified 5×5×5 Doppler–range–spatial-frequency feature map (after documented TDM and virtual-array reconstruction). Do not apply that mapping until layout and IQ parsing have been independently checked.

**Alternative:** RADIal ADC binary source, with DBReader/HDR processing and 8,252 labeled frames; download/access is substantially larger.

**No measured ROC or detector-baseline performance is asserted.**
