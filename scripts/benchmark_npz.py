"""Run an honest labeled, complex-feature benchmark; never manufacture measurements."""
import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from src.e47_radar.spectral import statistics

def run(path, depth=2, seed=47):
    with np.load(path, allow_pickle=False) as data:
        if set(("x", "y")) - set(data.files):
            raise ValueError("NPZ requires x (complex N×125) and y (binary N)")
        x, y = data["x"], data["y"]
    if x.ndim != 2 or x.shape[1] != 125 or not np.iscomplexobj(x):
        raise ValueError("Phase-preserving complex input (N,125) required")
    if y.shape != (len(x),) or not np.isin(y, [0, 1]).all():
        raise ValueError("Binary labels y required")
    if len(np.unique(y)) != 2 or np.min(np.bincount(y.astype(int))) < 4:
        raise ValueError("At least 4 observations per class required")
    s = statistics(x, (depth,))
    a, b = train_test_split(np.arange(len(y)), test_size=.3, stratify=y, random_state=seed)
    scores = np.column_stack((s["eta"], s[f"r{depth}"]))
    # Occupancy orientation learned only from train split.
    direction = 1 if np.mean(scores[a[y[a] == 1], 0]) >= np.mean(scores[a[y[a] == 0], 0]) else -1
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed))
    model.fit(scores[a], y[a])
    result = {
        "source": str(path), "evidence": "measured_only_if_source_provenance_verified",
        "n_samples": int(len(y)), "n_test": int(len(b)), "depth": int(depth),
        "seed": int(seed), "split": "stratified_random_not_group_or_sequence_safe",
        "auc_occupancy": float(roc_auc_score(y[b], direction * scores[b, 0])),
        "auc_joint_logistic": float(roc_auc_score(y[b], model.predict_proba(scores[b])[:, 1])),
        "caution": "No CA-CFAR or Doppler baseline. No provenance validation. Correlated frames require grouped split."
    }
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--depth", type=int, default=2)
    args = p.parse_args()
    result = run(args.input, args.depth)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
