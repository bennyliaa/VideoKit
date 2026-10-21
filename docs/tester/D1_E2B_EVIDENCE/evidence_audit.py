"""Independent archival decode/arithmetic, never imports candidate modules."""
from pathlib import Path
import hashlib,json,struct,zlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2b'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=read(BASE/'evidence/freeze-summary.json');manifest=read(BASE/'manifest/branches.json');policy=read(BASE/'profiles/runtime-policy.json')
t=read(BASE/freeze['targetedEvidence']);assert t['status']=='PASS' and t['assertions']==sum(g['assertions'] for g in t['groups'])==955
groups={g['module']:g for g in t['groups']};assert groups['alias_checks']['assertions']==46 and groups['diagnostic_checks']['assertions']==65
alias=groups['alias_checks'];assert len(alias['cases'])==4
for c in alias['cases']:
 assert c['controls']==1 and c['rpc']==c['fileByteDelegates']==c['remainingResources']==0 and len(c['opens'])==len(c['closes'])==2
 assert c['opens'][0]['path']==c['opens'][1]['path'] and Path(c['opens'][0]['path']).parent.name=='inputs'
 assert all((p['access'],p['share'],p['creation'],p['flags'])==(0x80000000,1,3,0x80) for p in c['opens'])
 assert c['stoppedObject']['object'] and c['stoppedObject']['ticket'] and c['metadataTransactions']<=2
 if c['case']=='close-unknown':assert c['stoppedObject']['disposition']=='UNKNOWN' and c['controlledCleanup'][0]['newCloseCalls']==0
save('alias-active-chain-review.json',dict(scope='Existing owned-file evidence, no rerun',closure='E2A-A01_STATICALLY_CLOSED_WITH_EXISTING_ACTIVE_CHAIN_EVIDENCE',evidence=alias))
d=read(BASE/freeze['diagnosticEvidence']);summary=read(BASE/'evidence/diagnostic-summary.json');plan=read(BASE/'evidence/diagnostic-reservation.json')
assert len(d['instances'])==2 and [i['method'] for i in d['instances']]==['ADD_TYPE','LOAD_FROM']
assert d['nativeReader']['cycles']==8 and d['nativeReader']['openedHandles']==d['nativeReader']['closedHandles']==16
assert d['workerJoined'] and not d['unknowns'] and not d['remainingResources']
rows=[]
for i,expected in zip(d['instances'],[[498,511,511,513],[497,497,497,499]]):
 identity=i['identity'];assert i['exitProof']['code']==0 and i['exitProof']['exited'] and i['transport']['threadsJoined'] and not i['transport']['errors']
 assert [s['stage'] for s in i['stages']]==['MINIMAL_START','LOAD_COMPLETE','INIT_COMPLETE','HELLO_SERIALIZED']
 assert [s['metrics']['handles'] for s in i['stages']]==expected
 assert i['exitProof']['pid']==identity['pid'] and i['exitProof']['creationTime100ns']==identity['creationTime100ns'] and i['exitProof']['instance']==identity['owner']
 assert int(plan['runId'])<=(identity['creationTime100ns']-116444736000000000)*100
 for s in i['stages']:
  assert s['identity']==identity and s['sameCreationValidatedByReader'] and s['observerFacts']['openedHandles']==s['observerFacts']['closedHandles']
  assert 0<=s['durationSeconds']<=5 and 0<=s['sampleDurationSeconds']<=.1
  rows.append(dict(method=i['method'],identity=identity,stage=s['stage'],metrics=s['metrics']))
 assert 0<=i['durationSeconds']<=30
assert 0<=d['durationSeconds']<=90
first=summary['validation']['firstExceedance'];assert first==dict(method='ADD_TYPE',stage='HELLO_SERIALIZED',metric='handles',value=513,limit=512)
normalized=hashlib.sha256(json.dumps(d,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')).hexdigest()
assert normalized==summary['validation']['diagnosticSha256'] and summary['validation']['eligibleForOneActualSyntheticRegression']
save('fixed-r-diagnostic-review.json',dict(scope='Existing exactly two original instances/eight OS samples, no rerun',rows=rows,costs=d['costs'],nativeReader=d['nativeReader'],firstExceedance=first,normalizedSha256=normalized,rawSha256=sha(BASE/freeze['diagnosticEvidence']),totalSeconds=d['durationSeconds'],causalHandleTypeAttribution=False))
reservation=read(BASE/'evidence/actual-regression-reservation.json');claim=read(BASE/'evidence/actual-regression-claim.json');actual=read(BASE/freeze['actualFullEvidence']);w=actual['witness'];runtime=w['runtimeObservation'];o=runtime['observation']
assert reservation['diagnosticFileSha256']==sha(BASE/freeze['diagnosticEvidence']) and reservation['diagnosticSha256']==normalized and reservation['dllSha256']==sha(BASE/'artifacts/E2B.dll') and reservation['policySha256']==sha(BASE/'profiles/runtime-policy.json')
assert reservation['consumed'] and reservation['maximumActualRuns']==1 and not reservation['realExecutionAllowed']
assert claim==w['actualRegressionAdmission'] and claim['runId']==reservation['runId']==str(actual['started'])
assert claim['controllerPid']==runtime['originalIdentities']['G']['pid'] and claim['launcherPid']==reservation['launcherPid']
assert len(list((BASE/'evidence').glob('run-selfcheck-*.json')))==1 and not list((BASE/'evidence').glob('mock-selfcheck-*.json'))
assert actual['exitCode']==1 and actual['noInFlight'] and not actual['mockMetricsUsed'] and w['status']=='FAIL'
assert o['status']=='STOP_PENDING' and o['baselines']['G']['handles']==160 and o['peaks']['G']['handles']==369 and 369-160==209
assert set(o['reasons'])=={'METRIC_THRESHOLD_EXCEEDED:G:handles','METRIC_DELTA_EXCEEDED:G:handles'}
assert o['baselines']['R']['handles']==o['peaks']['R']['handles']==501 and policy['limits']['G']['handles']==256 and policy['limits']['G']['deltaHandles']==64 and policy['limits']['R']['handles']==512
assert runtime['reader']['cycles']==4 and runtime['reader']['openedHandles']==runtime['reader']['closedHandles']==14 and not runtime['reader']['observerCreditHeld'] and not runtime['nativeQueryPending']
assert w['callbackHub']['lifecycle']=='CLOSED' and not w['callbackHub']['remainingCredits'] and not w['callbackHub']['ownershipPending'] and w['privateCells']==dict(total=44,peak=1,retained=0)
assert w['logClose']['closed'] and w['logClose']['remainingResources']==0 and all(p['exited'] and p['code']==0 for p in w['logClose']['exitedHelpers'].values())
run=BASE/'selfcheck'/w['root'];raw=(run/w['precloseSummary']).read_bytes();assert hashlib.sha256(raw).hexdigest()==w['precloseSummarySha'];pre=json.loads(raw);(OUT/'result-before-close.json').write_bytes(raw)
assert len(pre['rows'])==w['rows']==20 and [r['branch'] for r in pre['rows']]==(['PF']+manifest['executionOrder'])[:20]
assert (['PF']+manifest['executionOrder'])[20]=='P09-TIMEOUT' and 'METRIC_THRESHOLD_EXCEEDED:G:handles' in pre['error']
states={};usage={};unresolved=[]
for task_dir in sorted(p for p in run.iterdir() if p.is_dir() and list(p.glob('state*.slot'))):
 choices=[]
 for path in task_dir.glob('state*.slot'):
  b=path.read_bytes();assert len(b)==8192;seq,n,_=struct.unpack('<qiI',b[:16]);assert seq>0 and 0<=n<=8144;payload=b[48:48+n]
  assert hashlib.sha256(b[:16]+payload).digest()==b[16:48];decoder=zlib.decompressobj();decoded=decoder.decompress(payload,65537);assert decoder.eof and len(decoded)<=65536
  s=json.loads(decoded);assert (s['schema'],s['batch'],s['task'])==(3,run.name,task_dir.name);choices.append((seq,s))
  for row,u in s['usage'].items():
   target=usage.setdefault(row,{k:0 for k in u})
   for k,v in u.items():target[k]=max(target[k],v)
 states[task_dir.name]=max(choices,key=lambda v:v[0])[1]
 for cid,c in states[task_dir.name]['commands'].items():
  if c['status']!='DONE':unresolved.append(dict(task=task_dir.name,command=cid,status=c['status']))
assert len(states)==11 and set(states)==set(states['PF']['inventory'])
for path in (run/'events').glob('*.q'):
 events=[json.loads(line) for line in path.read_bytes().splitlines(keepends=True) if line.endswith(b'\n')]
 assert all(e['batch']==run.name and e['row']==path.stem for e in events)
 u=usage.setdefault(path.stem,{k:0 for k in w['usage']});u['qn']=max(u['qn'],sum(e['new'] for e in events));u['qr']=max(u['qr'],sum(not e['new'] for e in events))
total={k:sum(u[k] for u in usage.values()) for k in w['usage']};assert total==w['usage']
log=(run/'global.log').read_bytes();metrics=[s for s in log.splitlines(keepends=True) if s.startswith(b'[') or s.startswith(b'{"runtimeMetricFormat"')]
assert len(log)==36951 and sum(map(len,metrics))==396 and len(log)-396==36555
metadata=sum(p.stat().st_size for p in run.rglob('*') if p.is_file() and p.name not in ('L.bin','C.bin','Z.bin') and p.suffix!='.out');assert metadata==w['metadataPeak']==234324
save('actual-partial-failure-review.json',dict(scope='Existing actual OS authored-file failure, not rerun',outer=actual,precloseError=pre['error'],completedRows=[r['branch'] for r in pre['rows']],recordCount=len(states),inventory=sorted(states),mergedUsage=total,unresolvedSnapshotCommands=unresolved,finalGlobalLogBytes=len(log),finalMetricBytes=396,finalEventBytes=36555,finalMetadataSizeSum=metadata,fullPassCount=0,partialAssertionsNotCounted=w['assertions']))
save('single-use-admission-review.json',dict(scope='Read-only existing identity/digest bindings plus reviewed CREATE_NEW source; no reserve/claim invoked',reservation=reservation,claim=claim,actualRunCount=1,unusedAfterFailure=False,denials=read(BASE/'evidence/entry-denials.json')))
for rel in [freeze['diagnosticEvidence'],freeze['actualFullEvidence'],'evidence/diagnostic-summary.json','evidence/diagnostic-reservation.json','evidence/actual-regression-reservation.json','evidence/actual-regression-claim.json','evidence/entry-denials.json']:
 path=BASE/rel;(OUT/path.name).write_bytes(path.read_bytes())
save('archived-evidence-review.json',dict(scope='Independent existing evidence only',targetedAssertions=955,partialActualAssertions=77,actualFullPassAssertions=0,diagnosticInstances=2,diagnosticSamples=8,recordCount=11,usage=total,runtimeAdmission=freeze['runtimeAdmission'],fixtureBytes=freeze['syntheticFixtureBytes'],logsAndEvidenceBytesIncludingSeal=freeze['logsAndEvidenceBytesIncludingSeal'],ownFunctionalTests=0,newSampling=False,inFlight=[]))
print(json.dumps(dict(aliasClosed=True,targeted=955,actualStatus='FAIL',actualFullPass=0,admittedRecords=11,candidateUnchanged=True)))
