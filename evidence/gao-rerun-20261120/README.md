# Measured Gao range-cell pilot

66 frames from 22 recordings; held-out dates.

| Added noise power fraction | Conventional AUC | E47 joint AUC | Conventional + E47 AUC | Incremental 95% CI |
|---|---|---|---|---|
| 0.0 | 0.803744 | 0.529095 | 0.802728 | [-0.00352006436689134, 0.0030864197530864335] |
| 0.1 | 0.767200 | 0.534172 | 0.767788 | [-0.003156116642958673, 0.00444576170717248] |
| 1.0 | 0.663032 | 0.519902 | 0.659411 | [-0.00871999999999995, 0.0027415530527563625] |

Scope: source-annotated range-cell comparison. See result.json for all limitations and scores.

The acquisition gate independently checked the complex 128 × 255 × 4 × 2 ADC frame for recording `2019_04_09_bms1000`, matched it to the published coordinate annotation by recording and numeric frame identifier, and saved both checksums. The complete rerun preserved 66 matched frame/label pairs from 22 recordings. Five recordings from the held-out date supply the test set. The bundle records frame provenance and scores.

The bootstrap intervals for each added-noise condition include zero. The comparison uses annotation-derived range cells and simulated added noise. Independent object-level and velocity validation remain open. This reproduces the scope of the earlier [successful empirical workflow](https://github.com/nicholaskouns-create/Radar/actions/runs/39456451573).
