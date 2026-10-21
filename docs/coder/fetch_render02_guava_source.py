from pathlib import Path
import urllib.request,urllib.error,hashlib,json,datetime
R=Path('D:/CodexProjects/VideoKit').resolve();B=R/'docs/coder/d1render02';D=B/'evidence/guava-official-source';D.mkdir(exist_ok=False)
base='https://repo.maven.apache.org/maven2/com/google/guava/guava-parent/33.3.1-android/'
name='guava-parent-33.3.1-android.pom';records=[]
for suffix in ['', '.sha1','.md5','.asc']:
    url=base+name+suffix;start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(url,timeout=20) as response:
            raw=response.read(131073);headers=dict(response.headers);status=response.status;final=response.url
        assert len(raw)<=131072
        p=D/(name+suffix);p.write_bytes(raw)
        records.append({'requestedUrl':url,'finalUrl':final,'retrievedUtc':start,'httpStatus':status,'headers':headers,'path':p.relative_to(B).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    except urllib.error.HTTPError as error:records.append({'requestedUrl':url,'retrievedUtc':start,'httpStatus':error.code,'status':'NOT_RETRIEVED'})
raw=(D/name).read_bytes();assert len(raw)==20632
assert hashlib.sha256(raw).hexdigest()=='6e11986ea7250b51f847157e2dc937f32a306804dfce0007a5e81ddb9b95c579'
checks={}
for alg,suffix in [('sha1','.sha1'),('md5','.md5')]:
    p=D/(name+suffix)
    if p.exists():checks[alg]=hashlib.new(alg,raw).hexdigest()==p.read_text().strip().split()[0];assert checks[alg]
dest=B/'offline-maven/com/google/guava/guava-parent/33.3.1-android'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
(D/'source-receipt.json').write_text(json.dumps({'purpose':'NEW fixed-version provenance, not historical approval','coordinate':'com.google.guava:guava-parent:33.3.1-android','officialRepository':base,'records':records,'sameOriginChecksums':checks,'pgpSignature':'retained if available; NOT identity/trust verified','independentAdmission':'PENDING_TESTER_REVIEW','binaryDownloads':0,'dependencyVersionChanges':0},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'sameOriginChecksums':checks,'independentReview':'PENDING'},ensure_ascii=False))
