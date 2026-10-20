import pytest
from research_engine.registry import EvidenceRecord

def make(**updates):
    args = dict(run_id="r1", dataset_id="acicula-iq-v3", producer="Radar",
        algorithm="e47", algorithm_version="abc123", evidence_level="real_iq_descriptive",
        labels_verified=False, phase_preserved=True, result={"measured_auc":None})
    args.update(updates)
    return EvidenceRecord(**args)

def test_descriptive():
    assert len(make().digest()) == 64

def test_auc_rejected_without_labels():
    with pytest.raises(ValueError):
        make(result={"measured_auc":0.9}).validate()

def test_verified_labels_required():
    with pytest.raises(ValueError):
        make(evidence_level="verified_benchmark").validate()

def test_verified():
    assert make(evidence_level="verified_benchmark", labels_verified=True,
                result={"measured_auc":0.7}).validate()
