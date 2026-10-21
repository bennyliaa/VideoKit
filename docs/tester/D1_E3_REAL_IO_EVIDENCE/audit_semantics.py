"""Independent semantics over archived output bytes; no candidate imports or media."""
from pathlib import Path
import hashlib,json,base64,math
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e3';ARCHIVE=OUT/'original-output-archive'
RUN='e3-11a896d3c2c34483ba2dff60fa63f5c8';PREFIX='runs/'+RUN+'/'
def sha(b):return hashlib.sha256(b).hexdigest()
def encoded(v,sort=False):return json.dumps(v,sort_keys=sort,separators=(',',':'),ensure_ascii=True).encode('ascii')
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
collection=json.loads((OUT/'collection-integrity.json').read_bytes());usage=dict(collection['resultReadUsageIncludingPriorDriverAndVerify'])
usage['bytes']+=(OUT/'collection-integrity.json').stat().st_size;usage['files']+=1
# The first semantic pass verified all143 archived files and decoded states,
# then stopped at the alias-probe guard's empty version. Charge that read pass
# and resume only required semantic files; no original result is reopened.
usage['bytes']+=719649+(OUT/'decoded-original-states.json').stat().st_size+(OUT/'collection-integrity.json').stat().st_size
usage['files']+=145
def bounded(p):
    size=p.stat().st_size;assert usage['bytes']+size<=usage['byteCap'] and usage['files']<usage['fileCap']
    usage['bytes']+=size;usage['files']+=1
    return p.read_bytes()
selected=[r for r in collection['outputHashes'] if r['path'].startswith('execution/') or r['path'] in (PREFIX+'global.log',PREFIX+'result-before-close.json') or r['path'].endswith('.out')]
cache={r['path']:bounded(ARCHIVE/r['path']) for r in selected}
for r in selected:assert len(cache[r['path']])==r['bytes'] and sha(cache[r['path']])==r['sha256']
states=json.loads(bounded(OUT/'decoded-original-states.json'))
commands={k:dict(v,task=task) for task,state in states.items() for k,v in state['commands'].items()}
def get(n):return json.loads(cache[n])
driver=get('execution/driver-result.json');launcher=get('execution/launcher-result.json');rm=get('execution/result-manifest.json');pre=get(PREFIX+'result-before-close.json');w=driver['driverWitness'];claim=driver['claim']
manifest=json.loads((BASE/'manifest/branches.json').read_bytes());policy=json.loads((BASE/'profiles/runtime-policy.json').read_bytes())
assert rm['batchPassProven'] and rm['status']==driver['status']==launcher['status']==pre['status']==w['status']=='PASS'
assert driver['firstFailure'] is None and pre['error'] is None and launcher['originalChildExitObserved'] and launcher['originalChildExitCode']==0
assert all(v['accepted'] for v in (driver['completion'],driver['resources'])) and driver['real61Run']
assert claim==get('execution/claim.json')==pre['actualRegressionAdmission']==w['actualRegressionAdmission']
reservation=get('execution/reservation.json');launch=get('execution/launch.json')
assert claim['launcher']==reservation['launcher']==launch['launcher'] and claim['child']==launch['child']==launcher['originalChild']
assert claim['reservationSha256']==launch['reservationSha256']==sha(cache['execution/reservation.json'])
assert claim['launchSha256']==sha(cache['execution/launch.json'])
assert reservation['createdBeforeG'] and reservation['consumed'] and not reservation['refundAllowed'] and launcher['reservationConsumed']
assert claim['expectedFreeze']=='7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709'
assert claim['profile']=='REAL_IO' and claim['profileGeometry']==dict(boundary=2147483648,lengths=dict(L=3212959911,C=4096,Z=0))
assert not claim['mockMetricsUsed'] and claim['coordinatorSecretVerified']
assert [r['branch'] for r in pre['rows']]==['PF']+manifest['executionOrder'] and len(pre['rows'])==62
for row in pre['rows']:
    if row['branch']=='PF':continue
    spec=next(r for r in manifest['branches'] if r['id']==row['branch'])
    assert (row['controls'],row['queryNew'],row['queryReplay'],row['seconds'])==(spec['nonquery'],spec['queriesNew'],spec['queriesReplay'],spec['seconds'])
    assert math.isfinite(row['elapsedSeconds']) and 0<=row['elapsedSeconds']<=spec['seconds']
trace=pre['assertionEvidence'];assert len(trace)==pre['assertions']==w['assertions']==w['assertionEvidenceCount']==160
assert sha(encoded(trace,True))==w['assertionEvidenceSha256'] and all(r['seq']==i for i,r in enumerate(trace,1))
events=[];numeric=[];metricbytes=0
for line in cache[PREFIX+'global.log'].splitlines(keepends=True)[1:]:
    val=json.loads(line)
    if isinstance(val,list):numeric.append(val);metricbytes+=len(line)
    elif 'runtimeMetricFormat' in val:metricbytes+=len(line)
    else:events.append(val)
windowfacts=[]
for i,offset in enumerate([2147418112,2147450880,2147483648,3212894375],1):
    j=commands[f'P01-N{i}/d01'];r=commands[f'P01-N{i}/d02']
    assert j['args'][1:3]==r['args'][1:3]==[offset,65536]
    assert j['result']['n']==r['result']['n']==65536 and j['result']['sha']==r['result']['sha']
    for name,cmd in [(f'P01-N{i}/d01',j),(f'P01-N{i}/d02',r)]:
        assert cmd['status']=='DONE' and cmd['error']==''
        terminal=[e for e in events if e.get('id')==name and e.get('phase')=='DONE'];assert len(terminal)==1
        assert sha(encoded(cmd['result']))==terminal[0]['resultDigest']
    chunks=[]
    for k in range(4):
        cmd=commands[f'P01-S{i}/d{k+1:02}'];assert cmd['args'][1:4]==[offset+k,65536-k,1] and cmd['result']['n']==1
        value=base64.b64decode(cmd['result']['bytes']);assert len(value)==1 and sha(value)==cmd['result']['sha'];chunks.append(value)
    reference=commands[f'P01-S{i}/d05'];prefix=b''.join(chunks)
    assert reference['args'][1:3]==[offset,4] and reference['result']['n']==4 and reference['result']['sha']==sha(prefix)
    checkpoint=next(r for r in pre['rows'] if r['branch']==f'P01-S{i}')
    assert checkpoint['windowOutcome']=='UNFILLED' and checkpoint['windowBytesObserved']==4
    windowfacts.append(dict(index=i,offset=offset,requestedEachActor=65536,actualEachActor=65536,Jsha256=j['result']['sha'],Rsha256=r['result']['sha'],independentActorDigestsEqual=True,shortJRequests=[65536-k for k in range(4)],shortActualBytes=4,shortReferenceSha256=sha(prefix),shortOutcome='UNFILLED',noMediaReread=True))
jprefix=commands['Q01-SEQ/d01']['result'];rprefix=commands['Q01-SEQ/d02']['result'];payload=base64.b64decode(jprefix['bytes'])
assert len(payload)==32 and payload==base64.b64decode(rprefix['bytes']) and sha(payload)==jprefix['sha']==rprefix['sha']
outputs=[]
for i in range(1,11):
    name=f'T{i:02}.out';b=cache[PREFIX+name]
    expected=payload if i in (1,5) else b'Z\0xy\0\0\0abc' if i==2 else payload[:1] if i in (3,4) else b''
    assert b==expected
    outputs.append(dict(name=name,bytes=len(b),sha256=sha(b),expectedDerivedFrom='Independent archived J/R equal source prefix' if i in (1,3,4,5) else 'Approved explicit seek/write/abort plan',matches=True))
objects=[]
for task,state in states.items():
    for key,obj in state['objects'].items():
        assert obj['disposition'] in ('CLOSED_PROVEN','RELEASED_BY_OWNER_EXIT')
        if obj['role'] not in ('H','REF','guard'):continue
        version=obj['version'];guard=obj if obj['role']=='guard' else state['objects'][f'{task}-{version}-guard']
        assert all(str(obj[k])==str(guard[k]) for k in ('identity','length','mtime100ns'))
        assert guard['readOnly'] and guard['shareMode']==1 and guard['identityStatus']=='OPENED_HANDLE_PROVEN'
        objects.append(dict(task=task,key=key,role=obj['role'],identity=obj['identity'],length=obj['length'],mtime100ns=obj['mtime100ns'],disposition=obj['disposition']))
hub=w['callbackHub'];assert hub['lifecycle']=='CLOSED' and not hub['ownershipPending'] and hub['remainingCredits']==[]
assert all(hub[k]==0 for k in ('active','cells','queued','monitorInFlight','workersAlive'))
for worker in hub['workers'].values():assert all(worker[k] for k in ('entered','exited','joined','joinReturned','creditReleased')) and worker['releaseProof']=='THREAD_JOIN_PROVEN'
assert w['privateCells']==dict(active=0,archived=64,peak=1,retained=0,total=64) and len(pre['cellHistory'])==64
for c in pre['cellHistory']:
    assert all(c[k] for k in ('native_done','gated','released','notification_done','notifier_quiescent','archived')) and not c['retained']
    assert c['callbacks_registered']==c['callbacks_finished'] and c['callback_errors']==[]
close=w['logClose'];assert close['id']=='GC/n32' and close['closed'] and close['method']=='flush/fsync/close actually returned' and close['remainingResources']==0
assert set(close['exitedHelpers'])=={'J','R'} and all(p['exited'] and p['code']==0 for p in close['exitedHelpers'].values())
assert launcher['wrapperFacts']['parentProcessHandleCloseProven'] and launcher['wrapperFacts']['parentSpawnCreditsRemaining']==0
assert w['usage']==dict(credit=655360,ib=1573492,ic=59,n=351,qn=83,qr=18,records=32,targets=10,v=128)
assert w['identityQueries']==dict(G=116,J=63,R=53,extraRPCs=0,extraSourceBytes=0,perActorCap=512,queryPurpose='ORIGINAL_OPENED_IDENTITY_LENGTH_MTIME_BEFORE_SOURCE_BYTES')
runtime=w['runtimeObservation'];obs=runtime['observation'];reader=runtime['reader']
assert not runtime['mockMetricsUsed'] and not runtime['nativeQueryPending'] and obs['status']=='OBSERVED' and obs['reasons']==[] and obs['observationFinished']
assert len(numeric)==obs['samples']==reader['cycles']==6 and obs['maxObservedGapSeconds']<=2.5 and obs['sampleDurationSeconds']<=.1
for role,peak in obs['peaks'].items():
    base=obs['baselines'][role];limits=policy['limits'][role]
    for k in ('threads','handles','workingSetBytes','privateBytes'):assert base[k]<=peak[k]<=limits[k] and peak[k]-base[k]<=limits['delta'+k[0].upper()+k[1:]]
assert runtime['originalIdentities']['G']['pid']==claim['child']['pid'] and runtime['originalIdentities']['G']['creationTime100ns']==claim['child']['creationTime100ns']
assert reader['openedHandles']==reader['closedHandles']==20 and not reader['closeUnknown'] and not reader['observerCreditHeld']
fresh={k:get('execution/'+k+'.json') for k in ('fresh-memory','child-memory')};fresh['originalSampler']=runtime['freshMemory']
for f in fresh.values():assert f['status']=='MEMORY_READY' and not f['stopAcceptance'] and f['observation']['availablePhysicalBytes']>=2147483648
assert rm['outputUsage']==dict(fixtureBytes=76,metadataBytes=719573) and rm['combinedUsage']==dict(fixtureBytes=8268,metadataBytes=855814)
assert sum(r['bytes'] for r in collection['outputHashes'])==719649
assert w['metadataRequested']==w['metadataWritten']==6443406 and w['metadataUnknownRequestedBytes']==0 and w['metadataCommitStatus']=='HEALTHY'
assert len(cache[PREFIX+'global.log'])==runtime['log']['eventBytes']+74+metricbytes and metricbytes==575
gc=[(e['id'],e['phase']) for e in events if e['id'].startswith('GC/')]
assert gc==[(f'GC/n{i:02}',p) for i in range(1,32) for p in ('ADMITTED','DONE')]+[('GC/n32','READY_TO_CLOSE')]
assert driver['resources']['productionElapsedSeconds']<=180 and launcher['noInFlight'] and driver['noInFlight'] and rm['noInFlight']
save('semantic-audit.json',dict(at=datetime.now().astimezone().isoformat(),conclusion='PASS_WITHIN_THIS_BATCH_REAL_FINITE_BYTE_IO_SCOPE',newActualRunsByTester=0,coordinatorActualAttempts=1,mediaReread=False,findings=[],windowFacts=windowfacts,independentOutputChecks=outputs,sourcePrefixSha256=sha(payload),sourcePrefixHex=payload.hex(),openedObjects=objects,identityQueries=w['identityQueries'],profileGeometry=claim['profileGeometry'],claim=claim,scenarioCheckpoints=61,preflightCheckpoints=1,assertions=160,originalRuntimeObservation=runtime,originalHelperExits=close['exitedHelpers'],privateCells=w['privateCells'],ledgerPeaks=w['ledgerPeaks'],usage=w['usage'],freshMemory=fresh,productionElapsedSeconds=driver['resources']['productionElapsedSeconds'],metadataCumulativeWritten=w['metadataWritten'],metadataPeak=w['metadataPeak'],finalLogBytes=len(cache[PREFIX+'global.log']),finalMetricBytes=metricbytes,finalEventBytes=len(cache[PREFIX+'global.log'])-metricbytes,resultManifestSha256=collection['resultManifestSha256'],precloseSha256=collection['precloseSha256'],resultReadUsage=usage,noInFlight=True,unexecutedFiniteIOScenarioIds=[],notRun=['five product namespace durability variants','whole-file source hash/snapshot','video decode/playback','NAS','devices/C14','new actual attempt'],D1Passed=False,M0Started=False))
print(json.dumps(dict(status='PASS',windowFacts=windowfacts,outputChecks=outputs,openedObjects=len(objects),readUsage=usage,finalLogBytes=len(cache[PREFIX+'global.log']),finalEventBytes=len(cache[PREFIX+'global.log'])-metricbytes,finalMetricBytes=metricbytes,freshMemory={k:v['observation']['availablePhysicalBytes'] for k,v in fresh.items()}),ensure_ascii=False))
