"""Acquire a bounded real I/Q radar CSV from ACICULA/mocap2radar.

This is a phase-provenance acquisition experiment, not an object-detection
benchmark. Never fabricate binary labels or claim ADC FMCW cube geometry.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote

ROOT = 'https://huggingface.co'
DS = 'ACICULA/mocap2radar'
BASE = f'{ROOT}/api/datasets/{DS}/tree/main/raw/v3/radar'
MAX_BYTES = 5_000_000

def get(url, limit):
    req = Request(url, headers={'User-Agent': 'E47-Radar-research/1.0'})
    with urlopen(req, timeout=60) as f:
        out = f.read(limit + 1)
    if len(out) > limit:
        raise ValueError('Hard byte limit exceeded')
    return out

def main():
    report = {'source':DS,'evidence':'acquisition_attempt','measured_auc':None,
              'gate1_complex_iq':False,'gate1_labels':False}
    try:
        listing = json.loads(get(BASE+'?limit=100', 200_000))
        candidates = [o for o in listing if o.get('type')=='file' and o.get('path','').endswith('.csv') and o.get('size',MAX_BYTES+1)<=MAX_BYTES]
        report['candidate_count'] = len(candidates)
        if not candidates:
            report['status']='no_bounded_csv'
        else:
            obj = sorted(candidates,key=lambda o:o['size'])[0]
            path=obj['path']
            url=f'{ROOT}/datasets/{DS}/resolve/main/{quote(path,safe="/")}'
            raw=get(url,MAX_BYTES)
            report.update(path=path,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
            report['first_rows']=[r[:6] for r in rows[:3]]
            report['columns']=max(map(len,rows)) if rows else 0
            report['rows']=len(rows)
            # CSV documents I/Q, but explicit column names and units need source validation.
            report['status']='real_radar_csv_acquired_schema_inspected'
            report['gate1_complex_iq']=False
            report['note']='Source documents radar I/Q CSV. No verified fast-time/chirp/receiver ADC cube, labels or E47 detection ROC.'
    except Exception as e:
        report['status']='acquisition_error'
        report['error']=str(e)
    Path('acquisition_alternative.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if report['status']=='acquisition_error':
        raise SystemExit(1)

if __name__=='__main__':
    main()
