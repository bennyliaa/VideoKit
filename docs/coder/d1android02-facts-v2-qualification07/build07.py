"""Assertion-backed construction of independent declared revision directories."""
from pathlib import Path
import json,zipfile,hashlib,re,uuid,sys
R=Path(__file__).resolve().parent;rev=sys.argv[1] if len(sys.argv)>1 else 'REV1';assert rev in ('REV1','REV2');H=R/rev.lower();H.mkdir(exist_ok=True)
if rev=='REV2':
 prior=json.loads((R/'rev1/evidence/result.json').read_bytes());assert prior['revisionReturnProof']['allOriginalsProven'] and prior['auxOriginalsReturned'] and not any(prior['custody'].values()) and not prior['allPassed'],'REV2_REQUIRES_ALL_ORIGINAL_RETURN_PROOFS'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def put(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
work=R.parent/'D1_FACTS_V2_QUALIFICATION07_CODER_REQUIREMENTS_V1.0.md';assert sha(work.read_bytes())=='405448bc78b15cd64e4fa3ee66cf8e35a13af58af0e0983168bc9ac3a88d8d0c'
declaration=R/'batch-declaration07.json'
if not declaration.exists():save(declaration,dict(schema='QUALIFICATION07_TWO_REVISION_DECLARATION_V1',revisions=[dict(id=x,root=str(R/x.lower()),seed=str(uuid.uuid4()),expectedProductGraph=23,conditionalMaxGraph=25,readReservationBytes=469762048,savedReservationBytes=7340032) for x in ('REV1','REV2')],scopeDerivation='UUID5(revision seed,label); fresh revision root and source-sealed scope formula; independent nonce UUID5(seed,sourceSeal+nonce)',REV2OnlyAfterAllOriginalsReturnedAndNoNewUNKNOWN=True,firstFullPassStops=True,maxProductGraphs=50,maxIncludingSetupHelpers=56,processCap=96,wholeSeconds=360,stopNew=320,readCap=1073741824,totalReadReservation=1006632960,twoRevisionReadReservation=939524096,setupReadReservation=67108864,savedCap=16777216,twoRevisionSavedReservation=14680064,archiveReservation=1572864,reportReservation=524288,concurrency=1,scopeRetry=0,SDK=0,oldObjects='NO_QUERY_NO_MUTATION'))
D=json.loads(declaration.read_bytes());assert D['totalReadReservation']<D['readCap'] and D['twoRevisionSavedReservation']+D['archiveReservation']+D['reportReservation']==D['savedCap']
assert not (H/'evidence/result.json').exists(),'EXECUTED_REVISION_IMMUTABLE'
assert not (H/'evidence/execution-entered.json').exists(),'STARTED_REVISION_IMMUTABLE'
Z=R.parent/'d1android02-facts-v2-qualification06/QUALIFICATION06-frozen.zip';assert sha(Z.read_bytes())=='250c98231da3df0ae87e9f99f733e030a15de6d25c0ec8adf4a3531e3e4e4fd5'
patches=[]
def replace(s,old,new,n=1,label=''):
 actual=s.count(old);assert actual==n,(label or old[:100],actual,n)
 patches.append(dict(id=label or old[:100],expected=n,actual=actual));return s.replace(old,new)
def regex(s,pat,new,n=1,label=''):
 s,c=re.subn(pat,new,s);assert c==n,(label or pat,c,n);patches.append(dict(id=label or pat,expected=n,actual=c));return s
with zipfile.ZipFile(Z) as z:
 mf=z.read('reference/full-manifest.json');assert sha(mf)=='68dd9820be6eeaf585cbe22793f8a4bc4a1b279acc6356ced0d6dcaa4b8d2e1d';m=json.loads(mf);assert len(m['files'])==132
 for e in m['files']:assert len(z.read(e['path']))==e['bytes'] and sha(z.read(e['path']))==e['sha256']
 old=json.loads(z.read('reference/runner-source-seal.json'))['sources'];names=[x for x in old if x!='reference/fact-preauth-schema.json'];assert len(names)==30
 for e in m['files']:
  rel=e['path']
  if not (rel.startswith(('tools/','driver/','release/','selfchecks/')) or rel in ('worker06.py','prepare06.py','preflight06.py','pure_budget06.py','capacity_preflight06.py','parse06.ps1','write_guard.py')):continue
  if rel.startswith('selfchecks/work/'):continue
  raw=z.read(rel);new=rel.replace('06.py','07.py').replace('06.ps1','07.ps1')
  if rel!='tools/runtime_binding.py':
   s=raw.decode()
   if rev=='REV2':s=s.replace('qualification06\\','qualification07\\'+rev.lower()+'\\')
   s=s.replace('qualification06','qualification07/'+rev.lower()).replace('QUALIFICATION06','QUALIFICATION07').replace('Q06','Q07').replace('q06-','q07-').replace('plan06','plan07').replace('profile06','profile07').replace('preflight06','preflight07').replace('driver_guard06','driver_guard07').replace('call_plan06','call_plan07').replace('parse06','parse07').replace('ps-parse06','ps-parse07').replace('control-envelope-pure06','control-envelope-pure07');raw=s.encode()
  p=H/new;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 for e in m['files']:
  rel=e['path']
  if rel.startswith('reference/') and rel not in ('reference/runner-source-seal.json','reference/gate-sources.json','reference/profile06.json','reference/plan06.json','reference/fact-source-plan06.json','reference/upstream-before.json','reference/source-delta.json','reference/source-delta.patch'):
   p=H/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(rel))
 schema_raw=z.read('reference/fact-preauth-schema.json').decode();schema=json.loads(schema_raw)
 p=H/'tools/fact_preauth.py';s=p.read_text();s=regex(s,r"KEYS=set\([^\n]+\)",lambda _:"FACT_PREAUTH_SCHEMA07_RAW="+repr(schema_raw)+"\nFACT_PREAUTH_SCHEMA07=json.loads(FACT_PREAUTH_SCHEMA07_RAW)\nKEYS=set(FACT_PREAUTH_SCHEMA07['required'])\nassert FACT_PREAUTH_SCHEMA07['additionalProperties'] is False and FACT_PREAUTH_SCHEMA07['properties']['schema']['const']=='GLOBAL_IDLE_FACT_PREAUTH_V1'",label='preserve-whole-schema-under-existing-producer-pin')
 s=replace(s," if fixture:\n  read('route-preconstructor'"," if fixture:\n  read('route-child-reservation',B/'selfchecks/route_fixture.py','route-child-reservation','ORIGINAL_GATE_FOR_FIXED_CHILD',0)\n  read('route-preconstructor'",label='include-route-child-self-read')
 s=replace(s," else:add('native-image-reservation'"," else:\n  read('route-child-reservation',B/'tools/win32_route.py','route-child-reservation','ORIGINAL_GATE_FOR_FIXED_CHILD',0)\n  add('native-image-reservation'",label='include-live-route-child-self-read')
 put(p,s)
 if rev=='REV2':
  for rel in ('selfchecks/contract_cases.py','selfchecks/independent_cases_original.py'):
   p=H/rel;s=replace(p.read_text(),"B.parent/'d1android02-global-idle-semantics01/","Path('D:/CodexProjects/VideoKit/docs/coder')/'d1android02-global-idle-semantics01/",label='REV2-fixed-archived-fixture-root:'+rel);put(p,s)
 p=H/'tools/fact_collector.py';s=replace(p.read_text()," gate.source_bytes+=len(raw);gate.source_reads+=1"," gate.source_charge(argv[7],len(raw),'child-reservation')",label='F01-exact-one-space-raw-child-reservation');assert 'gate.source_bytes+=len(raw)' not in s;put(p,s)
 # Preserve original Runner counters and add explicit corresponding events.
 p=H/'tools/production_runner.py';s=replace(p.read_text(),'self.receipt_reads=[]','self.receipt_reads=[];self.source_fee_events=[]',label='Runner-source-fee-records')
 s=replace(s,'   self.source_bytes+=reservation;self.source_reads+=1',"   self.source_bytes+=reservation;self.source_reads+=1;fee=dict(path=str(path),kind='runner-source-read',chargedBytes=reservation,reads=1,actualBytes=None,originalReturned=False);self.source_fee_events.append(fee)",label='Runner-read-charge-event')
 s=replace(s,"  elif len(b)>=reservation:raise ValueError('RUNNER_SOURCE_SIZE_CHANGED')","  elif len(b)>=reservation:raise ValueError('RUNNER_SOURCE_SIZE_CHANGED')\n  if lane is None:fee.update(actualBytes=len(b),originalReturned=True)",label='Runner-read-original-return')
 s=replace(s,'\n  self.source_bytes+=reservation;self.source_reads+=1',"\n  self.source_bytes+=reservation;self.source_reads+=1;receipt_fee=dict(path=str(path),kind='runner-original-receipt',chargedBytes=reservation,reads=1,actualBytes=None,originalReturned=False);self.source_fee_events.append(receipt_fee)",label='Runner-receipt-charge-event')
 s=replace(s,"  self.receipt_reads.append(observed)","  self.receipt_reads.append(observed);receipt_fee.update(actualBytes=observed['readBytes'],originalReturned=observed['originalCloseReturned'])",label='Runner-receipt-original-return')
 put(p,s)
 p=H/'tools/entry_gates.py';s=p.read_text();s=replace(s,"  prepared=subprocess.Popen.preflight(argv,**route_kw)","  self.source_charge(script,script.stat().st_size,'route-child-reservation')\n  prepared=subprocess.Popen.preflight(argv,**route_kw)",label='reserve-child-self-hash-before-original-Popen');put(p,s)
 # Always persist complete current rows before testing the final equality.
 p=H/'tools/facts_entry.py';s=p.read_text();check="  if g.source_reads!=ticket.sourcePlan['sourceReads'] or g.source_bytes!=ticket.sourcePlan['sourceBytes'] or len(g.source_events)!=len(ticket.sourcePlan['rows']):raise ValueError('FACT_COMPLETE_SOURCE_PLAN_ACTUAL_MISMATCH')\n";s=replace(s,check,'',label='move-final-compare-after-durable-rows');at=s.index(' except BaseException:\n  import time');s=s[:at]+check+s[at:];put(p,s)
 s=replace(s,"   if getattr(c,'bodyReturned',False):c.finish_after_original_collect_return(g)","   if getattr(c,'bodyReturned',False):\n    rejected_release=c.finish_after_original_collect_return(g);g.write('facts-known-rejection-release.json',encode(dict(originalRelease=rejected_release,originalFactsBodyReturned=True,constructorEntered=c.entered,knownRejection=True)))",label='known-body-returned-rejection-original-release-witness')
 s=replace(s,"   elif not c.entered and not g.released and g.lease is not None and not g.lease.closed:g.release()","   elif not c.entered and not g.released and g.lease is not None and not g.lease.closed:\n    rejected_release=g.release();g.write('facts-known-rejection-release.json',encode(dict(originalRelease=rejected_release,originalConstructorEntered=False,knownRejection=True)))",label='known-preconstructor-rejection-original-release-witness');put(p,s)
 # Exact source membership and caller constants, in dependency order.
 p=H/'tools/production_runner.py';s=regex(p.read_text(),r'SOURCE_FILES=\([^\n]+\)','SOURCE_FILES='+repr(tuple(names)),label='source-membership30');put(p,s)
 p=H/'tools/admission_checks.ps1';s=regex(p.read_text(),r" \$srcKeys=@\([^\n]+\)"," $srcKeys=@("+','.join(repr(x) for x in names)+")",label='PS-source-membership30');put(p,s)
 gate=json.loads(z.read('reference/gate-sources.json'));gate['files']=[e for e in gate['files'] if e['path'] in names];assert len(gate['files'])==22
 old_gate=sha(z.read('reference/gate-sources.json'))
 # Preserve original runtime exact bytes despite all path adaptation.
 assert sha((H/'tools/runtime_binding.py').read_bytes())=='47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982'
 def digest(rel):return sha((H/rel).read_bytes())
 pin_symbols={'GICollectorSha256':'tools/fact_collector.py','GIFactPlanSha256':'reference/fact-plan.json','GIV2AdapterSha256':'tools/facts_qualification.py','GIV2CaptureSha256':'tools/outer_capture.py','GIV2OriginSha256':'tools/capture_origin.py'}
 p=H/'tools/admission_checks.ps1';s=p.read_text()
 for symbol,rel in pin_symbols.items():s=regex(s,r"(\$script:"+symbol+r"=')[0-9a-f]{64}(')",lambda m:m[1]+digest(rel)+m[2],label='named-consumer:'+symbol)
 s=replace(s,old['tools/production_runner.py'],digest('tools/production_runner.py'),2,label='PS-original-Runner-pin');put(p,s)
 for e in gate['files']:e['sha256']=digest(e['path'])
 save(H/'reference/gate-sources.json',gate);gh=digest('reference/gate-sources.json')
 p=H/'tools/outer_owner.py';s=replace(p.read_text(),old['tools/production_runner.py'],digest('tools/production_runner.py'),label='Owner-original-Runner-pin');s=replace(s,old_gate,gh,label='Owner-Gate-pin');put(p,s)
 p=H/'tools/capture_android02.ps1';s=p.read_text()
 for rel,count in (('tools/outer_owner.py',5),('tools/admission_checks.ps1',1)):s=replace(s,old[rel],digest(rel),count,label='entry-pin:'+rel)
 # Gate hash occurs both in its explicit constant and a comparison, and must
 # update every exact occurrence; record the count before applying.
 count=s.count(old_gate);assert count>=1;s=replace(s,old_gate,gh,count,label='entry-all-Gate-pin-consumers');put(p,s)
 save(H/'reference/runner-source-seal.json',dict(schema='PRODUCTION_RUNNER_SOURCE_SEAL_V1',sources={x:digest(x) for x in names}))
 p=H/'release/capture-policy.json';v=json.loads(p.read_bytes())
 for k,rel in [('entrySha256','tools/capture_android02.ps1'),('outerOwnerSha256','tools/outer_owner.py'),('gateSourcesSha256','reference/gate-sources.json'),('runnerSourceSha256','tools/production_runner.py')]:v[k]=digest(rel)
 save(p,v)
 save(H/'reference/upstream06-zip-audit.json',dict(files=132,bytes=m['bytes'],bad=0,zipSha256=sha(Z.read_bytes()),manifestSha256=sha(mf),old05ActiveReads=0))
 save(H/'reference/source-schema-consolidation07.json',dict(originalSchemaSha256=sha(schema_raw.encode()),completeRawContractEmbedded=True,requiredKeysPreserved=sorted(schema['required']),source30=names,gate22=[e['path'] for e in gate['files']],routeChildSelfReadStillPerformed=True,newParentReservationBeforePopen=True))
save(H/'reference/build-patch-audit07.json',dict(allExactCounts=True,patches=patches,revision=rev,scopeRetry=0))
put(H/'WORK_ORDER.md',work.read_text())
print(json.dumps(dict(revision=rev,source30=len(names),gate22=len(gate['files']),assertedPatches=len(patches),productCalls=0)))
