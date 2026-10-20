"""Bounded range access to the authors' public Gao ADC archive."""
import io, json, re, html, hashlib, zipfile
from pathlib import Path
import requests
from scipy.io import loadmat

SOURCE='https://drive.google.com/uc?export=download&id=1OfqXXgoFg6xRYZkRqPJye4cQ29Fomh3l'
class RangeFile(io.RawIOBase):
    def __init__(self,url,session):
        self.url=url;self.session=session;self.pos=0;self.transferred=0
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
        end=self.pos+n-1
        with self.session.get(self.url,headers={'Range':f'bytes={self.pos}-{end}'},stream=True,timeout=60) as r:
            if r.status_code!=206:raise RuntimeError('Range request not honored')
            r.raise_for_status()
            data=b''.join(r.iter_content(262144))
        if len(data)!=n:raise RuntimeError('Truncated range')
        self.pos+=n;self.transferred+=n
        return data

def main():
    session=requests.Session()
    r=session.get(SOURCE,timeout=30);r.raise_for_status()
    form=re.search(r'<form[^>]+action="([^"]+)"',r.text)
    if not form:raise RuntimeError('Expected public download confirmation form')
    params=dict(re.findall(r'name="([^"]+)"[^>]*value="([^"]*)"',r.text))
    url=requests.Request('GET',html.unescape(form.group(1)),params=params).prepare().url
    f=RangeFile(url,session)
    with zipfile.ZipFile(f) as z:
        names=z.namelist()
        print('ARCHIVE_ENTRIES',len(names))
        print('EXAMPLE_PATHS',json.dumps(names[:15]))
        frames=[n for n in names if '/radar_raw_frame/' in n and n.endswith('.mat')]
        seqs=sorted(set(n.split('/radar_raw_frame/')[0] for n in frames))
        print('SEQUENCES',json.dumps(seqs))
        for seq in seqs[:4]:
            frame=sorted(n for n in frames if n.startswith(seq+'/'))[0]
            raw=z.read(frame);data=loadmat(io.BytesIO(raw))
            print('FRAME',frame,'SHA256',hashlib.sha256(raw).hexdigest(),'ARRAYS',[(k,list(v.shape),str(v.dtype)) for k,v in data.items() if not k.startswith('__')])
            labels=[n for n in names if n.startswith(seq+'/text_labels/') and n.endswith('.csv')]
            print('LABEL_NAMES',json.dumps(labels[:4]))
            if labels:print('LABEL',labels[0],z.read(labels[0]).decode()[:1000])
        print('TRANSFERRED_BYTES',f.transferred)
if __name__=='__main__':main()
