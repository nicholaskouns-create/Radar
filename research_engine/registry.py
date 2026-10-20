"""Fail-closed evidence records shared across repositories."""
import hashlib
import json
from dataclasses import dataclass, asdict

LEVELS = {"candidate", "metadata_only", "real_iq_descriptive", "labeled_measured", "verified_benchmark"}

@dataclass(frozen=True)
class EvidenceRecord:
    run_id: str
    dataset_id: str
    producer: str
    algorithm: str
    algorithm_version: str
    evidence_level: str
    labels_verified: bool
    phase_preserved: bool
    result: dict

    def validate(self):
        if self.evidence_level not in LEVELS:
            raise ValueError("Unknown evidence level")
        if not all((self.run_id,self.dataset_id,self.producer,self.algorithm,self.algorithm_version)):
            raise ValueError("Missing required identity or version")
        if self.evidence_level in {"labeled_measured","verified_benchmark"} and not self.labels_verified:
            raise ValueError("Measured classification requires verified labels")
        if self.result.get("measured_auc") is not None:
            if not self.labels_verified or not self.phase_preserved or self.evidence_level not in {"labeled_measured","verified_benchmark"}:
                raise ValueError("Measured AUC requires verified labels, phase and evidence")
        return self

    def canonical_json(self):
        self.validate()
        return json.dumps(asdict(self),sort_keys=True,separators=(",",":"),allow_nan=False)

    def digest(self):
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()
