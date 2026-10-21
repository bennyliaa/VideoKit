"""Independent JSON arithmetic/source inspection. No candidate imports or OS/media probes."""
from pathlib import Path
import ast,hashlib,json
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2';OLD=ROOT/'docs/coder/d1e1e'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=read(BASE/'profiles/cases.json');inputs=read(BASE/'profiles/inputs.json');policy=read(BASE/'profiles/runtime-policy.json');manifest=read(BASE/'manifest/branches.json');old=read(OLD/'manifest/branches.json')
assert sha(BASE/'evidence/freeze-summary.json')=='06a799a0ba39eb76c9887fc7b5690fc29f20e1ee826c6067e9f8a322a9273ae2'
assert sha(BASE/'artifacts/E2-source.zip')=='4e3510c4cba3c99919faf26cf5ff72ab2ebe4ada2fcf7db3690fba4451b312c2'
assert len(c['cases'])==61 and c['limits']==old['limits']==manifest['limits']
oldrows={r['id']:r for r in old['branches']};alloc=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')
windows=[2147483648-65536,2147483648-32768,2147483648,3212959911-65536]
assert [(w['offset'],w['requestedBytes']) for w in inputs['largeFileWindows']['windows']]==[(o,65536) for o in windows]
rows=[];totals=dict(inputBytes=0,inputCalls=0,validationBytes=0)
def usage(ws):
 u=dict(inputBytes=0,inputCalls=0,validationBytes=0)
 for w in ws:
  assert type(w['inputRequestCharged']) is bool and type(w['requestedBytes']) is int
  if not w['inputRequestCharged']:assert w['requestedBytes']==w['delegateCalls']==0;continue
  if w['budgetClass']=='INPUT':u['inputBytes']+=w['requestedBytes'];u['inputCalls']+=1
  else:assert w['budgetClass']=='VALIDATION';u['validationBytes']+=w['requestedBytes']
 return u
pf=usage(c['phaseProfiles']['PF']['windows']);assert pf==dict(inputBytes=32,inputCalls=2,validationBytes=0);totals.update(pf)
for r in c['cases']:
 assert all(r[k]==oldrows[r['id']][k] for k in alloc),r['id']
 u=usage(r['realIO']['windows']);assert u==r['realIO']['expectedRequestUsage'] and all(u[k]<=r[k] for k in u)
 for k,v in u.items():totals[k]+=v
 if r['id'].startswith('P01-N'):
  offset=windows[int(r['id'][-1])-1];assert [(w['offsetBytes'],w['requestedBytes']) for w in r['realIO']['windows']]==[(offset,65536)]*2
 if r['id'].startswith('P01-S'):
  offset=windows[int(r['id'][-1])-1];assert [(w['offsetBytes'],w['requestedBytes']) for w in r['realIO']['windows']]==[(offset+i,65536-i) for i in range(4)]+[(offset,4)]
 d=r['requiredDurability'];assert d['level']==('NONE' if r['id'].startswith('P') else 'OS_DATA_SYNC_ACK')
 assert not d['productReady'] and not d['businessCommit'] and not d['powerLossClaim']
 if r['productVariant'].get('requiredDurability')=='NAMESPACE_DURABLE':assert r['productVariant']['admission']=='NOT_RUN_DURABILITY_UNPROVEN'
 rows.append(dict(id=r['id'],allocationPreserved=True,usage=u,durability=d,productVariant=r['productVariant'],windows=r['realIO']['windows'],outputWrites=r['realIO']['outputWrites'],injectedEffects=r['realIO']['injectedEffects']))
assert totals==c['plannedRequestUsage']==dict(inputBytes=1573492,inputCalls=59,validationBytes=128)
assert sum(r['requiredDurability']['level']=='NONE' for r in c['cases'])==31
assert sum(r['requiredDurability']['level']=='OS_DATA_SYNC_ACK' for r in c['cases'])==30
namespace=[r['id'] for r in c['cases'] if r['productVariant'].get('requiredDurability')=='NAMESPACE_DURABLE'];assert len(namespace)==5
assert policy['maxSamples']*policy['maxRecordBytes']+1024==policy['maxLogBytes']==26752
assert 104320+26752==131072 and 23+1==24
assert policy['minimumAvailablePhysicalBytes']==2147483648 and policy['state']=='PROPOSED'
save('configuration-and-budget-audit.json',dict(scope='Static frozen configuration only; no media/stat/native/entry execution',at=datetime.now().astimezone().isoformat(),windows=windows,rows=rows,totals=totals,unusedInputBytes=1573522-totals['inputBytes'],sourceCases=31,outputCases=30,namespaceVariantsNotRun=namespace,observerLogArithmetic=dict(events=104320,metrics=26752,total=131072,cycles=201,recordBytes=128,headerBytes=1024),observerCreditArithmetic=dict(existingManagedPeak=23,temporaryObserver=1,total=24,doesNotProve='Fresh peak or OS/runtime totals'),runtimePolicy=policy,state='CONFIGURATION_REVIEW_ONLY_NOT_RUNNABLE'))
preserved=[]
for rel in ['src/authority.py','src/recovery.py','src/recovery_checks.py','src/metadata_checks.py','src/Native.cs','src/Core.cs']:
 same=(BASE/rel).read_bytes()==(OLD/rel).read_bytes();assert same,rel
 preserved.append(dict(path=rel,sha256=sha(BASE/rel),unchangedFromE1E=True))
for rel in ['src/notifications.py','src/startup_checks.py']:
 same=(BASE/rel).read_text(encoding='utf-8')==(OLD/rel).read_text(encoding='utf-8').replace('E1E','E2');assert same,rel
 preserved.append(dict(path=rel,sha256=sha(BASE/rel),unchangedFromE1E=False,onlyChanges='E1E -> E2 literal label/thread name/scope',unchangedAfterExplicitLabelNormalization=True))
save('preserved-fix-audit.json',dict(scope='Static byte identity; no regression rerun',preserved=preserved))
for rel in ['evidence/adapter-feasibility.json','evidence/entry-denials.json','evidence/observer-self-1792165801337125700.json']:
 p=BASE/rel;(OUT/p.name).write_bytes(p.read_bytes())
t=read(BASE/'evidence/targeted-1792165801504473800.json');assert t['assertions']==716
group=next(g for g in t['groups'] if g['assertions']==97);assert group['status']=='PASS' and len(group['checks'])==97
obs=read(BASE/'evidence/observer-self-1792165801337125700.json');assert obs['assertions']==6 and not obs['experimentBaseline'] and not obs['experimentRuntimePeak']
assert obs['nativeReaderFacts']['openedHandles']==obs['nativeReaderFacts']['closedHandles']==2 and obs['nativeReaderFacts']['maximumOwnedHandlesObserved']==1
save('configuration-evidence-review.json',dict(scope='Existing producer evidence only, no rerun',integration=159,targeted=716,syntheticTotal=875,e2ConfigurationGroup=group,separateSelfProcessMetadataAssertions=6,notGJRExperimentBaseline=True,observerSelf=obs,entryDenials=read(BASE/'evidence/entry-denials.json')))
print(json.dumps(dict(configurationArithmetic='PASS',preservedFixes='PASS',rows=61,syntheticEvidence=875,ownFunctionalTests=0)))
