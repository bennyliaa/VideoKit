"""Freeze D1 source/configuration and evidence references; excludes media and output copies."""
from pathlib import Path
import hashlib,json,zipfile,sys,datetime
root=Path(sys.argv[1]).resolve();candidate='D1-20261005-C01';base=root/'docs/coder/d1';evidence=base/'evidence'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
sources=[]
for path in root.rglob('*'):
    if not path.is_file():continue
    relative=path.relative_to(root);parts=relative.parts
    if any(p in ('.gradle','.idea','build','test_media','.git','classes','artifacts','outputs','evidence') for p in parts):continue
    if relative.as_posix()=='local.properties':continue
    sources.append(path)
sources.sort()
rows=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources]
manifest={'candidateId':candidate,'git_commit':None,'source_files':rows,'excluded':'test_media, outputs, generated classes/build, APK artifacts, evidence, machine-local local.properties'}
(evidence/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=base/'artifacts'/candidate/(candidate+'-source.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for path in sources:z.write(path,path.relative_to(root).as_posix())
files=[]
for path in sorted(evidence.iterdir()):
    if path.is_file() and path.name!='freeze-summary.json':files.append({'path':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
artifacts=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(archive.parent.iterdir()) if p.is_file()]
summary={'candidateId':candidate,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'state':'BLOCKED / NOT_READY_FOR_FORMAL_ACCEPTANCE','source_manifest_sha256':sha(evidence/'source-manifest.json'),'artifacts':artifacts,'evidence':files,'required_remaining':['Android devices and real media/encoding trials','tracking model provenance rights and labeled quality tests','native crash/OOM isolation worker prototype and device injection','Sink async ready reconciliation and real output validation','full notices/vulnerability review/special fixture coverage']}
(evidence/'freeze-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('source files',len(rows),'evidence files',len(files),'source snapshot',sha(archive))
for p in artifacts:print(p['path'],p['sha256'])
