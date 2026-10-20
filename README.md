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
python scripts/benchmark_npz.py --input data/labeled_complex_125.npz --output results/run.json
```

NPZ requires complex x of shape (N,125) and binary y of shape (N,). The mapping from measured ADC to these 125 complex features must be predeclared, label-blind, and physically justified. Arbitrary reshaping is not a validated encoding. NPZ benchmarks do not replace source-specific CA-CFAR and Doppler baselines on original radar cubes. Supabase stores provenance and small result metadata, not raw ADC.