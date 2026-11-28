> ⚛️ **[E₄₇ Φ₄ LIVE QUANTUM CIRCUIT](https://nicholaskouns-create.github.io/qsvt-phi4/)** · [Full 125D → 250D → 500D circuit](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/qsvt-phi4-circuit/) · [Exact complementary factorization + reproducible NumPy certificate](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/research/e47/qsp_phi4). Shared derivation; no independent application benchmark inferred.

# Radar

## Optical Geometry × KKP-RADAR Educational Atlas

[Launch the integrated optical–radar laboratory](https://nicholaskouns-create.github.io/Radar/optical-radar-atlas/) · [Standalone source](optical-radar-atlas/index.html) · [E₄₇ spectral bridge](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-radar-bridge/).

Mobile-first, offline-capable browser laboratory with six optical geometry lessons plus six synthetic radar primers (moving echo, multipath, phase, clutter/CA-CFAR proxy, negative-space mapping, and seven-shell E₄₇). The radar engine processes procedurally generated complex I/Q patches using the unchanged 125-dimensional triple-spin-2 Casimir operator. Includes range–Doppler, phase/coherence/gradient/curvature, spectral shells, CFAR proxy, telemetry and local self-tests. Educational simulated data only; no measured detection performance is claimed.

Research documentation: [KKP-RADAR concept proposal](https://docs.google.com/document/d/1cTyRJIj5FR9_afL3KWm9JMAiF_1T3fCVqmOBPLpmhbo/edit) · [Phase-retaining ADC prototype](src/e47_radar/adc.py).


> **Current license:** [All Rights Reserved](LICENSE) for owned original material. No new reuse permission. Earlier licenses and third-party/public-domain rights remain unaffected.


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

[The E₄₇ spectral kernel · formalism and verification](e47-spectral-kernel/README.md)


<!-- FUN-WITH-EINSTEIN-2026 -->
### 🪐 Fun With Einstein · Interactive spectral & quantum lab

[Launch Fun With Einstein](https://nicholaskouns-create.github.io/fun-with-einstein/) · [Source & Python/Lean/Coq proof modules](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/docs/fun-with-einstein) · [CI compiler status](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/fun-with-einstein.yml).

Fivefold C₅ eigenvalue ratio = φ⁻²; 125D Casimir E₄₇ projector; 250D quantum-ancilla probability α=47/(125φ²); stationary Einstein-equation recovery. Spectral simulation and gravitational statements have different evidence classes.
<!-- /FUN-WITH-EINSTEIN-2026 -->


---

### E₄₇ · Computed spectral geometry

[Open the interactive E₄₇ visualizer](./e47-geometry/index.html) · [GitHub Pages instrument](https://nicholaskouns-create.github.io/Radar/e47-geometry/)

Additive, mobile-friendly 125-site 3D projector-density lattice, five exact rational density slices, seven SU(2) spectral sectors, minimax contraction and five-stage polynomial projection. The 3D embedding is a coordinate visualization of the invariant spectral subspace, not a physical solid.


<!-- ΩBA-PROOF-LINK-20261124 -->
### ΩBA · First-Principles Triadic Contraction and E₄₇ Continuity

[**Open the light-mode interactive ΩBA proof plate**](https://nicholaskouns-create.github.io/omega-ba/) · [Local Unicode derivation](omega-ba/README.md) · [Executable NumPy validation](omega-ba/omega_ba_validation.py) · [Local interactive page](omega-ba/index.html).

A mathematical three-stage alignment → binding → commitment map (𝒪=A∘B∘Ω), Banach strict-contraction proof with explicit assumptions, and a distinct E₄₇ spectral complement contraction (125→47, rate 15/17). Python tests and evidence boundaries are supplied; acoustic, biological and retrocausal effects are not asserted.
<!-- /ΩBA-PROOF-LINK-20261124 -->
