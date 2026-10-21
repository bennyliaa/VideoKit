from pathlib import Path
import hashlib,json,zipfile,shutil,re,datetime
R=Path('D:/CodexProjects/VideoKit').resolve();B=(R/'docs/coder/d1render01').resolve();E=B/'evidence'
freeze=E/'render01-freeze.json';assert not freeze.exists(),'candidate already frozen'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
refs=['docs/milestones/D1_RENDER_AUDIO_SOURCE_CODER_REQUIREMENTS_V1.0.md','docs/milestones/D1_RENDER_AUDIO_SOURCE_TESTER_REQUIREMENTS_V1.0.md','docs/coder/D1_EXIT_READINESS_DELIVERY_V1.0.md','docs/FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md']
pins=[]
for name in refs:
    p=R/name;d=B/'reference'/p.name;d.parent.mkdir(exist_ok=True);shutil.copyfile(p,d)
    pins.append({'source':name,'path':d.relative_to(B).as_posix(),'sha256':sha(p)})
dump(E/'requirement-pins.json',pins)

java=sorted(p for folder in ['src','android','upstream','app/src'] for p in (B/folder).rglob('*.java'))
source_index=[];md='# RENDER01 源码定位\n\n原始源码/Android入口为冻结版本；类存在不代表设备运行。\n\n| 源码 | SHA256 |\n|---|---|\n'
for p in java:
    text=p.read_text(encoding='utf-8-sig');line=next((i for i,s in enumerate(text.splitlines(),1) if re.search(r'\b(class|interface)\s+',s)),1)
    x={'path':p.relative_to(R).as_posix(),'sha256':sha(p),'line':line};source_index.append(x)
    md+=f'| [{p.name}](D:/CodexProjects/VideoKit/{x["path"]}:{line}) | `{x["sha256"]}` |\n'
(B/'SOURCE_INDEX_V1.0.md').write_text(md,encoding='utf-8');dump(E/'production-source-index.json',source_index)

inputs=json.loads((E/'build-inputs-final.json').read_text(encoding='utf-8'))
assert all(sha(B/x['path'])==x['sha256'] for x in inputs)
local=json.loads((E/'local-006/source-pins.json').read_text(encoding='utf-8'))
assert all(sha(B/x['path'])==x['sha256'] for x in local)
audit=json.loads((E/'apk-audit-002/artifact-audit.json').read_text(encoding='utf-8'))
assert all(sha(R/x['path'])==x['sha256'] for x in audit['artifacts'])
matrix=json.loads((B/'completion-matrix.json').read_text(encoding='utf-8'));assert all(x['status'] in {'PASS','FAIL','NOT_RUN','BLOCKED'} for x in matrix['rows'])
assert matrix['D1']=='NOT_PASSED' and matrix['M0']=='NOT_STARTED'

# Source/archive membership is explicit. Build cache and tool runtimes are outside the review ZIP.
exclude={'offline-maven','.gradle','.kotlin','build','verifier-classes','__pycache__'}
files=[p for p in B.rglob('*') if p.is_file() and not any(x in exclude for x in p.relative_to(B).parts)
       and p.name not in {'render01-freeze.json','notification-receipt.json','post-freeze-verification.json'}]
reports=[R/'docs/coder'/n for n in ['D1_RENDER_AUDIO_SOURCE_DELIVERY_V1.0.md','D1_RENDER_AUDIO_SOURCE_TECHNICAL_DECISIONS_V1.0.md','D1_RENDER_AUDIO_SOURCE_DEVICE_PLAN_V1.0.md']]
files+=reports;files=sorted(set(files))
assert not any(p.suffix.lower() in {'.jks','.p12','.keystore'} for p in files)
link_checks=[]
for p in reports+[B/'SOURCE_INDEX_V1.0.md']:
    for relative,line in re.findall(r'\]\(D:/CodexProjects/VideoKit/([^):]+)(?::(\d+))?\)',p.read_text(encoding='utf-8')):
        target=R/relative;ok=target.is_file() and (not line or int(line)<=len(target.read_text(encoding='utf-8-sig').splitlines()))
        link_checks.append({'source':p.relative_to(R).as_posix(),'target':relative,'line':line,'pass':ok})
assert all(x['pass'] for x in link_checks)
dump(E/'delivery-verification.json',{'result':'PASS_DOCUMENT_SOURCE_ARTIFACT_BINDING_ONLY','buildInputFilesUnchanged':len(inputs),'localTestSourceFilesMatchFinal':len(local),'productionJavaFiles':len(java),'completionRows':len(matrix['rows']),'linkChecks':link_checks,'deviceOrSDKFieldCommands':0,'mediaPayloadReads':0,'AndroidRuntime':'NOT_RUN','fullD1':'NOT_PASSED'})
files.append(E/'delivery-verification.json');files=sorted(set(files))
archive=R/'docs/coder/D1-20261020-RENDER01-source.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist())==len(set(z.namelist()))==len(files)
    assert z.testzip() is None
    for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files+[archive]]
out={'schemaVersion':1,'candidateId':'D1-20261020-RENDER01','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gitCommit':None,'status':'FROZEN_FOR_RESPONSIBLE_REVIEW_NOT_DEVICE_DISPATCH','D1':'NOT_PASSED','M0':'NOT_STARTED','files':rows,'archiveMembers':len(files),'archive':rows[-1],
     'buildInputManifestSha256':sha(E/'build-inputs-final.json'),'finalBuildAttempt':'010','finalLocalCheck':'006','signatures':'official cached apksig verification passed; Debug only','runtimeExecution':'NOT_RUN','nativeRebuilds':0,'mavenVersionChanges':0,'nativeBaseline':'7 C14 binaries; 6 identical E13F, CPU JNI intentionally C14 matching readonly source ABI','metadataGap':'RENDER01-META-PROV-01 OPEN; binary verification strict, verify-metadata=false','excludedCache':'offline-maven/Gradle/JDK/SDK/build outputs excluded; final artifacts and source/recorded inputs retained','noExecutionAuthorityCreated':True}
dump(freeze,out)
print(json.dumps({'candidate':out['candidateId'],'frozenFiles':len(rows),'zipMembers':len(files),'zip':out['archive'],'freeze_sha256':sha(freeze),'reports':[x for x in rows if x['path'].endswith('DELIVERY_V1.0.md')]},ensure_ascii=False,indent=2))
