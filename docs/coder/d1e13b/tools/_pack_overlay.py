import sys
if sys.argv[1:]!=['pack']:raise SystemExit('Explicit package_overlay.py pack required; verify is read-only')
from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,shutil,subprocess,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e13a';E=B/'evidence'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':sha(b)}
def js(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def check(r):assert pin(R/r['path'])=={k:r[k] for k in ['path','bytes','sha256']},r['path']
prior=[]
for name,h in [('d1e11/evidence/e11-freeze.json','fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5'),('d1e11/revision-r1/evidence/e11-final-freeze.json','2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3'),('d1e12/e12-freeze.json','6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640'),('d1e13/evidence/e13-freeze.json','3b80d430aa7f859174ffae0a4b5ca948a01aa032d15c0666fb595e6a1bba5cc0'),('d1e13a/evidence/e13a-freeze.json','24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6')]:
    path=R/'docs/coder'/name;assert pin(path)['sha256']==h;rows=json.loads(path.read_text())['immutableFiles']
    for row in rows:check(row)
    prior.append({'seal':pin(path),'immutableRowsVerified':len(rows)})
js(E/'base-freeze-verification.json',{'status':'PASS_READONLY_OLD_BYTES','priorSeals':prior,'builds':0,'deviceCalls':0})
refs=[R/'docs/tester/D1_E13A_ARCHITECTURE_REVIEW_REPORT_V1.0.md',R/'docs/tester/D1_E13A_REVIEW_EVIDENCE/metadata-command-review.json',R/'docs/milestones/D1_E13B_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13B_TESTER_REQUIREMENTS_V1.0.md',OLD/'release/candidate-binding.json',OLD/'release/device-plan.json']
ref=B/'reference';ref.mkdir(exist_ok=True)
for p in refs:shutil.copyfile(p,ref/p.name)
js(E/'authority-input-pins.json',{'references':[pin(p) for p in refs],'scope':'Existing accepted reviews/requirements, not a new execution permit'})
js(E/'primary-source-review.json',{'reviewDate':'2026-10-18','sdkDownloads':0,'sources':[{'url':'https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java','lines':['8320-8333','8635-8659','8874'],'finding':'Supported unfiltered processes route; optional active list; terminal force-background flag.'},{'url':'https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ProcessList.java','lines':['3780-3860'],'finding':'Active list is emitted before OOM stages in full process output.'},{'url':'https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActiveInstrumentation.java','lines':['99-129'],'finding':'Multi-line entries include target details, unindented permissions, arguments; retained finished entries remain busy.'}],'vendorEvidence':json.loads((E/'metadata-shell-check-results.json').read_text())['historicalVendorInputs'],'limitations':'Upstream tag/old vendor raw are references, not fresh device observation. Active fixtures are explicitly constructed.'})
diffs=[]
for p in sorted((B/'release/metadata').glob('*')):
    if not p.is_file():continue
    before=OLD/'release/metadata'/p.name
    if before.is_file():
        target=E/'diffs'/(p.name+'.diff');target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(''.join(difflib.unified_diff(before.read_text().splitlines(True),p.read_text().splitlines(True),fromfile=pin(before)['path'],tofile=pin(p)['path'])),encoding='utf-8')
        diffs.append({'base':pin(before),'overlay':pin(p),'diff':pin(target)})
js(E/'metadata-diff-manifest.json',{'changes':diffs,'productChanges':0})
reuse=json.loads((B/'release/overlay-binding.json').read_text())
for row in reuse['baseArtifacts']:check(row)
js(E/'base-product-reuse.json',{'baseCandidate':'D1-20261018-E13A','baseSeal':pin(OLD/'evidence/e13a-freeze.json'),'baseSourceArchive':pin(R/'docs/coder/D1-20261018-E13A-source.zip'),'artifacts':reuse['baseArtifacts'],'productVersion':17,'acceptedSourceVersion':15,'APK_JAR_nativeBuilds':0,'scopeDraftsChanged':False,'actualScope':None,'actualOnce':None})
metadata=json.loads((B/'release/metadata/three-client-manifest.json').read_text());semantic=json.loads((E/'metadata-shell-check-results.json').read_text());overlay=json.loads((E/'overlay-check-results.json').read_text())
assert len(semantic['cases'])==20 and len(overlay['collectorCases'])==4 and len(overlay['syntax'])==32
js(E/'final-summary.json',{'status':'PASS_METADATA_ONLY_LOCAL_SCOPE','semanticCases':20,'historicalVendorIdleInputs':4,'activeFixtures':'Controlled insertions, not actual active device events','exactCollectorSubstituteCases':4,'syntaxChecks':32,'argvScriptBytePairs':3,'productTests':0,'builds':0,'deviceCalls':0,'queryClientsPrepared':3,'budgetsUnchanged':True})
# No APK/JAR/private signing key, Gradle tree or obsolete local awk prototype is in this overlay.
files=[]
for folder in ['release','reference']:
    files += [p for p in (B/folder).rglob('*') if p.is_file()]
files += [B/'tools'/name for name in ['processes_reader.sh','process_record.py','check_shell_metadata.py','run_shell_reader.sh','prepare_overlay.py','check_overlay.py','package_overlay.py','_pack_overlay.py']]
files += [p for p in E.rglob('*') if p.is_file() and not any(x in {'metadata-cases'} for x in p.relative_to(E).parts) and p.name!='metadata-check-results.json' and p.name!='e13b-freeze.json']
files += list((R/'docs/coder').glob('D1_E13B_*.md'))+[R/'docs/milestones/D1_E13B_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13B_TESTER_REQUIREMENTS_V1.0.md']
names=sorted({pin(p)['path'] for p in files});archive=R/'docs/coder/D1-20261018-E13B-metadata.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for name in names:z.write(R/name,name)
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist())==len(names) and set(z.namelist())==set(names)
    for name in names:assert z.read(name)==(R/name).read_bytes()
seal={'schema':1,'id':'D1-20261018-E13B-METADATA','baseProduct':'D1-20261018-E13A','status':'FROZEN_METADATA_ONLY_DEVICE_NOT_RUN','atUtc':datetime.now(timezone.utc).isoformat(),'archive':pin(archive),'immutableFiles':[pin(R/n) for n in names]+[pin(archive)],'priorSeals':prior,'exclusions':['Local scratch/.checks/__pycache__','Undeployed local awk prototype and its exploratory logs','External seal self','Post-freeze verification/handoff/notification'],'productBuilds':0,'deviceCalls':0,'actualScope':None,'actualOnce':None}
js(E/'e13b-freeze.json',seal);sealpin=pin(E/'e13b-freeze.json')
def snapshot():return [pin(p) for p in sorted(B.rglob('*')) if p.is_file() and not any(v in {'.checks','__pycache__'} for v in p.relative_to(B).parts)]
before=snapshot();checks=[]
for args in [[],['verify','--seal-sha',sealpin['sha256']],['--help'],['pack','--help']]:
    argv=[sys.executable,'-X','utf8','-B',str(B/'tools/package_overlay.py')]+args;result=subprocess.run(argv,capture_output=True,timeout=60);assert result.returncode==0,(args,result.stderr)
    checks.append({'argv':argv,'exitCode':0,'stdout':result.stdout.decode(),'stderr':result.stderr.decode()})
assert before==snapshot(),'READONLY_VERIFY_MUTATED_FILES'
receipt={'status':'PASS_E13B_FINAL_READONLY_VERIFICATION','archive':pin(archive),'externalSeal':sealpin,'archiveEntries':len(names),'immutableRows':len(seal['immutableFiles']),'readOnlyFilesBeforeAfter':len(before),'verifications':checks,'priorSeals':prior,'baseArtifactsReused':reuse['baseArtifacts'],'semanticCases':20,'collectorCases':4,'syntaxChecks':32,'productBuilds':0,'deviceCalls':0,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
js(R/'docs/coder/D1_E13B_FINAL_READONLY_VERIFICATION_V1.0.json',receipt)
print(json.dumps({k:v for k,v in receipt.items() if k!='verifications'},ensure_ascii=False))
