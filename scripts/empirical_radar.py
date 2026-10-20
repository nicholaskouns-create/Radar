"""Bounded range access to the authors' public Gao ADC archive."""
import io, json, re, html, hashlib, zipfile
from pathlib import Path
import requests
import time
from collections import OrderedDict
from scipy.io import loadmat

SOURCE='https://drive.google.com/uc?export=download&id=1OfqXXgoFg6xRYZkRqPJye4cQ29Fomh3l'
class RangeFile(io.RawIOBase):
    def __init__(self,url,session):
        self.url=url;self.session=session;self.pos=0;self.transferred=0;self.cache=OrderedDict()
        r=session.get(url,headers={'Range':'bytes=0-0'},stream=True,timeout=60)
        if r.status_code!=206: r.close();raise RuntimeError('Server does not honor byte ranges: '+str(r.status_code))
        self.size=int(r.headers['Content-Range'].split('/')[-1]);r.close()
        print('ARCHIVE_BYTES',self.size,flush=True)
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        return self.pos
    def read(self,n=-1):
        n=self.size-self.pos if n<0 else min(n,self.size-self.pos)
        if n<=0:return b''
        if n>64_000_000 or self.transferred+n>1_500_000_000:raise RuntimeError('Acquisition budget exceeded')
        start=self.pos;end=start+n
        blocks=[]
        first=start//1048576;last=(end-1)//1048576
        for block in range(first,last+1):
            if block not in self.cache:
                lo=block*1048576;hi=min(self.size,lo+1048576)-1
                for attempt in range(3):
                    try:
                        with self.session.get(self.url,headers={'Range':f'bytes={lo}-{hi}'},stream=True,timeout=90) as r:
                            if r.status_code!=206:
                                raise RuntimeError('Range HTTP '+str(r.status_code))
                            if r.headers.get('Content-Range','').split('/')[0]!=f'bytes {lo}-{hi}':
                                raise RuntimeError('Incorrect content range')
                            data=b''.join(r.iter_content(262144))
                        if len(data)!=hi-lo+1:raise RuntimeError('Truncated range')
                        break
                    except (requests.RequestException,RuntimeError) as exc:
                        print('RANGE_RETRY',attempt+1,str(exc),flush=True)
                        if attempt==2:raise
                        time.sleep(2**(attempt+1))
                self.transferred+=len(data)
                if self.transferred>1_500_000_000:raise RuntimeError('Acquisition budget exceeded')
                self.cache[block]=data
            self.cache.move_to_end(block)
            blocks.append(self.cache[block])
        data=b''.join(blocks)[start-first*1048576:end-first*1048576]
        while len(self.cache)>8:self.cache.popitem(last=False)
        self.pos=end
        return data

import os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.e47_radar.spectral import operators

OUT=Path("empirical_results")
C0=299792458.0
RANGES=np.arange(128)*4e6/128*C0/(2*21e12)
CHIRPS=[0,63,127,191,254]
NOISE=[0.0,0.1,1.0]

def label_cells(rows):
    positive=np.zeros(128,bool);ambiguous=np.zeros(128,bool)
    for row in rows:
        px,py,w,h=map(float,row[2:6])
        if not np.isfinite([px,py,w,h]).all() or w<0 or h<0:
            raise ValueError("Invalid coordinate annotation")
        positive |= np.abs(RANGES-np.hypot(px,py))<=.45
        lo_x,hi_x=px-w/2,px+w/2;lo_y,hi_y=py-h/2,py+h/2
        near_x=0 if lo_x<=0<=hi_x else min(abs(lo_x),abs(hi_x))
        near_y=0 if lo_y<=0<=hi_y else min(abs(lo_y),abs(hi_y))
        far=np.hypot(max(abs(lo_x),abs(hi_x)),max(abs(lo_y),abs(hi_y)))
        near=np.hypot(near_x,near_y)
        ambiguous |= (RANGES>=near-.45)&(RANGES<=far+.45)
    keep=(positive|~ambiguous)&(np.arange(128)>=11)&(np.arange(128)<117)&(RANGES<=25)
    return positive.astype(int),keep

def features(raw,P,B):
    window=raw*np.hanning(125)[None,:]
    steering=np.exp(-2j*np.pi*np.arange(128)[:,None]*np.arange(125)[None,:]/128)
    x=(window[:,None,:]*steering[None,:,:]).reshape(-1,125)
    norm=np.sum(abs(x)**2,axis=1)
    if np.any(norm<=0):raise ValueError("Zero-energy ADC")
    eta=(np.sum(abs(x@P.T)**2,axis=1)/norm).reshape(5,128).mean(axis=0)
    residual=(np.sum(abs(x@B.T)**2,axis=1)/norm).reshape(5,128).mean(axis=0)
    power=(abs(np.fft.fft(window,n=128,axis=1))**2).mean(axis=0)
    ratio=np.full(128,np.nan)
    for k in range(11,117):
        reference=np.r_[power[k-11:k-3],power[k+4:k+12]]
        ratio[k]=power[k]/max(reference.mean(),np.finfo(float).tiny)
    return np.column_stack([np.log1p(power),np.log1p(ratio),eta,residual])

def measure(y,s,threshold):
    return {"auc":float(roc_auc_score(y,s)),"average_precision":float(average_precision_score(y,s)),
            "threshold_from_validation":float(threshold),
            "test_range_cell_tpr":float(np.mean(s[y==1]>=threshold)),
            "test_annotation_negative_fpr":float(np.mean(s[y==0]>=threshold))}

def evaluate(a):
    f=a["features"];y=a["y"];g=a["groups"];split=a["split"];noise=a["noise"]
    all_results=[]
    predictions=[]
    for level in NOISE:
        cond=noise==level
        tr=cond&(split=="train");va=cond&(split=="validation");te=cond&(split=="test")
        for mask in [tr,va,te]:
            if len(np.unique(y[mask]))!=2:raise ValueError("Both classes required in every date split")
        models={}
        for name,col in [("matched_filter",0),("ca_cfar",1),("e47_occupancy",2),("e47_residual2",3)]:
            direction=1
            if col>=2 and f[tr& (y==1),col].mean()<f[tr&(y==0),col].mean():direction=-1
            models[name]=(direction*f[va,col],direction*f[te,col])
        for name,cols in [("conventional_logistic",[0,1]),("e47_joint",[2,3]),("conventional_plus_e47",[0,1,2,3])]:
            m=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=3000,random_state=47))
            m.fit(f[tr][:,cols],y[tr])
            models[name]=(m.predict_proba(f[va][:,cols])[:,1],m.predict_proba(f[te][:,cols])[:,1])
        results={}
        for name,(sv,st) in models.items():
            threshold=np.quantile(sv[y[va]==0],.95,method="higher")
            results[name]=measure(y[te],st,threshold)
        groups=np.unique(g[te]);rng=np.random.default_rng(47);deltas=[]
        for _ in range(1000):
            chosen=rng.choice(groups,len(groups),replace=True)
            idx=np.concatenate([np.flatnonzero(g[te]==group) for group in chosen])
            if len(np.unique(y[te][idx]))<2:continue
            deltas.append(roc_auc_score(y[te][idx],models["conventional_plus_e47"][1][idx])-roc_auc_score(y[te][idx],models["conventional_logistic"][1][idx]))
        pergroup={}
        for group in groups:
            ix=g[te]==group
            pergroup[group]={name:float(roc_auc_score(y[te][ix],v[1][ix])) for name,v in models.items()} if len(np.unique(y[te][ix]))==2 else {"auc":None,"reason":"one class"}
        result={"added_noise_power_fraction":level,"train_cells":int(tr.sum()),"validation_cells":int(va.sum()),"test_cells":int(te.sum()),
                "test_positive_cells":int(y[te].sum()),"test_recordings":len(groups),"scores":results,
                "incremental_auc":results["conventional_plus_e47"]["auc"]-results["conventional_logistic"]["auc"],
                "paired_recording_bootstrap_ci95":np.quantile(deltas,[.025,.975]).tolist(),"bootstrap_draws":len(deltas),"per_test_recording_auc":pergroup}
        all_results.append(result)
        for i,original in enumerate(np.flatnonzero(te)):
            predictions.append({"noise":level,"recording":str(g[original]),"frame":str(a["frame"][original]),"range_m":float(a["range_m"][original]),"label":int(y[original]),**{name:float(v[1][i]) for name,v in models.items()}})
    return all_results,predictions

def main():
    OUT.mkdir(exist_ok=True)
    session=requests.Session()
    r=session.get(SOURCE,timeout=30);r.raise_for_status()
    form=re.search(r'<form[^>]+action="([^"]+)"',r.text)
    if not form:raise RuntimeError("Expected authors' public download form")
    params=dict(re.findall(r'name="([^"]+)"[^>]*value="([^"]*)"',r.text))
    url=requests.Request("GET",html.unescape(form.group(1)),params=params).prepare().url
    f=RangeFile(url,session)
    _,_,P,G,_=operators();B=(np.eye(125)-P)@np.linalg.matrix_power(G,2)
    assert np.linalg.matrix_rank(P,tol=1e-7)==47
    records=[];provenance=[];selected=[]
    rng=np.random.default_rng(47)
    with zipfile.ZipFile(f) as z:
        names=z.namelist()
        frames=[n for n in names if "/radar_raw_frame/" in n and n.endswith(".mat")]
        seqs=sorted(set(n.split("/radar_raw_frame/")[0] for n in frames))
        for seq in seqs:
            frame_map={int(Path(n).stem):n for n in frames if n.startswith(seq+"/")}
            label_map={int(Path(n).stem):n for n in names if n.startswith(seq+"/text_labels/") and n.endswith(".csv")}
            common=sorted(set(frame_map)&set(label_map))
            if len(common)<3:raise RuntimeError("Insufficient matched frame IDs: "+seq)
            indices=sorted(set(common[int(q*(len(common)-1))] for q in [.25,.5,.75]))
            date=Path(seq).name[:10]
            split="train" if date in ["2019_04_09","2019_04_30"] else "validation" if date=="2019_05_09" else "test" if date=="2019_05_29" else None
            if split is None:raise RuntimeError("Unplanned date: "+date)
            selected.append({"recording":seq,"split":split,"frames":indices})
            for frame_id in indices:
                fp=frame_map[frame_id];lp=label_map[frame_id]
                raw=z.read(fp);lr=z.read(lp)
                cube=loadmat(io.BytesIO(raw)).get("adcData")
                if cube is None or cube.shape!=(128,255,4,2) or not np.iscomplexobj(cube) or not np.isfinite(cube).all():raise RuntimeError("ADC schema mismatch")
                truth=np.loadtxt(io.BytesIO(lr),delimiter=",",ndmin=2) if lr.strip() else np.empty((0,6))
                if truth.size and truth.shape[1]<6:raise RuntimeError("Label schema mismatch")
                truth=truth[:,:6]
                yy,keep=label_cells(truth)
                adc=cube[:125,CHIRPS,0,0].T.copy()
                power=float(np.mean(abs(adc)**2))
                rotation=np.exp(1j*rng.uniform(-np.pi,np.pi))
                for level in NOISE:
                    n=(rng.normal(size=adc.shape)+1j*rng.normal(size=adc.shape))*np.sqrt(level*power/2)
                    x=(adc+n)*rotation
                    feat=features(x,P,B)
                    if not provenance and level==0:
                        feat0=features(adc,P,B)
                        error=float(np.nanmax(abs(feat-feat0)))
                        assert error<1e-9,("phase equivariance",error)
                        print("PHASE_EQUIVARIANCE_MAX_ERROR",error,flush=True)
                    for k in np.flatnonzero(keep):
                        records.append((feat[k],int(yy[k]),seq,split,level,frame_id,float(RANGES[k])))
                provenance.append({"recording":seq,"frame":frame_id,"raw_path":fp,"label_path":lp,
                                   "raw_sha256":hashlib.sha256(raw).hexdigest(),"label_sha256":hashlib.sha256(lr).hexdigest(),
                                   "raw_bytes":len(raw),"targets":int(len(truth))})
                print("ACQUIRED",len(provenance),seq,frame_id,"targets",len(truth),flush=True)
                (OUT/"provenance.json").write_text(json.dumps(provenance,indent=2))
    a={"features":np.stack([v[0] for v in records]),"y":np.array([v[1] for v in records]),"groups":np.array([v[2] for v in records]),"split":np.array([v[3] for v in records]),
       "noise":np.array([v[4] for v in records]),"frame":np.array([v[5] for v in records]),"range_m":np.array([v[6] for v in records])}
    np.savez_compressed(OUT/"derived_features.npz",**a)
    results,predictions=evaluate(a)
    report={"status":"executed_on_measured_complex_adc","evidence":"source_annotated_range_cell_pilot",
            "code_commit":os.environ.get("GITHUB_SHA"),"workflow_run":os.environ.get("GITHUB_RUN_ID"),
            "source":SOURCE,"source_citation":"Gao et al., DOI 10.21227/xm40-jx59; RAMP-CNN DOI 10.1109/JSEN.2020.3036047",
            "recordings":len(selected),"frames":len(provenance),"transferred_bytes":f.transferred,
            "sample_rate_hz":4e6,"slope_hz_s":21e12,"range_grid_m":float(RANGES[1]),"protocol":"research/gao_empirical_protocol.md",
            "split_manifest":selected,"results":results,
            "limitations":["source coordinate annotations, no independent calibration certificate","annotation-negative cells may contain unlabeled reflectors",
                           "range-cell classification, not object-level detection","no radial velocity truth","added-noise ratios are not measured target SNR","five held-out test recordings"]}
    (OUT/"result.json").write_text(json.dumps(report,indent=2))
    (OUT/"test_predictions.json").write_text(json.dumps(predictions))
    print("RESULT_JSON",json.dumps(report),flush=True)
    with open(os.environ.get("GITHUB_STEP_SUMMARY",str(OUT/"summary.md")),"a") as out:
        out.write("# Measured Gao range-cell pilot\n\n"+str(len(provenance))+" frames from "+str(len(selected))+" recordings; held-out dates.\n\n")
        out.write("| Added noise power fraction | Conventional AUC | E47 joint AUC | Conventional + E47 AUC | Incremental 95% CI |\n|---|---|---|---|---|\n")
        for r in results:
            out.write(f'| {r["added_noise_power_fraction"]} | {r["scores"]["conventional_logistic"]["auc"]:.6f} | {r["scores"]["e47_joint"]["auc"]:.6f} | {r["scores"]["conventional_plus_e47"]["auc"]:.6f} | {r["paired_recording_bootstrap_ci95"]} |\n')
        out.write("\nScope: source-annotated range-cell comparison. See result.json for all limitations and scores.\n")
if __name__=="__main__":main()
