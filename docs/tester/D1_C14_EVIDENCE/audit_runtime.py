"""Independent review of recorded C14 attempt evidence; no ADB or test dispatch."""
import collections,json,pathlib,re
B=pathlib.Path(__file__).resolve().parent;rows=json.loads((B/'tablet/results.json').read_text(encoding='utf-8'));review=[]
for row in rows:
 if 'attempt' not in row:continue
 o=B/'tablet'/row['attempt'];e=json.loads((o/'post/evidence.json').read_text(encoding='utf-8'));s=(o/'post/host.log').read_text(encoding='utf-8',errors='replace');events=[]
 for line in s.splitlines():
  f=dict(re.findall(r'(\w+)=([^\s]+)',line))
  if f.get('stage','').startswith('CPU_') or f.get('stage')=='EXIT_EVIDENCE':events.append(f)
 violations=[];identities={};primary={};dead={};released=set();starts=[];frames=[];registrations=[];exits=[];budget=[];calls={}
 for f in events:
  stage=f['stage'];task=f.get('task');gen=f.get('generation');key=(task,gen);pair=(f.get('pid'),f.get('uid'))
  if stage=='CPU_GENERATION_REGISTERED':
   if task in released:violations.append('REGISTER_AFTER_RELEASE:'+str(key))
   if key in identities and identities[key]!=pair:violations.append('GENERATION_IDENTITY_CHANGED:'+str(key))
   identities[key]=pair;dead.setdefault(key,False)
   if f.get('primary')=='true':
    if task in primary and primary[task]!=pair:violations.append('PRIMARY_IDENTITY_CHANGED:'+task)
    primary[task]=pair
  if stage=='CPU_GENERATION_DEATH':
   if key in identities and identities[key]!=pair:violations.append('DEATH_IDENTITY_MISMATCH:'+str(key))
   dead[key]=True
  if stage=='CPU_TASK_STARTED':
   starts.append(f)
   if task in released or primary.get(task)!=pair:violations.append('START_WITHOUT_PRIMARY_OR_AFTER_RELEASE:'+str(task))
  if stage in ['CPU_FRAME','CPU_PREALLOC_BUDGET']:
   if primary.get(task)!=pair:violations.append('MEDIA_ON_NONPRIMARY:'+str(task))
   if stage=='CPU_FRAME':frames.append(f)
  if stage=='CPU_REGISTRATION_DIAG':registrations.append(f)
  if stage=='EXIT_EVIDENCE':exits.append(f)
  if stage=='CPU_BINDING_LEDGER':budget.append(f)
  if stage=='CPU_LEDGER':
   if pair!=('-1','-1') and task in primary and primary[task]!=pair:violations.append('FINAL_PUBLIC_IDENTITY_CHANGED:'+task)
   calls[task]=f
   if f.get('slot_released')=='true':
    if any(not value for k,value in dead.items() if k[0]==task):violations.append('SLOT_WITH_UNPROVEN_GENERATION:'+task)
    if f.get('pending_calls')!='0' or f.get('source_released')!='true' or f.get('stop_pending')!='false':violations.append('SLOT_WITH_PENDING:'+task)
    released.add(task)
 if row['result']=='PASS':assert not violations,(row['method'],violations)
 review.append(dict(method=row['method'],result=row['result'],instrumentationFinished=e['instrumentationCompletion'],activeWorkersAtPost=e['activeWorkerLines'],violations=violations,primaryIdentities={k:list(v) for k,v in primary.items()},registeredGenerations=[dict(task=k[0],generation=k[1],pid=v[0],uid=v[1],observedDeath=dead.get(k,False)) for k,v in identities.items()],starts=starts,frames=frames,registrationEvents=registrations,exitEvents=exits,budgetSnapshots=budget,finalCpu=e['lastCpuLedger'],finalGeneration=e['lastGenerationLedger'],finalBinding=e['lastBindingLedger'],finalUnbind=e['lastUnbindLedger'],rawProof=e['rawProof']))
(B/'runtime-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8');print(str(len(review))+' recorded methods independently reviewed; no identity/media/slot violations in PASS attempts')
