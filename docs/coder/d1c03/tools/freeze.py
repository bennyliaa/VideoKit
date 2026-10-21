"""Freeze C03 source/config/report snapshot and recursive evidence manifest. Never modifies C01."""
from pathlib import Path
import hashlib,json,sys,zipfile,datetime
root=Path(sys.argv[1]).resolve();candidate='D1-20261005-C03';base=root/'docs/coder/d1c03';evidence=base/'evidence';artifacts=base/'artifacts'/candidate
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
    if any(x in ('.gradle','.idea','.kotlin','.git','build','classes','__pycache__','test_media','artifacts','outputs','evidence','.codex','.agents') for x in parts):continue
    if relative.name=='local.properties':continue
    name=relative.as_posix()
    allowed=(parts[:3]==('docs','coder','d1c03') or name.startswith('app/src/') or name.startswith('gradle/') or name in {
        'AGENTS.md','build.gradle.kts','settings.gradle.kts','gradle.properties','gradlew','gradlew.bat',
        'app/build.gradle.kts','app/gradle.lockfile','gradle.lockfile',
        'docs/milestones/D1_C03_CODER_REQUIREMENTS_V1.0.md',
        'docs/coder/D1_DELIVERY_D1-20261005-C03.md','docs/coder/D1_C03_DEVICE_APPENDIX_V1.0.md',
        'docs/coder/D1_C03_TOOL_SECURITY_DECISION_V1.0.md','docs/coder/D1_C03_TRACKING_SAMPLES_AND_LABELS_V1.0.md',
        'docs/coder/D1_C03_M0_FREEZE_SCOPE_V1.0.md'})
    if not allowed:continue
    paths.append(p)
paths.sort()
manifest={'candidateId':candidate,'git_commit':None,'source_files':[record(p) for p in paths],'excluded':'media, C01/C02 snapshots/reports/device request, tester/coordinator mutable documents, machine-local config and generated outputs; baseline integrity separately verified'}
(evidence/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=artifacts/(candidate+'-source.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,p.relative_to(root).as_posix())
summary={'candidateId':candidate,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'state':'BLOCKED / NOT_READY_FOR_FORMAL_ACCEPTANCE','git_commit':None,'source_manifest_sha256':sha(evidence/'source-manifest.json'),'artifacts':[record(p) for p in sorted(artifacts.iterdir()) if p.is_file()],'evidence':[record(p) for p in sorted(evidence.rglob('*')) if p.is_file() and p.name!='freeze-summary.json'],'required_remaining':['Phone/tablet C03 execution after coordinator selects candidate; no C02 overwrite during current testing','Different-UID signed companion actual codec/GPU/FD/parallel-death feasibility plus extra APK product/signing/distribution decision','Full risky-media/face pipeline migration and production adversarial/OOM isolation','Labeled real tracking samples, weights rights or qualified replacement, unchanged final P0 quality gates','Restricted vulnerable tooling requires supported patched graph and compatibility review before restricted services are enabled; final distribution NOTICE','Provider/NAS SourceDisconnected and remaining product platform capabilities']}
(evidence/'freeze-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('source_files',len(paths),'evidence_files',len(summary['evidence']))
for row in summary['artifacts']:print(row['path'],row['sha256'])
