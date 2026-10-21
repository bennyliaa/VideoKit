import hashlib,json,sys,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();cache=Path(sys.argv[2]);result=[]
ns={'m':'http://maven.apache.org/POM/4.0.0'}
for line in (root/'app/gradle.lockfile').read_text().splitlines():
    if line.startswith('#') or ':' not in line:continue
    coordinate,configs=line.split('=',1);group,name,version=coordinate.split(':');files=[];licenses=[]
    for path in sorted((cache/group/name/version).rglob('*')):
        if not path.is_file():continue
        files.append({'name':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
        if path.suffix=='.pom':
            tree=ET.parse(path)
            for entry in tree.findall('m:licenses/m:license',ns):
                licenses.append({key:entry.findtext('m:'+key,namespaces=ns) for key in ('name','url')})
    result.append({'coordinate':coordinate,'resolved_configurations':configs.split(','),'pom_license_claims':licenses,'license_review':'POM metadata only; inherited/custom notices require review','cached_artifacts':files})
(root/'docs/coder/d1/evidence/dependency-inventory.json').write_text(json.dumps({'scope':'App resolved lock graph; build plugins covered by verification metadata separately','vulnerability_scan':'NOT_RUN','dependencies':result},indent=2),encoding='utf-8')
apks=[]
media_names={p.name for p in (root/'test_media').rglob('*') if p.is_file()}
for path in sorted((root/'app/build/outputs/apk').rglob('*.apk')):
    with zipfile.ZipFile(path) as z:
        entries=z.namelist();matches=[n for n in entries if Path(n).name in media_names]
        # DEX strings are a static check for release exclusion, not runtime instrumentation.
        spike=[n for n in entries if n.endswith('.dex') and b'Lcom/videokit/spike/' in z.read(n)]
        apks.append({'path':str(path.relative_to(root)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'test_media_named_entries':matches,'dex_with_spike_descriptor':spike,'native_libraries':[n for n in entries if n.endswith('.so')],'internet_permission_check':'see aapt-badging.txt'})
(root/'docs/coder/d1/evidence/apk-audit.json').write_text(json.dumps(apks,indent=2),encoding='utf-8')
print('locked components',len(result),'missing cached entries',[r['coordinate'] for r in result if not r['cached_artifacts']]);print(json.dumps(apks,indent=2))
