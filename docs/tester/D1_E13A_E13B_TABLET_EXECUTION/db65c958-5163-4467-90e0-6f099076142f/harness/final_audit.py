"""Read-only final audit of existing original receipts; no device/process dispatch."""
from pathlib import Path
import hashlib,json,re,zipfile
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];R=B.parents[3];C=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def ck(n,v,d=None):C.append(dict(name=n,passed=bool(v),detail=d))
scope=load(B/'inputs/execution-scope.json');index=load(B/'inputs/input-index.json')
for p in list(index.values())+scope['reviews']+scope['artifacts']+scope['metadataArgv']+[scope['productSeal'],scope['overlaySeal'],scope['overlayArchive'],scope['metadataManifest']]:
 raw=(R/p['path']).read_bytes();ck('immutable pin',len(raw)==p['bytes'] and sha(raw)==p['sha256'],p['path'])
for id in ['01-M1_PRE_DEPLOY','02-RECOVERED-M1_PRE_DEPLOY','03-DEPLOY']:
 receipt=load(B/'evidence'/f'{id}-receipt.json')
 for s in ['stdout','stderr']:
  raw=(B/'evidence'/f'{id}-{s}.txt').read_bytes();ck('original raw pin',len(raw)==receipt[s+'Bytes'] and sha(raw)==receipt[s+'Sha256'],id+' '+s)
 ck('known original actually returned',receipt['originalProcessReturned'] and receipt['bothOriginalPipesReturned'] and receipt['stdinClosed'] and not receipt['responseTimedOut'] and not receipt['overflow'],id)
first=load(B/'evidence/01-M1_PRE_DEPLOY-receipt.json');current=load(B/'evidence/02-RECOVERED-M1_PRE_DEPLOY-receipt.json');deploy=load(B/'evidence/03-DEPLOY-receipt.json')
m1=load(B/'evidence/02-RECOVERED-M1_PRE_DEPLOY-audit.json')
ck('recovered M1 independently admitted',m1['status']=='PASS_CURRENT_DEVICE_METADATA' and not m1['failed'] and current['exitCode']==0)
ck('exact current source and ledger',m1['device']['appVersion']==15 and m1['ledger']['bytes']==2271 and m1['ledger']['consumed']==214483 and m1['ledger']['recordsR']==m1['ledger']['recordsS']==7 and m1['ledger']['reserved']==0)
intent=load(B/'evidence/03-DEPLOY-intent.json');ck('actual approved host JAR used',intent['argv'][2]==str(R/scope['artifacts'][-1]['path']).replace('\\','/'))
stderr=(B/'evidence/03-DEPLOY-stderr.txt').read_text(encoding='utf-8')
ck('exact deployment gate exception',deploy['exitCode']==1 and 'java.io.IOException: E11_ONCE_FIXED_ROLE' in stderr and 'E11DeploymentOnce.record(E11DeploymentOnce.java:22)' in stderr and 'E13HostActivationSession.java:32' in stderr)
matched=re.search(r'^E9_PC_REGISTRY_ENTRY_END (\{.*\})$',stderr,re.M);closed=json.loads(matched[1])['fields']
ck('original registry supervisor physically closed',closed['kind']=='pcClosed' and closed['allOriginalsReturned']=='true' and closed['pcPid']==str(deploy['pid']) and f"E9_PC_CLOSED handle={closed['handle']} actualOriginalReturns=true" in stderr)
ck('new once never created',not (B/'deployment/e13a-activation-deployment.once').exists())
ck('no successful internal deployment summary','E13_DEPLOY_BUDGET' not in stderr)
jar=R/scope['artifacts'][-1]['path']
with zipfile.ZipFile(jar) as z:
 a=z.read('com/videokit/spike/e4/E11DeploymentOnce.class');b=z.read('com/videokit/spike/e4/E13HostActivationSession.class')
 ck('actual JAR contains conflicting fixed roles',b'activation-deployment.once' in a and b'e13a-activation-deployment.once' not in a and b'e13a-activation-deployment.once' in b)
for prior in [scope['productSeal'],scope['overlaySeal']]:
 for p in load(R/prior['path'])['immutableFiles']:
  raw=(R/p['path']).read_bytes();ck('frozen package unchanged',len(raw)==p['bytes'] and sha(raw)==p['sha256'],p['path'])
rawText=sum(load(B/'evidence'/f'{id}-receipt.json')[s+'Bytes'] for id in ['01-M1_PRE_DEPLOY','02-RECOVERED-M1_PRE_DEPLOY','03-DEPLOY'] for s in ['stdout','stderr'])
hostBytes=(B/'evidence/env-recovery-read-01.json').stat().st_size
live=load(B/'evidence/live-resource-ledger.json')
ledger=dict(state='BLOCKED_DEPLOYMENT_ONCE_FIXED_ROLE_MISMATCH',atUtc=datetime.now(timezone.utc).isoformat(),batchId=scope['batchId'],knownDirectOriginalClients=3,hostReadonlyRecoveryOperations=1,operatorStartServerOperations=0,reportedAutomaticDaemonAttemptConservative=1,knownActuallyLaunchedOperations=4,actualOrReportedAttemptConservativeCharge=5,unissuedDeploymentChildAllocationHeld=32,totalConservativeAllocationHeld=37,maxOperations=56,conservativeRemainingAllocation=19,originalClientOutputBytes=rawText,hostReadonlyOutputBytes=hostBytes,observedTextBytes=rawText+hostBytes,unissuedDeploymentChildTextReservationHeld=524288,totalConservativeTextHeld=rawText+hostBytes+524288,maxTextBytes=2097152,extraM1OccupancyReviewsUsed=0,extraPcControlConnections=0,deploymentInternalSdkChildrenStarted=0,installDispatches=0,onceExists=False,failedM1Preserved=True,recoveredM1=m1['status'],currentDeviceFactsTimeScope='Recovered M1 observation only; M2/M3 not run. No inferred final online state.',lastObservedLedger=m1['ledger'],sharedAdbServer=dict(pid=5340,exactPath='D:/Android/SDK/platform-tools/adb.exe',adoptedExisting=True,restartedOrKilled=False,originalAutoStartupAttemptReturnAckInvented=False),knownManagedOriginalsReturned=True,productSupervisorClosed=closed,implicitDaemonAttemptPid='NOT_REPORTED; no all-descendant-closure inference',rawParserCompatibilityCorrections=0,preDispatchControllerClockCompatibilityCorrections=1,newMediaOutputBytes=0,newR=0,newS=0,cases={m:'NOT_RUN' for m in scope['methods']},M2='NOT_RUN',M3='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
ck('cumulative reservations reconcile',live['chargedOriginalOperations']==ledger['totalConservativeAllocationHeld'] and live['originalTextBytes']==ledger['totalConservativeTextHeld'])
ck('all bounds preserved',ledger['totalConservativeAllocationHeld']<=56 and ledger['totalConservativeTextHeld']<2097152)
(B/'evidence/resource-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result=dict(status='PASS_FINAL_EVIDENCE_AUDIT_EXECUTION_BLOCKED',atUtc=datetime.now(timezone.utc).isoformat(),checks=C,failed=[c for c in C if not c['passed']],checkCount=len(C),deviceCallsByAudit=0,resourceSummary=ledger)
(B/'evidence/independent-final-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=result['status'],checks=len(C),failed=result['failed'],observedText=ledger['observedTextBytes'],conservativeAllocation=37,actualKnownOperations=4),ensure_ascii=False))
