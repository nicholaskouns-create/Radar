# Radar

E47 × public radar reproducible benchmark. **Exact algebra, synthetic experiments, and measured-data results are separate evidence classes.** No measured AUC is claimed until real phase-preserving data and labels have been processed.

## Fixed formalism
H = V₂⊗³ (dim 125); C = J_total²; K = (C−6I)(C−30I); P = P₆+P₃₀ (rank 47); Γ = I−K²/99144. Occupancy η(x)=||Px||²/||x||². Complement residual rₙ(x)=||(I−P)Γⁿx||²/||x||².

## Data sources
- [RADIal](https://github.com/valeoai/RADIal): raw ADC, annotations; preferred primary measured object detection.
- [Gao raw ADC](https://github.com/Xiangyu-Gao/Raw_ADC_radar_dataset_for_automotive_object_detection): alternative labeled raw radar.
- [CRUW](https://www.cruwdataset.org/download): confirm released phase-preserving representation.
- [CARRADA](https://arthurouaknine.github.io/codeanddata/carrada): do not assume raw ADC is available.
- [Rad-R](https://huggingface.co/datasets/gtaxcenter/radr): robustness/fault labels, not automatically vehicle-detection labels.

No raw archives, API keys, or credentials in Git. Dataset downloads require license checks and checksum manifests. Large data belong in external object storage. GitHub Actions runs deterministic algebra tests, not unlimited large downloads.

## Run
```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m scripts.benchmark_grouped --input data/labeled_complex_125_grouped.npz --output results/run.json
```

Grouped NPZ requires complex x of shape (N,125), binary y of shape (N,), and recording identifiers groups of shape (N,). The older benchmark_npz.py uses a random split and is demonstration-only, not acceptable for measured claims. The mapping from measured ADC to these 125 complex features must be predeclared, label-blind, and physically justified. Arbitrary reshaping is not a validated encoding. NPZ benchmarks do not replace source-specific CA-CFAR and Doppler baselines on original radar cubes. Supabase stores provenance and small result metadata, not raw ADC.
## Acquisition gate status (2026-10-20)
- Rad-R synchronized metadata exemplar downloaded and checksum verified, but no ADC/IQ samples present. See `research/2026-10-20-radr-acquisition-audit.md`.
- Strict Gao MATLAB ADC validator: `src/e47_radar/gao.py`. It rejects real-valued, malformed, nonfinite, or ambiguous frames, preserves complex samples and records SHA-256. No source-specific labeled Gao frame has yet been obtained and passed this gate.
- `src/e47_radar/adc.py` provides a phase-equivariant *prototype* 5×5×5 encoding and frame-level range/CFAR/Doppler proxy scores. No measured E47 detector ROC is available.
- Gates 2–5 cannot be empirically completed before authentic labeled complex ADC passes Gate 1. Synthetic regression tests are not measured evidence.
