from pathlib import Path
import datetime,hashlib,json,os,sys,zipfile
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c11';e=base/'evidence';art=base/'artifacts/D1-20261016-C11'
assert not (e/'freeze-summary.json').exists(),'C11 is already frozen; do not rewrite it'
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
for name in ['build.gradle.kts','settings.gradle.kts','gradle.properties','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile','docs/coder/initialize_c11.py','docs/SYSTEM_ARCHITECTURE_V1.0.md','docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md','docs/OPEN_SOURCE_FRAMEWORKS_AND_DEVELOPMENT_EFFORT_ESTIMATE_V1.0.md','docs/milestones/D1_C11_CODER_REQUIREMENTS_V1.0.md','docs/coder/D1_DELIVERY_D1-20261016-C11.md','docs/coder/D1_C11_DEVICE_APPENDIX_V1.0.md','docs/coder/D1_C11_LICENSE_BUILD_ADMISSION_V1.0.md','docs/coder/D1_C11_EXIT_EVIDENCE_DESIGN_V1.0.md','docs/coder/D1_C11_DEFECT_MATRIX_V1.0.md']:
 p=root/name
 if p.exists():paths.append(p)
paths=sorted(set(paths));manifest={'candidateId':'D1-20261016-C11','git_commit':None,'source_files':[row(p) for p in paths],'excluded':'C01-C10 immutable deliveries, original media, transient outputs/classes/build/Gradle caches, GPG runtime home, post-freeze identity receipt; full signed FFmpeg source retained as archive, inherited generated configuration/evidence separately hashed'}
(e/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=art/'D1-20261016-C11-source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(p,p.relative_to(root).as_posix())
summary={'candidateId':'D1-20261016-C11','git_commit':None,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'state':'READY_FOR_COORDINATED_DEVICE_TEST / D1_NOT_PASSED','source_manifest_sha256':sha(e/'source-manifest.json'),'artifacts':[row(p) for p in sorted(art.iterdir()) if p.is_file()],'evidence':[row(p) for p in sorted(e.rglob('*')) if p.is_file() and p.name!='freeze-summary.json'],'pure_assertions':review['pure_assertions'],'script_assertions':review['script_assertions'],'total_local_assertions':review['total_local_assertions'],'cpu_device_methods':review['cpu_device_methods'],'host_device_methods':review['host_device_methods'],'legacy_device_methods':review['legacy_device_methods'],'android_execution':'NOT_RUN','scope':'single APK ordinary-isolated ARM64 API31+ Debug generation/trace repair; unchanged FFmpeg 8.0.3/quota/Media3; only legacy regression uses companion','required_remaining':['Coordinator hands entire C11 once to tester; actual enabled/component/service hard preflight, preserve phone manual-enable block if unresolved; no bypass, uninstall or data clear','All frozen CPU/lifecycle, host and legacy methods per eligible device; distinguish real test failure, environment block and execution unknown; preserve all attempts','Strict sync STOP/caller/task/epoch, ACK loss, actual death/source/pending-call/slot recovery and second-task/UI nonblocking behavior are device NOT_RUN','Keep C01-C10 historical results and C07 ordinary UNKNOWN/signal FAIL unchanged; no cleanup-derived target signal proof','Full Kit/AAR/Flutter product/multi-host/model rights/all P0/distribution remain incomplete; do not enter M0']}
(e/'freeze-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print('FROZEN',len(paths),'sources',len(summary['evidence']),'evidence',len(summary['artifacts']),'artifacts')
