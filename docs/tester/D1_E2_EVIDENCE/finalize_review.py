"""Finalize static E2 configuration review without candidate execution/import."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E2_ADMISSION_REVIEW_REPORT_V1.0.md'
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',report.read_text(encoding='utf-8')):
 target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
 if lm:target=target[:lm.start()]
 p=Path(target);assert p.exists(),target
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines())
archive=read(OUT/'archive-and-manifest-audit.json')
assert sha(BASE/'evidence/freeze-summary.json')==archive['freezeSha256']
for r in archive['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
upstream=read(BASE/'upstream-e1e/freeze-summary.json');source=read(BASE/'upstream-e1e/source-manifest.json');baselines=read(BASE/'upstream-e1e/preserved-baselines.json')
for r in upstream['files']+upstream['selfcheckFiles']+source['files']+baselines['files']:assert sha(ROOT/r['path'])==r['sha256']
w=read(BASE/'evidence/selfcheck-1792165512531930500.json')['witness']
assert w['callbackHub']['lifecycle']=='CLOSED' and not w['callbackHub']['ownershipPending'] and not w['callbackHub']['remainingCredits']
save('callback-hub-archived-state.json',dict(scope='Existing normal synthetic witness, not rerun',callbackHub=w['callbackHub'],privateCells=w['privateCells'],managedResourcePeaks=w['ledgerPeaks'],outerCloseProof=w['logClose']))
save('runtime-decision-review.json',dict(scope='Static proposal conflict, not measured process thread peak',GThreadDelta=dict(proposed=8,baselineChoices=['G before PF/n01','G after HELLO'],plannedAdditions=dict(nativePool=2,pipeReadersAndDrainers=4,completion=2,temporaryP10=2),sumPlanned=10,conclusion='PF-before baseline +8 may reject permitted planned concurrency; baseline choice unspecified',recommendation='Coordinator may approve +12 while retaining absolute16 and original pre-PF baseline, or explicitly bounded phase-specific anchors; tester changed no thresholds'),minimumAvailableMemory=dict(proposed=2147483648,oldSnapshot=964145152,oldSnapshotIsFresh=False,newProbePerformed=False),observerLog=dict(events=104320,metrics=26752,total=131072,allocationApproved=False,integrationComplete=False),nativeBridge=dict(preferredRoute='Pinned Windows x64/JBR21 FFM plus narrowly approved existing FileDescriptor handle access in original J helper',implemented=False,approved=False,extraMediaFD=0,extraN=0,extraRPC=0),realExecutionAllowed=False))
save('external-primary-reference-notes.json',dict(scope='Documentation supporting route recommendation only; no target execution',sources=[dict(url='https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/io/FileDescriptor.java',supports='OpenJDK21 internal FileDescriptor handle field; not proof of deployed JBR ABI'),dict(url='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/foreign/package-summary.html',supports='JDK21 preview foreign function and memory API'),dict(url='https://docs.oracle.com/en/java/javase/21/core/restricted-methods.html',supports='Restricted native access and explicit runtime option'),dict(url='https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle',supports='Query identity of already open Windows handle')],engineeringInference='Prefer a reviewed J-only FFM bridge using the existing FD; implementation, flags and actual JBR compatibility remain unapproved'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E2 independent configuration admission review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),conclusion='CONFIGURATION_ACCEPTABLE_FOR_NEXT_ADAPTER_BATCH; REAL_EXECUTION_NOT_ADMITTED',findings=[dict(id='E2-C01',classification='PRE_EXECUTION_CONFIGURATION_DECISION',topic='G +8 delta versus up to10 planned additional threads with pre-PF anchor; phase anchor ambiguous',observedRuntimeViolation=False)],knownUnimplementedAdapters=['A02 exact read-only input and separate CREATE_NEW output namespace','A05 J opened-FD identity bridge','Observer runner wiring and log-credit enforcement'],priorFixesPreserved=True,candidateIntegrity='PASS',candidateUnchanged=True,producerSelectedChecks=dict(integration=159,targeted=716,syntheticTotal=875,separateConfigurationProcessMetadataChecks=6,scope='Existing evidence only'),ownFunctionalTests=0,targetedRerun=False,PFStarted=False,mediaIO=False,mediaStat=False,build=False,adb=False,newHelperProcesses=0,newWorkerThreads=0,inFlight=[],thresholdsChanged=False,realExperimentAuthorized=False,D1Passed=False,M0Started=False,C14Resumed=False,notification='Pending direct authorized coordinator notification'))
print(json.dumps(dict(reportSha256=sha(report),configurationDecisions=1,candidateUnchanged=True,inFlight=[])))
