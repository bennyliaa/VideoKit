"""Independent audit of the existing failed M1 raw only; never starts a process/device."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[1];R=BASE.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
checks=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)))
index=load(BASE/'inputs/input-index.json')
for pin in index.values():
 p=R/pin['path'];raw=p.read_bytes();ck('immutable input '+pin['path'],len(raw)==pin['bytes'] and sha(raw)==pin['sha256'])
scope=load(BASE/'inputs/execution-scope.json')
for pin in scope['metadataArgv']+scope['reviews']+[scope['productSeal'],scope['overlaySeal'],scope['overlayArchive'],scope['metadataManifest']]+scope['artifacts']:
 raw=(R/pin['path']).read_bytes();ck('reviewed artifact '+pin['path'],len(raw)==pin['bytes'] and sha(raw)==pin['sha256'])
receipt=load(BASE/'evidence/01-M1_PRE_DEPLOY-receipt.json');intent=load(BASE/'evidence/01-M1_PRE_DEPLOY-intent.json')
out=(BASE/'evidence/01-M1_PRE_DEPLOY-stdout.txt').read_bytes();err=(BASE/'evidence/01-M1_PRE_DEPLOY-stderr.txt').read_bytes()
argv=load(R/scope['metadataArgv'][0]['path'])['argv']
ck('exact reviewed direct M1 argv',intent['argv']==argv)
ck('original stdout',len(out)==receipt['stdoutBytes']==0 and sha(out)==receipt['stdoutSha256'])
ck('original stderr',len(err)==receipt['stderrBytes']==144 and sha(err)==receipt['stderrSha256'])
ck('actual failed client natural return',receipt['exitCode']==1 and receipt['signal'] is None and receipt['originalProcessReturned'] and receipt['bothOriginalPipesReturned'] and receipt['stdinClosed'])
ck('not a timeout or truncation',not receipt['responseTimedOut'] and not receipt['overflow'])
ck('actual ADB startup error',b'failed to start daemon' in err and b'cannot connect to daemon' in err)
ck('no metadata frame obtained',b'E13A_METADATA' not in out and b'BEGIN\t' not in out)
ck('once absent',not (BASE/'deployment/e13a-activation-deployment.once').exists())
controller=load(BASE/'evidence/controller-ledger.json')
ck('one original metadata client only',len(controller['entries'])==1 and controller['chargedOriginalProcessAllocation']==1 and controller['cumulativeOriginalTextBytes']==144 and controller['stopped'])
ledger=dict(state='BLOCKED_HOST_ADB_STARTUP',atUtc=datetime.now(timezone.utc).isoformat(),batchId=scope['batchId'],actualDirectMetadataClients=1,actualDeploymentJavaEntries=0,actualCaseJavaEntries=0,actualInstrumentChildren=0,actualInstallDispatches=0,originalCommandTextBytes=144,pcControlConnections=0,successfulPathAllocation=48,pcOperationLimit=50,extraM1OccupancyReviewsUsed=0,extraM1OccupancyReviewsRemaining=2,autoDaemonStartupReported=True,autoDaemonProcessIdentity='NOT_REPORTED_BY_ORIGINAL_ADB_STDERR',autoDaemonIndependentReturnProof=False,conservativeAutomaticStartupAllocation=1,totalConservativeProcessCharge=2,conservativeRemainingOperationAllocation=48,noAutomaticRetryAuthorizedForStartupFailure=True,onceExists=False,knownOriginalClientReturned=True,knownOriginalPipesReturned=True,allDescendantProcessesReturnClaimed=False,currentDeviceAvailability='NOT_OBSERVED',currentSourcePair='NOT_OBSERVED',currentLedger='NOT_READ',ledgerBaselineReferenceOnly=scope['legacy'],newMediaOutputBytes=0,newR=0,newS=0,rawParserCorrectionsUsed=0,preDispatchControllerClockAdaptations=1,cases={m:'NOT_RUN' for m in scope['methods']})
(BASE/'evidence/resource-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result=dict(status='PASS_EXISTING_RAW_AUDIT_EXECUTION_BLOCKED',atUtc=datetime.now(timezone.utc).isoformat(),checks=checks,failed=[c for c in checks if not c['passed']],deviceCallsByAudit=0,processesStartedByAudit=0,currentDeviceFactsInferredFromHistoricalEvidence=False)
(BASE/'evidence/independent-blocked-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=result['status'],checkCount=len(checks),failed=result['failed'],originalClientTextBytes=144,conservativeProcesses=2),ensure_ascii=False))
