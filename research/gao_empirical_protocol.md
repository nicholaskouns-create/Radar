# Gao measured range-cell comparison — protocol frozen before scoring

Source: Gao et al., Raw ADC Data of 77GHz MMWave Radar for Automotive Object Detection, DOI 10.21227/xm40-jx59, authors' public Automotive.zip. Cite Gao et al., RAMP-CNN, IEEE Sensors Journal (2021), DOI 10.1109/JSEN.2020.3036047. Source configuration: 4 MHz sample rate, 21 MHz/us slope, 128 fast-time samples. ADC shape (128,255,4,2), complex. Pair frames and coordinate annotations by integer filename stem, accommodating zero padding.

Acquire three evenly spaced matched frames per recording (25%, 50%, 75% of matched indices), across all 22 listed recordings. No frame selection by scores. Dates 2019-04-09 and 2019-04-30 train; 2019-05-09 validation; 2019-05-29 test. All frames of each recording stay together.

Fixed linear map: transmitter 0, receiver 0, chirps [0,63,127,191,254], fast-time indices 0..124. Hann-window these 125 samples. For each range bin k=1..111, de-rotate by exp(-2*pi*i*k*n/128); flatten the 125 chronological samples directly in the existing E47 computational basis. No basis, depth, or frequency-sign selection using test labels. Compute occupancy and depth-2 residual on each vector, then average over the five chirps. Full range FFT and reference cells use this identical 125-sample window, zero-padded to 128. No TDM receiver/antenna mixing.

Baseline scores: mean coherent matched-filter power across five chirps; CA-CFAR ratio with guard=3, training=8 each side; fixed logistic combination of log power and log CFAR. E47 scores: occupancy, residual, fixed logistic joint model. Incremental model: conventional features plus E47. Directions for single E47 scores and standardization/logistic parameters learned on train only; logistic C=1, max_iter=3000, seed=47. Thresholds set at the 95th percentile of validation annotation-negative cells.

Annotation positives: range-bin centers within 0.45 m of any annotated object center hypot(x,y). Ambiguous cells within the annotated bounding rectangle's radial envelope plus 0.45 m are excluded unless positive. Remaining cells are annotation-negative, not independently certified empty space. Only finite CA-CFAR interior cells with range <=25 m are evaluated.

Paired conditions: measured samples without injected noise, and complex Gaussian noise with power 0.1 or 1.0 times each frame's selected-sample mean power. These are added-noise power ratios, NOT measured target SNR. Same realization and global phase rotation enter all methods.

Report held-out range-cell ROC AUC/AP, validation-calibrated test TPR/FPR, per-recording scores, and paired recording bootstrap (1000 draws) 95% intervals for incremental AUC. Labels remain source annotations; independent metrology, velocity truth, exhaustive clutter labeling, object-level Pd/Pfa, and new hardware capture are not asserted. Do not claim generalized detector superiority from this pilot.

Archive checksum each acquired frame and label; retain derived scores and result JSON as workflow artifacts. Do not upload raw ADC to GitHub. Integration needs no Supabase credential.
