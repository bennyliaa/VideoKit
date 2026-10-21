from pathlib import Path
import datetime,hashlib,json,os,sys,zipfile
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c09';e=base/'evidence';art=base/'artifacts/D1-20261016-C09'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
review=json.loads((e/'candidate-self-review.json').read_text(encoding='utf-8'));assert review['review']=='PASS_LOCAL_BUILD_STATIC_AND_PURE_CHECKS'
paths=[];excluded={'outputs','classes','evidence','artifacts','gpg-home','build','__pycache__','.gradle','.kotlin','.git'}
for directory,folders,names in os.walk(base):
 folders[:]=[n for n in folders if n not in excluded]
 for name in names:
  if name!='freeze-identities.txt':paths.append(Path(directory)/name)
for folder in ['app/src','gradle']:
 paths += [p for p in (root/folder).rglob('*') if p.is_file()]
for name in ['build.gradle.kts','settings.gradle.kts','gradle.properties','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile','docs/SYSTEM_ARCHITECTURE_V1.0.md','docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md','docs/OPEN_SOURCE_FRAMEWORKS_AND_DEVELOPMENT_EFFORT_ESTIMATE_V1.0.md','docs/milestones/D1_C09_CODER_REQUIREMENTS_V1.0.md','docs/coder/D1_DELIVERY_D1-20261016-C09.md','docs/coder/D1_C09_DEVICE_APPENDIX_V1.0.md','docs/coder/D1_C09_LICENSE_BUILD_ADMISSION_V1.0.md']:
 p=root/name
 if p.exists():paths.append(p)
paths=sorted(set(paths));manifest={'candidateId':'D1-20261016-C09','git_commit':None,'source_files':[row(p) for p in paths],'excluded':'C01-C08 immutable deliveries, original media, transient outputs/classes/build/Gradle caches, GPG runtime home, post-freeze identity receipt; full generated configuration and audit evidence separately hashed'}
(e/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=art/'D1-20261016-C09-source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(p,p.relative_to(root).as_posix())
summary={'candidateId':'D1-20261016-C09','git_commit':None,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'state':'READY_FOR_COORDINATED_DEVICE_TEST / D1_NOT_PASSED','source_manifest_sha256':sha(e/'source-manifest.json'),'artifacts':[row(p) for p in sorted(art.iterdir()) if p.is_file()],'evidence':[row(p) for p in sorted(e.rglob('*')) if p.is_file() and p.name!='freeze-summary.json'],'pure_assertions':215,'cpu_device_methods':17,'android_execution':'NOT_RUN','scope':'single APK ordinary-isolated ARM64 API31+ Debug CPU experiment; only legacy regression uses companion','required_remaining':['Coordinator hands this entire frozen candidate to tester once, phone then tablet serially; verify fresh identities and data before use','Actual isolated loading/frames/PTS/quotas/cancellation/death/source FD release/fault/raw signal/second task/host survival and affected legacy gates','Keep historical ordinary UNKNOWN/C07 FAIL unchanged; no opportunistic reruns or cleanup-derived signal proof','Full Kit/AAR/Flutter product/multi-host/model rights/all P0/distribution remain incomplete; do not enter M0']}
(e/'freeze-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print('FROZEN',len(paths),'sources',len(summary['evidence']),'evidence',len(summary['artifacts']),'artifacts')
