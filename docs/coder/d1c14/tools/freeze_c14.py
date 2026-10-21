from pathlib import Path
import datetime,hashlib,json,os,sys,zipfile
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c14';e=base/'evidence';art=base/'artifacts/D1-20261016-C14'
assert not (e/'freeze-summary.json').exists(),'C14 is already frozen; do not rewrite it'
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
for name in ['build.gradle.kts','settings.gradle.kts','gradle.properties','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile','docs/coder/initialize_c14.py','docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md','docs/PUBLIC_API_CONTRACT_V1.0.md','docs/EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md','docs/TRACKING_TECHNICAL_SPIKE_V1.0.md','docs/MILESTONES_V1.0.md','docs/SYSTEM_ARCHITECTURE_V1.0.md','docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md','docs/OPEN_SOURCE_FRAMEWORKS_AND_DEVELOPMENT_EFFORT_ESTIMATE_V1.0.md','docs/milestones/D1_C14_CODER_REQUIREMENTS_V1.0.md','docs/coder/D1_DELIVERY_D1-20261016-C14.md','docs/coder/D1_C14_DEVICE_APPENDIX_V1.0.md','docs/coder/D1_C14_LICENSE_BUILD_ADMISSION_V1.0.md','docs/coder/D1_C14_ENCODER_NEGOTIATION_DESIGN_V1.0.md','docs/coder/D1_C14_DEFECT_MATRIX_V1.0.md','docs/coder/D1_C14_PIPELINE_BOUNDARY_DESIGN_V1.0.md','docs/coder/D1_C14_REMAINING_GATE_REVIEW_V1.0.md','docs/coder/D1_C13_TRACKING_EVIDENCE_V1.0.md','docs/PROJECT_DECISIONS_AND_EXECUTION_V1.0.md','docs/coder/D1_C14_FRAMEWORK_MAPPING_V1.0.md','docs/coder/D1_C11_EXIT_EVIDENCE_DESIGN_V1.0.md']:
 p=root/name
 assert p.is_file(),p;paths.append(p)
paths += [p for p in e.rglob('*') if p.is_file() and p.name not in {'source-manifest.json','freeze-summary.json'}]
paths=sorted(set(paths));manifest={'candidateId':'D1-20261016-C14','git_commit':None,'source_files':[row(p) for p in paths],'excluded':'C01-C13 immutable deliveries, original media, transient outputs/classes/build/Gradle caches, GPG runtime home, post-freeze identity receipt; full signed FFmpeg source retained as archive, inherited generated configuration/evidence included in ZIP and independently hashed'}
(e/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=art/'D1-20261016-C14-source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(p,p.relative_to(root).as_posix())
summary={'candidateId':'D1-20261016-C14','git_commit':None,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'state':'READY_FOR_COORDINATED_DEVICE_TEST / D1_NOT_PASSED','source_manifest_sha256':sha(e/'source-manifest.json'),'artifacts':[row(p) for p in sorted(art.iterdir()) if p.is_file()],'evidence':[row(p) for p in sorted(e.rglob('*')) if p.is_file() and p.name!='freeze-summary.json'],'pure_assertions':review['pure_assertions'],'script_assertions':review['script_assertions'],'total_local_assertions':review['total_local_assertions'],'cpu_device_methods':review['cpu_device_methods'],'host_device_methods':review['host_device_methods'],'legacy_device_methods':review['legacy_device_methods'],'pipeline_device_methods':review['pipeline_device_methods'],'encoder_device_methods':review['encoder_device_methods'],'scheduled_device_methods':review['scheduled_device_methods'],'compiled_designated_methods':review['compiled_designated_methods'],'unchanged_signal_methods':review['unchanged_signal_methods'],'android_execution':'NOT_RUN','scope':'finite public AVC capability/configure negotiation with typed diagnostics; unchanged six-frame pipeline/PTS/content/EOF and CPU acquisition algorithms; unchanged FFmpeg 8.0.3/quota/Media3; only legacy regression uses companion','required_remaining':['Coordinator hands entire C14 once to tester; actual enabled/component/service hard preflight, preserve phone system-disabled block if unresolved; do not ask user to find a missing enable button; no bypass, uninstall or data clear','All 73 scheduled CPU/lifecycle, host, legacy, pipeline and encoder methods; two unchanged CPU SIGSEGV methods NOT_RUN_UNCHANGED_PLATFORM_LIMIT per eligible device; distinguish real test failure, environment block and execution unknown; preserve all attempts','Strict sync STOP/caller/task/epoch, ACK loss, actual death/source/pending-call/slot recovery and second-task/UI nonblocking behavior are device NOT_RUN','Keep historical signal0/ordinary UNKNOWN/trace absence unchanged; C13 self OS0 FAIL and independent system11 remain separate; unchanged acquisition path is not rerun for new identity; no cleanup-derived target signal proof','Full Kit/AAR/Flutter product/multi-host/model rights/all P0/distribution remain incomplete; do not enter M0']}
(e/'freeze-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print('FROZEN',len(paths),'sources',len(summary['evidence']),'evidence',len(summary['artifacts']),'artifacts')
