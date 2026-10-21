"""Standard local Maven layout, copied only from artifacts matching existing verification pins.
No generated POM, version substitution, external download, or added dependency.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import hashlib,json,shutil,sys
R=Path('D:/CodexProjects/VideoKit').resolve();B=R/'docs/coder/d1render01'
C=Path('C:/Users/benny/.gradle/caches/modules-2/files-2.1');D=B/'offline-maven'
N={'v':'https://schema.gradle.org/dependency-verification'};rows=[];missing=[]
root=ET.parse(B/'gradle/verification-metadata.xml').getroot()
for c in root.findall('v:components/v:component',N):
    g,n,v=(c.get(k) for k in ['group','name','version'])
    for a in c.findall('v:artifact',N):
        name=a.get('name')
        if not name.endswith(('.pom','.module','.jar','.aar')) or name.endswith(('-sources.jar','-javadoc.jar')):continue
        pins={s.get('value') for s in a.findall('v:sha256',N)}
        options=list((C/g/n/v).glob('*/'+name))
        if not options:missing.append(g+':'+n+':'+v+'/'+name);continue
        found=False
        for source in options:
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            if digest not in pins:continue
            dest=D/Path(*g.split('.'))/n/v/name;dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
            else:shutil.copyfile(source,dest)
            rows.append({'coordinate':g+':'+n+':'+v,'artifact':name,'cache_source':str(source),'path':dest.relative_to(B).as_posix(),'sha256':digest,'bytes':source.stat().st_size});found=True;break
        assert found,'no trusted cached artifact: '+g+':'+n+':'+v+'/'+name
p=B/('evidence/offline-repository'+('-'+sys.argv[1] if len(sys.argv)>1 else '')+'.json');assert not p.exists();p.write_text(json.dumps({'pin_source':'candidate verification metadata (original root pins + reviewed frozen E13F SBOM hashes)','pin_sha256':hashlib.sha256((B/'gradle/verification-metadata.xml').read_bytes()).hexdigest(),'files':rows,'unavailable_unused_or_unresolved':missing},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'verified_reused_files':len(rows),'bytes':sum(x['bytes'] for x in rows),'not_cached':len(missing)}))
