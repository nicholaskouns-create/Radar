"""Audit real ACICULA I/Q measurements without inventing radar cube axes."""
import csv
import hashlib
import io
import json
import numpy as np
from pathlib import Path
from urllib.request import urlopen

URL = "https://huggingface.co/datasets/ACICULA/mocap2radar/resolve/main/raw/v3/radar/DiagonalLong2Fast.csv"
SHA256 = "197905b5ec4c4b8eaeb291ead3e9847a9696be2b6f5726047c7e18789dbcb00d"

def parse_iq(raw):
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    if not rows or set(rows[0]) != {'Beacon',' I_payload','Q_payload'}:
        raise ValueError('Unexpected real I/Q CSV columns')
    beacon = np.asarray([int(r['Beacon']) for r in rows], dtype=np.int64)
    i = np.asarray([float(r[' I_payload']) for r in rows])
    q = np.asarray([float(r['Q_payload']) for r in rows])
    z = i + 1j*q
    if not np.isfinite(z).all():
        raise ValueError('Nonfinite measured samples')
    return beacon, z

def main():
    with urlopen(URL,timeout=60) as f:
        raw=f.read(1_000_001)
    digest=hashlib.sha256(raw).hexdigest()
    if digest != SHA256:
        raise RuntimeError('Checksum mismatch')
    beacon,z=parse_iq(raw)
    # Phase equivariance of any complex-linear window: no magnitude substitution.
    window=z[:125]
    phase=np.exp(1j*.43)
    phase_error=float(np.max(np.abs(phase*window-(window*phase))))
    report={'source':URL,'sha256':digest,'samples':int(len(z)),
            'beacon_unique':int(len(np.unique(beacon))),
            'complex_sample_count':int(len(z)),
            'mean_i':float(z.real.mean()),'mean_q':float(z.imag.mean()),
            'rms_amplitude':float(np.sqrt(np.mean(np.abs(z)**2))),
            'phase_window_test_error':phase_error,
            'raw_iq_acquired':True,
            'fmcw_adc_cube_verified':False,
            'object_detection_labels_verified':False,
            'measured_auc':None,
            'evidence':'real_iq_sequence_descriptive_only',
            'note':'125 consecutive I/Q samples are NOT the validated spin-2 tensor mapping or a Doppler/range/antenna cube.'}
    Path('real_iq_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
