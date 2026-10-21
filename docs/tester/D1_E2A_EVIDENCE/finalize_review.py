"""Finalize independent E2A static review, no candidate/native/thread execution."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E2A_ADMISSION_REVIEW_REPORT_V1.0.md'
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',report.read_text(encoding='utf-8')):
 target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
 if lm:target=target[:lm.start()]
 p=Path(target);assert p.exists(),target
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines())
a=read(OUT/'archive-and-manifest-audit.json');assert sha(BASE/'evidence/freeze-summary.json')==a['freezeSha256']
for r in a['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
for folder in ['upstream-e2','upstream-e1e']:
 f=read(BASE/folder/'freeze-summary.json');s=read(BASE/folder/'source-manifest.json')
 for r in f['files']+f['selfcheckFiles']+s['files']:assert sha(ROOT/r['path'])==r['sha256']
for r in read(BASE/'upstream-e1e/preserved-baselines.json')['files']:assert sha(ROOT/r['path'])==r['sha256']
freeze=read(BASE/'evidence/freeze-summary.json');w=read(BASE/freeze['integrationEvidence'])['witness'];run=BASE/'selfcheck'/w['root']
final_size=sum(p.stat().st_size for p in run.rglob('*') if p.is_file() and p.name not in ('L.bin','C.bin','Z.bin') and p.suffix!='.out')
assert final_size==w['metadataPeak']==634207
save('final-metadata-size-review.json',dict(scope='Read-only enumeration of existing authored-run metadata only; no source-media access',root=str(run),actualFinalMetadataFileSizeSum=final_size,producerPeak=w['metadataPeak'],agrees=True,doesNotClaim='No independent proof of transient OS peaks or hostile external modification'))
save('runtime-root-cause-next-step.json',dict(scope='Recommendations only; no new sampling or launch',observed=dict(role='R',originalPid=38684,handles=519,limit=512,stage='PF/n05 HELLO baseline',inputBytes=0,inputCalls=0),provenRootCause=None,doesNotProve='Media handle leak or removable handle types; only aggregate counters exist',nextBatch=['Fix E2A-A01 exact input alias use within existing grant control','Authorize finite non-media R-startup stage diagnostics with original pid/creation/owner and explicit observation costs','Inspect existing precompiled DLL Add-Type loading and required runtime resources; direct absolute-path Assembly.LoadFrom is only an unproven candidate','Change only attributable unnecessary startup/loading or owned undisposed resources; do not close runtime-owned arbitrary handles','Preserve first 519 failure and fixed512/+128 policy; no repeated sampling/warmup/reset to select a lower value','After a specific reduction, new frozen actual-OS authored-file regression before separate real admission'],newSamplingPerformed=False,thresholdRaised=False))
save('external-primary-reference-notes.json',dict(scope='Documentation supporting an untested startup-loading hypothesis',sources=[dict(url='https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/add-type?view=powershell-7.6',supports='Add-Type loads an assembly from a specified path; Utility cmdlet'),dict(url='https://learn.microsoft.com/dotnet/api/system.reflection.assembly.loadfrom',supports='Direct loading an assembly from its specified path')],inference='Direct loading might avoid unnecessary cmdlet startup dependencies, not proved to reduce handles or solve519'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E2A independent adapter whole-package review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),conclusion='LIMITED_ADAPTER_MAIN_PATHS_STATICALLY_SUPPORTED; ONE_P2_ALIAS_PATH_GAP; R519_GT512_STILL_BLOCKS_REAL_ADMISSION',findings=[dict(id='E2A-A01',severity='P2',topic='Q09-ALIAS still opens output-root C.bin instead of resolved input alias',observedRuntimeFailure=False)],actualRuntimeAdmission='BLOCKED_R_HANDLES_519_GT_512',priorFixesPreserved=True,candidateIntegrity='PASS',candidateUnchanged=True,producerSelectedChecks=dict(integration=159,targeted=844,driverSyntheticTotal=1003,separateJavaBridgeAssertions=87,javaProcesses=10,scope='Existing evidence only; actual OS gate failure kept separate'),ownFunctionalTests=0,targetedRerun=False,newSampling=False,PFStarted=False,mediaIO=False,mediaStat=False,build=False,adb=False,newHelperProcesses=0,newWorkerThreads=0,inFlight=[],thresholdsChanged=False,realExperimentAuthorized=False,D1Passed=False,M0Started=False,C14Resumed=False,notification='Pending direct authorized coordinator notification'))
print(json.dumps(dict(reportSha256=sha(report),newP2=1,RRuntimeAdmission=False,candidateUnchanged=True,inFlight=[])))
