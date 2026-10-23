import hashlib
import json
import pytest
from src.e47_radar.clock_bridge import canonical, verify_clock_receipt, bind_receipt

def make_receipt():
    x = {"schema": "city.quantum.clock-receipt.v1",
         "state": {"dim": 1, "density": [[[1, 0]]]}}
    x["integrity"] = {"algorithm": "SHA-256",
                      "digest": hashlib.sha256(canonical(x).encode()).hexdigest()}
    return x

def test_valid_receipt_is_not_attested():
    assert verify_clock_receipt(make_receipt())["clock_status"] == "unattested"

def test_tampering_rejected():
    x = make_receipt()
    x["state"]["density"][0][0][0] = 0
    with pytest.raises(ValueError, match="digest mismatch"):
        verify_clock_receipt(x)

def test_binding(tmp_path):
    p = tmp_path / "clock.json"
    p.write_text(json.dumps(make_receipt()))
    b = bind_receipt(p, "nicholaskouns-create/Radar", "abc")
    assert b["clock_receipt_sha256"] == make_receipt()["integrity"]["digest"]
    assert b["physical_time_attested"] is False
