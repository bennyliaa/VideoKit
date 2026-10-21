"""Restore only SHA256-pinned POM/Gradle module descriptions; never fetch binaries/SDKs.
Existing verification metadata is the authority, not any returned remote text.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import hashlib,json,urllib.request,urllib.error,concurrent.futures,threading,sys
R=Path('D:/CodexProjects/VideoKit').resolve();B=R/'docs/coder/d1render01'
C=Path('C:/Users/benny/.gradle/caches/modules-2/files-2.1').resolve()
N={'v':'https://schema.gradle.org/dependency-verification'}
root=ET.parse(R/'gradle/verification-metadata.xml').getroot();jobs=[]
for component in root.findall('v:components/v:component',N):
    g,n,v=(component.get(k) for k in ['group','name','version']);folder=C/g/n/v
    # Parent/BOM/multiplatform redirect modules legitimately have no binary of their own.
    for a in component.findall('v:artifact',N):
        name=a.get('name')
        if not name.endswith(('.pom','.module')) or list(folder.glob('*/'+name)):continue
        expected=[h.get('value') for h in a.findall('v:sha256',N)]
        prior=[]
        for record in (B/'evidence').glob('pinned-metadata-restoration*.json'):
            prior.extend(json.loads(record.read_text(encoding='utf-8'))['results'])
        if any(x['status']=='NOT_RESTORED' and x['coordinate']==g+':'+n+':'+v and x['artifact']==name for x in prior):continue
        if expected:jobs.append((g,n,v,name,expected))
assert len(jobs)<=128
lock=threading.Lock();total=0
def fetch(job):
    global total
    g,n,v,name,expected=job;part=g.replace('.','/')+'/'+n+'/'+v+'/'+name
    bases=['https://dl.google.com/dl/android/maven2/','https://repo.maven.apache.org/maven2/'] if g.startswith('androidx.') else ['https://repo.maven.apache.org/maven2/','https://dl.google.com/dl/android/maven2/']
    failures=[]
    for base in bases:
        url=base+part
        try:
            with urllib.request.urlopen(url,timeout=15) as response:raw=response.read(262145)
            if len(raw)>262144:raise ValueError('METADATA_PER_FILE_CAP')
            with lock:
                total+=len(raw)
                if total>4194304:raise ValueError('METADATA_TOTAL_CAP')
            digest=hashlib.sha256(raw).hexdigest()
            if digest not in expected:raise ValueError('PIN_MISMATCH_NO_INSTALL')
            dest=(C/g/n/v/hashlib.sha1(raw).hexdigest()/name).resolve()
            assert dest.is_relative_to(C)
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb') as stream:stream.write(raw)
            return {'coordinate':g+':'+n+':'+v,'artifact':name,'url':url,'bytes':len(raw),'sha256':digest,'cache_path':str(dest),'status':'RESTORED_MATCHED_EXISTING_PIN'}
        except Exception as error:failures.append({'url':url,'error':type(error).__name__+':'+str(error)[:100]})
    return {'coordinate':g+':'+n+':'+v,'artifact':name,'status':'NOT_RESTORED','errors':failures}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,jobs))
out={'scope':'existing root-pinned metadata only, including parent/BOM modules; no binary/version/SDK/media/device changes','trusted_pin_file_sha256':hashlib.sha256((R/'gradle/verification-metadata.xml').read_bytes()).hexdigest(),'metadata_bytes':total,'results':results}
p=B/('evidence/pinned-metadata-restoration'+('-'+sys.argv[1] if len(sys.argv)>1 else '')+'.json');assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'metadata_jobs':len(jobs),'restored':sum(x['status']=='RESTORED_MATCHED_EXISTING_PIN' for x in results),'not_restored':[x['coordinate'] for x in results if x['status']!='RESTORED_MATCHED_EXISTING_PIN'],'bytes':total},ensure_ascii=False))
