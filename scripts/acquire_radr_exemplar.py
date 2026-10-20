"""Acquire a bounded public Rad-R HDF5 exemplar, inspect its schema, never infer IQ."""
import hashlib
import json
import os
from pathlib import Path
from urllib.request import urlopen, Request

URL = "https://huggingface.co/datasets/radr-anon-2026/radr/resolve/main/synced_hdf5/degrade0.h5"
EXPECTED_SHA256 = "f4db4bbd4f5c7796093783a777428eb34504ccd2bc8dae51453f64ddd50af525"
MAX_BYTES = 8_000_000

def main():
    import h5py
    import numpy as np
    dest = Path("data/radr_degrade0.h5")
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = Request(URL, headers={"User-Agent": "E47-Radar-reproducibility/1.0"})
    count = 0
    digest = hashlib.sha256()
    with urlopen(request, timeout=45) as response, dest.open("wb") as f:
        while True:
            block = response.read(65536)
            if not block:
                break
            count += len(block)
            if count > MAX_BYTES:
                raise RuntimeError("Exceeded hard byte budget")
            digest.update(block)
            f.write(block)
    if digest.hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("Public source checksum mismatch; aborting")
    inventory = []
    with h5py.File(dest, "r") as f:
        def visit(name, obj):
            if isinstance(obj, h5py.Dataset):
                inventory.append({"path": name, "shape": list(obj.shape), "dtype": str(obj.dtype), "is_complex": bool(np.issubdtype(obj.dtype, np.complexfloating))})
        f.visititems(visit)
    result = {
        "source": URL, "sha256": digest.hexdigest(), "bytes": count,
        "evidence": "measured_file_acquired_schema_only",
        "license_claim": "CC-BY-4.0 per dataset card; attribution required",
        "inventory": inventory,
        "phase_preserving_adc_confirmed": False,
        "auc_measured": None,
        "note": "HDF5 schema alone does not establish raw IQ availability, label validity, or 125-dimensional mapping."
    }
    Path("acquisition_report.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
