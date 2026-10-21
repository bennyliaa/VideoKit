"""Freeze C08 source/config/report snapshot and recursive evidence manifest. Never modifies C01/C02/C03/C04/C05/C06."""
from pathlib import Path
import hashlib,json,sys,zipfile,datetime
root=Path(sys.argv[1]).resolve();candidate='D1-20261005-C08';base=root/'docs/coder/d1c08';evidence=base/'evidence';artifacts=base/'artifacts'/candidate
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def record(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
paths=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    relative=p.relative_to(root);parts=relative.parts
    if any(x in ('.gradle','.idea','.kotlin','.git','build','classes','__pycache__','test_media','artifacts','outputs','evidence','.codex','.agents','gpg-home') for x in parts):continue
    if relative.name=='freeze-identities.txt':continue
    if relative.name=='local.properties':continue
    name=relative.as_posix()
    allowed=(parts[:3]==('docs','coder','d1c08') or name.startswith('app/src/') or name.startswith('gradle/') or name in {
        'AGENTS.md','build.gradle.kts','settings.gradle.kts','gradle.properties','gradlew','gradlew.bat',
        'app/build.gradle.kts','app/gradle.lockfile','gradle.lockfile',
        'docs/milestones/D1_C08_CODER_REQUIREMENTS_V1.0.md',
        'docs/coder/D1_DELIVERY_D1-20261005-C08.md','docs/coder/D1_C08_DEVICE_APPENDIX_V1.0.md',
        'docs/coder/D1_C08_LICENSE_BUILD_REVIEW_V1.0.md'})
    if not allowed:continue
    paths.append(p)
paths.sort()
manifest={'candidateId':candidate,'git_commit':None,'source_files':[record(p) for p in paths],'excluded':'media, C01-C07 immutable deliveries, tester/coordinator mutable documents, machine-local config, gpg-home, generated outputs and post-freeze identity receipt; generated FFmpeg config/build facts separately retained in evidence; baseline integrity separately verified'}
(evidence/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=artifacts/(candidate+'-source.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,p.relative_to(root).as_posix())
summary={'candidateId':candidate,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'state':'BLOCKED_STRICT_WHITELIST / NOT_READY_FOR_DEVICE_EXECUTION','git_commit':None,'apk_built':False,'ffmpeg_app_integration':'STOPPED_NOT_ADMITTED','device_execution':'NOT_RUN','source_manifest_sha256':sha(evidence/'source-manifest.json'),'artifacts':[record(p) for p in sorted(artifacts.iterdir()) if p.is_file()],'evidence':[record(p) for p in sorted(evidence.rglob('*')) if p.is_file() and p.name!='freeze-summary.json'],'required_remaining':['After explicit user resumption: close H263 decoder/parser whitelist composition and compiled-object license/security audit before any App integration','Implement opaque AVIO, bounded seek broker, actual PTS frame and task/epoch/UID/PID/byte/queue gates in single-APK ordinary isolated CPU service','Prepare normal/corrupt/SIGSEGV/hang/actual death/SourceReleased/second-task/host-survival tests; device execution remains NOT_RUN and is not scheduled','C07 historical FAIL and ordinary UNKNOWN FAIL unchanged; do not automatically rerun or replace evidence','P0 full pipeline, formal export/quality gates, model rights and product admission remain unresolved'],'user_pause':'After this blocked delivery closes, stop development/testing/new assignments and wait for explicit user resumption.'}
(evidence/'freeze-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('source_files',len(paths),'evidence_files',len(summary['evidence']))
for row in summary['artifacts']:print(row['path'],row['sha256'])
