"""Verify a Time quantum-clock receipt before binding it to repository evidence.

An SHA-256 digest detects accidental corruption but does NOT authenticate an
untrusted producer. This bridge never synthesizes a quantum-clock tick.
"""
import hashlib
import json
from pathlib import Path

CLOCK_SCHEMA = "city.quantum.clock-receipt.v1"

def canonical(value):
    """Sorted JSON for the subset of receipt fields with JSON-safe values.

    Cross-language floating-point canonicalization is not guaranteed for all
    values; compare the digest produced by the Time engine when possible.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def verify_clock_receipt(receipt):
    if not isinstance(receipt, dict) or receipt.get("schema") != CLOCK_SCHEMA:
        raise ValueError("Unsupported clock receipt schema")
    integrity = receipt.get("integrity")
    if not isinstance(integrity, dict) or integrity.get("algorithm") != "SHA-256":
        raise ValueError("Missing SHA-256 integrity")
    payload = {k: v for k, v in receipt.items() if k != "integrity"}
    digest = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    if digest != integrity.get("digest"):
        raise ValueError("Clock receipt digest mismatch")
    state = receipt.get("state")
    if not isinstance(state, dict) or not isinstance(state.get("dim"), int):
        raise ValueError("Missing clock density state")
    n = state["dim"]
    rho = state.get("density")
    if n <= 0 or n > 125 or not isinstance(rho, list) or len(rho) != n:
        raise ValueError("Invalid density shape")
    if any(not isinstance(row, list) or len(row) != n for row in rho):
        raise ValueError("Invalid density rows")
    for row in rho:
        for z in row:
            if not isinstance(z, list) or len(z) != 2 or any(
                not isinstance(v, (float, int)) or isinstance(v, bool) for v in z
            ):
                raise ValueError("Invalid complex amplitude")
    # The authoritative Time engine performs the PSD/trace/Hermitian test.
    return {"schema": CLOCK_SCHEMA, "sha256": digest, "integrity": "digest-only",
            "clock_status": "unattested", "physical_time_attested": False}

def bind_receipt(path, repository, commit_sha):
    receipt = json.loads(Path(path).read_text())
    verified = verify_clock_receipt(receipt)
    return {"schema": "e47-clock-cross-domain-binding-v1",
            "repository": repository, "commit_sha": commit_sha,
            "clock_receipt_sha256": verified["sha256"],
            "clock_receipt_schema": verified["schema"],
            "clock_status": "unattested",
            "physical_time_attested": False}
