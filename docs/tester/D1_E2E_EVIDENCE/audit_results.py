"""Independent reconciliation of completed immutable outputs; no candidate imports."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e2e'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=read(BASE/'evidence/e2e-freeze.json'); manifest=read(BASE/'manifest/branches.json')
for r in f['immutableFiles']:
    b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
assert sha((BASE/'evidence/e2e-freeze.json').read_bytes())=='aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
rm=read(BASE/'execution/result-manifest.json');launcher=read(BASE/'execution/launcher-result.json');driver=read(BASE/'execution/driver-result.json')
assert rm['complete'] and rm['resultHashComplete'] and rm['noInFlight'] and launcher['noInFlight'] and driver['noInFlight']
assert launcher['status']==driver['status']==rm['status']=='FAIL' and driver['firstFailure']=='INCOMPLETE_FULL_ROW_COUNT'
assert launcher['reservationConsumed'] and launcher['wrapperFacts']['spawnCalls']==1
assert launcher['originalChildExitObserved'] and launcher['originalChildExitCode']==2
assert launcher['wrapperFacts']['parentProcessHandleCloseProven'] and launcher['wrapperFacts']['parentSpawnCreditsRemaining']==0
root=BASE/'selfcheck'/driver['driverWitness']['root']; pre=read(root/'result-before-close.json'); witness=driver['driverWitness']
assert pre['status']=='PASS' and pre['error'] is None
assert sha((root/'result-before-close.json').read_bytes())==witness['precloseSummarySha']
rows=pre['rows'];expected=['PF']+[r['id'] for r in manifest['branches'] if r['id'] not in ('P10-D','P10-C')]+[r['id'] for r in manifest['branches'] if r['id'] in ('P10-D','P10-C')]
assert [r['branch'] for r in rows]==expected and len(rows)==62 and len(set(expected))==62
by={r['id']:r for r in manifest['branches']};by['PF']=manifest['preflight'] if 'preflight' in manifest else {}
branch_details=[]
for row in rows:
    if row['branch']=='PF':continue
    spec=by[row['branch']]
    assert (row['controls'],row['queryNew'],row['queryReplay'],row['seconds'])==(spec['nonquery'],spec['queriesNew'],spec['queriesReplay'],spec['seconds'])
    assert 0<=row['elapsedSeconds']<=spec['seconds']
    branch_details.append(dict(row,independentStatus='COMPLETED_ORIGINAL_CHECKPOINT',batchStatus='FAIL_PRESERVED'))
assert len(branch_details)==61
usage=witness['usage'];assert usage==dict(credit=655360,ib=1573492,ic=59,n=351,qn=83,qr=18,records=32,targets=10,v=128)
assert len(pre['cellHistory'])==64 and len({r['operation'] for r in pre['cellHistory']})==64
assert witness['privateCells']==dict(active=0,archived=64,peak=1,retained=0,total=64)
hub=witness['callbackHub'];assert hub['lifecycle']=='CLOSED' and hub['remainingCredits']==[] and not hub['ownershipPending']
assert all(hub[k]==0 for k in ('active','cells','queued','monitorInFlight','workersAlive'))
for w in hub['workers'].values():
    assert all(w[k] is True for k in ('entered','exited','joined','joinReturned','creditReleased')) and w['releaseProof']=='THREAD_JOIN_PROVEN'
close=witness['logClose'];assert close['closed'] and close['id']=='GC/n32' and close['remainingResources']==0
assert all(p['exited'] and p['code']==0 for p in close['exitedHelpers'].values())
assert witness['metadataCommitStatus']=='HEALTHY' and witness['metadataUnknownRequestedBytes']==0
assert witness['metadataRequested']==witness['metadataWritten']==6431845
allfiles={p.relative_to(BASE).as_posix():p for base in (BASE/'execution',BASE/'selfcheck') for p in base.rglob('*') if p.is_file()}
assert len(allfiles)==146 and {r['path'] for r in rm['files']}==set(allfiles)-{'execution/result-manifest.json'}
for r in rm['files']:
    p=allfiles[r['path']];assert not p.is_symlink() and not p.is_junction()
    b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
fixture=lambda p:p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out'
actual=dict(fixtureBytes=sum(p.stat().st_size for p in allfiles.values() if fixture(p)),metadataBytes=sum(p.stat().st_size for p in allfiles.values() if not fixture(p)))
assert actual==rm['outputUsage']==dict(fixtureBytes=135244,metadataBytes=704997)
assert rm['combinedUsage']==dict(fixtureBytes=135244,metadataBytes=812811)
assert (root/'L.bin').read_bytes()==bytes(i%251 for i in range(131072))
assert (root/'C.bin').read_bytes()==bytes(i%251 for i in range(4096)) and (root/'Z.bin').read_bytes()==b''
outputs=[]
for i in range(1,11):
    p=root/f'T{i:02}.out';expected_bytes=bytes(range(32)) if i in (1,5) else b'Z\0xy\0\0\0abc' if i==2 else b'\0' if i in (3,4) else b''
    b=p.read_bytes();assert b==expected_bytes
    outputs.append(dict(name=p.name,bytes=len(b),sha256=sha(b),matchesIndependentExpectedBytes=True))
log=(root/'global.log').read_bytes();metriclines=[];events=[]
for line in log.splitlines(keepends=True):
    if line.startswith(b'['):metriclines.append(line)
    elif line.startswith(b'{'):
        item=json.loads(line)
        if 'runtimeMetricFormat' in item:metriclines.append(line)
        else:events.append(item)
metricbytes=sum(map(len,metriclines));assert metricbytes==538 and len(metriclines)==6
assert len(log)==93440 and len(log)-metricbytes==92902
assert witness['runtimeObservation']['observation']['samples']==5
assert not witness['runtimeObservation']['mockMetricsUsed'] and not witness['runtimeObservation']['nativeQueryPending']
obs=witness['runtimeObservation']['observation'];policy=read(BASE/'profiles/runtime-policy.json')
for role,peak in obs['peaks'].items():
    baseline=obs['baselines'][role];limit=policy['limits'][role]
    for k in ('threads','handles','workingSetBytes','privateBytes'):
        assert peak[k]<=limit[k] and peak[k]-baseline[k]<=limit['delta'+k[0].upper()+k[1:]]
reader=witness['runtimeObservation']['reader'];assert reader['openedHandles']==reader['closedHandles']==18 and reader['maximumOwnedHandlesObserved']==1 and not reader['closeUnknown'] and not reader['observerCreditHeld']
for rel,p in allfiles.items():
    dest=OUT/'execution-archive'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
facts=dict(at=datetime.now().astimezone().isoformat(),batchStatus='FAIL',finding='E2E-F01: wrapper compares PF+61 checkpoint count 62 against 61',rawBatchFailurePreserved=True,actualAttempts=1,fullBatchPasses=0,completedScenarioCount=61,preflightCheckpoints=1,reportedCheckpoints=62,assertions=160,precloseStatus='PASS_BEFORE_WRAPPER_FINAL_CHECK',manifestIntegrity='PASS',immutableUnchanged=True,outputFiles=146,resultManifestSha256=sha((BASE/'execution/result-manifest.json').read_bytes()),precloseSha256=witness['precloseSummarySha'],independentOutputs=outputs,usage=usage,outputUsage=actual,combinedUsage=rm['combinedUsage'],runtimeObservation=witness['runtimeObservation'],ledgerPeaks=witness['ledgerPeaks'],metadataPeak=witness['metadataPeak'],metadataCumulativeWritten=witness['metadataWritten'],finalGlobalLogBytes=len(log),finalEventBytes=len(log)-metricbytes,finalMetricBytes=metricbytes,GCn32ReturnProven=True,helpers=close['exitedHelpers'],originalG=launcher['originalChild'],originalGExitCode=2,originalLauncher=driver['claim']['launcher'],noInFlight=True,unexecutedScenarioIds=[],realMedia='NOT_RUN',devices='NOT_RUN',nextAttemptAuthorized=False)
save('independent-results-audit.json',facts);save('completed-and-not-run.json',dict(preflight=rows[0],completedScenarios=branch_details,cleanup='GC/n01..n32 actual returned',unexecutedSelfOwnedScenarios=[],notRun=['REAL_IO/test_media','devices/C14','five product namespace durability variants','second actual attempt'],fullBatchStatus='FAIL',fullBatchPasses=0))
print(json.dumps({k:facts[k] for k in ('batchStatus','finding','completedScenarioCount','assertions','outputFiles','resultManifestSha256','precloseSha256','outputUsage','combinedUsage','finalGlobalLogBytes','noInFlight')},ensure_ascii=False))
