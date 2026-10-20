"""Label-honest E47 comparative evaluation with recording-group isolation."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.e47_radar.spectral import statistics


def evaluate(x, y, groups, *, depth=2, seed=47, test_size=.3):
    """Use recording IDs for a held-out test; directions fitted on train only."""
    x = np.asarray(x)
    y = np.asarray(y)
    groups = np.asarray(groups)
    if len(x) != len(y) or groups.shape != y.shape:
        raise ValueError("x, y, and recording groups must align")
    if y.ndim != 1 or not np.isin(y, (0, 1)).all():
        raise ValueError("Binary y required")
    if depth < 1 or not isinstance(depth, int):
        raise ValueError("Positive integer depth required")
    if len(np.unique(groups)) < 4:
        raise ValueError("At least four recording groups required")
    s = statistics(x, (depth,))
    features = np.column_stack((s["eta"], s[f"r{depth}"]))
    split = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train, test = next(split.split(features, y, groups))
    if len(np.unique(y[train])) < 2 or len(np.unique(y[test])) < 2:
        raise ValueError("Both classes required on train and test; adjust recording groups")
    if set(groups[train]) & set(groups[test]):
        raise AssertionError("Recording leakage")
    direction = 1. if np.mean(features[train][y[train] == 1, 0]) >= np.mean(features[train][y[train] == 0, 0]) else -1.
    joint = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, random_state=seed))
    joint.fit(features[train], y[train])
    # Residual alone learns the sign from the TRAIN portion.
    residual_dir = 1. if np.mean(features[train][y[train] == 1, 1]) >= np.mean(features[train][y[train] == 0, 1]) else -1.
    return {
        "evidence": "unverified_dataset_provenance",
        "depth": depth, "seed": seed,
        "split": "held_out_recording_groups",
        "n_train": len(train), "n_test": len(test),
        "n_train_groups": len(np.unique(groups[train])),
        "n_test_groups": len(np.unique(groups[test])),
        "group_overlap_count": len(set(groups[train]) & set(groups[test])),
        "auc_occupancy": float(roc_auc_score(y[test], direction * features[test, 0])),
        "auc_residual": float(roc_auc_score(y[test], residual_dir * features[test, 1])),
        "auc_joint_logistic": float(roc_auc_score(y[test], joint.predict_proba(features[test])[:, 1])),
        "not_performed": ["CA-CFAR", "Doppler threshold", "phase provenance validation", "uncertainty interval"],
        "interpretation": "Measured claim requires externally verified recording provenance, labels and predeclared ADC-to-125 mapping."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--seed", type=int, default=47)
    a = parser.parse_args()
    with np.load(a.input, allow_pickle=False) as z:
        if not {"x", "y", "groups"} <= set(z.files):
            raise ValueError("NPZ requires complex x (N,125), binary y, and recording groups")
        x, y, groups = z["x"], z["y"], z["groups"]
    result = evaluate(x, y, groups, depth=a.depth, seed=a.seed)
    result["sha256_input"] = hashlib.sha256(Path(a.input).read_bytes()).hexdigest()
    result["source_file"] = str(a.input)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
