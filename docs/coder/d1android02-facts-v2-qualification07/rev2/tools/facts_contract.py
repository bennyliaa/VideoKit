"""Exact message bounds and closed structures for this one facts contract."""
import json,hashlib,base64,re
PREAUTH_BYTES=16384
FACT_ENTRY_BYTES=262144
FACT_RAW_BYTES=139264
QUALIFICATION_WIRE_BYTES=16384
EVIDENCE_BYTES=8388608
REVIEW_BYTES=2097152
RECEIPT_FIELDS='schema scope mode sourceSha256 planSha256 routeProofSha256 initialProofSha256 hostEnvironment rawSha256 rawBytes stdoutBytes stderrBytes hostElapsedSeconds collectedAtUtc originalBodyReturned outerControllerReturnStillRequired facts authorizationKind externalPreauthSha256 runtimeBindingSha256 captureStartTick'.split()
BINDING_FIELDS='schema mode preauthSha256 scope planId runId nonce generation ownerPid ownerThread claimFileId scopeStartTick proofStartTick routeProofSha256 initialProofSha256 gateReceiptSha256 sourceSealSha256 gateSourcesSha256 binderSha256 boundAtUtc'.split()
RELEASE_FIELDS='originalUnlockCloseReturned generation failure sdkChildrenEntered endTick allTemporaryThreadsJoined factProofTimely factCaptureQualified outerControllerReturnStillRequired'.split()
GATE_FIELDS='schema scope planId kind generation ownerPid ownerThread checkerPid temporaryResourcesReturned scopeClaimIntentionallyRetained claimFileId claimPath scopeStartTick proofStartTick checkerSourceSha256 gateSourcesSha256 entrySha256 ownerSha256 routeSha256 events controlBeforeReceipt receiptWriteBytes physicalIO sourceHashBytes sourceHashReads'.split()
PROOF_FIELDS='schema id nextId scope controllerPid controllerExited toolStreamsReturned originalResourcesReturnedAtConsole captureQualifiedAtConsole approvedForNext captureReceiptSha256 semanticDependency dependencyAccepted batchSdkChildrenEntered batchTextChargedBytesKnown batchBinaryArchiveBytesKnown batchAmountUnknown batchGroups outerReturnSha256 scopeStartTick outerDelta proofWriteBytes candidateOnlyWriterCloseNotProven'.split()
WIRE_FIELDS='schema representation receipt receiptSha256 parsedFactsSha256 rawBase64 release binding gateReceiptBase64 initialProofBase64 outerProcessReturnStillRequired qualificationIssued sourceBytes sourceReads controlBytes fixtureConstructorCalls fixtureAudit'.split()
def fail(c):raise ValueError(c)
def exact(d,keys,c):
 if type(d) is not dict or set(d)!=set(keys):fail(c)
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def dec(raw,cap,code):
 if type(raw) is not bytes or not 1<=len(raw)<=cap:fail(code+'_BYTES')
 def pairs(items):
  d={};seen=set()
  for k,v in items:
   if k.casefold() in seen:fail(code+'_DUPLICATE')
   seen.add(k.casefold());d[k]=v
  return d
 try:return json.loads(raw.decode('utf-8','strict'),object_pairs_hook=pairs,parse_constant=lambda _:fail(code+'_NUMBER'))
 except (UnicodeError,json.JSONDecodeError):fail(code+'_JSON')
def integer(v,lo=0,hi=9223372036854775807):return type(v) is int and lo<=v<=hi
def hash_string(v):return type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None
def b64(raw):return base64.b64encode(raw).decode('ascii')
def unb64(s,cap,code):
 if type(s) is not str or len(s)>4*((cap+2)//3):fail(code+'_BYTES')
 try:b=base64.b64decode(s,validate=True)
 except (ValueError,TypeError):fail(code+'_BASE64')
 if len(b)>cap or b64(b)!=s:fail(code+'_BASE64')
 return b
def encode_entry(out,gate,raw):
 r=out['receipt'];wire=dict(schema='GLOBAL_IDLE_FACT_ENTRY_RETURN_V2',representation='FACTS_BASE64_SINGLE_COPY_V1',receipt={k:v for k,v in r.items() if k!='facts'},receiptSha256=sha(enc(r)),parsedFactsSha256=sha(enc(r['facts'])),rawBase64=b64(raw),release=out['release'],binding=out['binding'],gateReceiptBase64=b64(gate.receipt_bytes),initialProofBase64=b64(gate.proof_bytes),outerProcessReturnStillRequired=True,qualificationIssued=False,sourceBytes=gate.source_bytes,sourceReads=gate.source_reads,controlBytes=sum(e['bytes'] for e in gate.events)+gate.carry)
 if 'fixtureConstructorCalls' in out:wire.update(fixtureConstructorCalls=out['fixtureConstructorCalls'],fixtureAudit=out['fixtureAudit'])
 data=enc(wire)
 if len(data)>FACT_ENTRY_BYTES:fail('FACT_ENTRY_REPRESENTATION_BOUND')
 return data
def decode_entry(raw,preauth_raw,policy_raw,argv,identity,read_source):
 """Pure packet obligations; original object provenance is checked by caller."""
 from fact_collector import facts,FIXTURE_PY,B
 from fact_preauth import load_pins,validate,utc,same
 import uuid,math
 def uid(v,code):
  try:ok=type(v) is str and str(uuid.UUID(v))==v
  except ValueError:ok=False
  if not ok:fail(code)
 def ints(d,keys,code,low=1):
  for k in keys:
   if not integer(d[k],low):fail(code+':'+k)
 def hashes(d,keys,code):
  for k in keys:
   if not hash_string(d[k]):fail(code+':'+k)
 def bools(d,keys,code,value=True):
  for k in keys:
   if type(d[k]) is not bool or d[k] is not value:fail(code+':'+k)
 try:
  out=dec(raw,FACT_ENTRY_BYTES,'FACT_ENTRY');mode='OFFLINE_FIXTURE' if 'fixtureConstructorCalls' in out else 'LIVE'
  exact(out,WIRE_FIELDS if mode=='OFFLINE_FIXTURE' else [k for k in WIRE_FIELDS if k not in ('fixtureConstructorCalls','fixtureAudit')],'V2_ENTRY_SCHEMA')
  if out['schema']!='GLOBAL_IDLE_FACT_ENTRY_RETURN_V2' or out['representation']!='FACTS_BASE64_SINGLE_COPY_V1':fail('V2_ENTRY_REPRESENTATION')
  bools(out,['outerProcessReturnStillRequired'],'V2_ENTRY_RETURN_FLAG');bools(out,['qualificationIssued'],'V2_ENTRY_QUAL_FLAG',False)
  for k in ('sourceBytes','sourceReads','controlBytes'):
   if not integer(out[k],0,268435456 if k=='sourceBytes' else 64 if k=='sourceReads' else 262144):fail('V2_ENTRY_BUDGET:'+k)
  wire_r=out['receipt'];exact(wire_r,[k for k in RECEIPT_FIELDS if k!='facts'],'V2_RECEIPT_SCHEMA')
  rb=out['binding'];exact(rb,BINDING_FIELDS,'V2_BINDING_SCHEMA');rel=out['release'];exact(rel,RELEASE_FIELDS,'V2_RELEASE_SCHEMA')
  gate_raw=unb64(out['gateReceiptBase64'],16384,'V2_GATE');proof_raw=unb64(out['initialProofBase64'],4096,'V2_PROOF');gr=dec(gate_raw,16384,'V2_GATE');pr=dec(proof_raw,4096,'V2_PROOF');exact(gr,GATE_FIELDS,'V2_GATE_SCHEMA');exact(pr,PROOF_FIELDS,'V2_PROOF_SCHEMA')
  data=unb64(out['rawBase64'],FACT_RAW_BYTES,'V2_RAW');parsed=facts(data)
  r={k:parsed if k=='facts' else wire_r[k] for k in RECEIPT_FIELDS}
  if sha(enc(parsed))!=out['parsedFactsSha256'] or sha(enc(r))!=out['receiptSha256']:fail('V2_RECEIPT_OR_PARSE_HASH')
  hashes(r,['scope','sourceSha256','planSha256','routeProofSha256','initialProofSha256','rawSha256','externalPreauthSha256','runtimeBindingSha256'],'V2_RECEIPT_HASH_TYPE')
  ints(r,['rawBytes','stdoutBytes','captureStartTick'],'V2_RECEIPT_INTEGER');ints(r,['stderrBytes'],'V2_RECEIPT_INTEGER',0)
  bools(r,['originalBodyReturned','outerControllerReturnStillRequired'],'V2_RECEIPT_RETURN')
  if r['schema']!='GLOBAL_IDLE_FACT_CAPTURE_V2' or r['authorizationKind']!='GLOBAL_IDLE_FACT_PREAUTH_V1' or r['hostEnvironment']!='INHERITED_SEVEN_OVERRIDES_ABSENT' or r['mode']!=mode or r['rawBytes']!=len(data) or r['stdoutBytes']!=len(data) or r['stderrBytes']!=0 or r['rawSha256']!=sha(data):fail('V2_RECEIPT_VALUES')
  if type(r['hostElapsedSeconds']) not in (float,int) or not math.isfinite(r['hostElapsedSeconds']) or not 0<=r['hostElapsedSeconds']<15:fail('V2_RECEIPT_DURATION')
  for key in ('generation','planId','nonce'):uid(rb[key],'V2_BINDING_UUID:'+key)
  if type(rb['runId']) is not str or re.fullmatch('D1MA02-[A-Z0-9_-]{1,32}',rb['runId']) is None:fail('V2_BINDING_RUN_ID')
  ints(rb,['ownerPid','ownerThread','claimFileId','scopeStartTick','proofStartTick'],'V2_BINDING_INTEGER')
  hashes(rb,['scope','preauthSha256','routeProofSha256','initialProofSha256','gateReceiptSha256','sourceSealSha256','gateSourcesSha256','binderSha256'],'V2_BINDING_HASH_TYPE')
  if rb['schema']!='GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1' or rb['mode']!=mode:fail('V2_BINDING_KIND')
  bools(rel,['originalUnlockCloseReturned','allTemporaryThreadsJoined','factProofTimely','factCaptureQualified','outerControllerReturnStillRequired'],'V2_RELEASE_RETURN')
  ints(rel,['sdkChildrenEntered','endTick'],'V2_RELEASE_INTEGER');uid(rel['generation'],'V2_RELEASE_GENERATION')
  if rel['failure'] is not None or rel['sdkChildrenEntered']!=1 or rel['generation']!=rb['generation']:fail('V2_RELEASE_VALUES')
  ints(gr,['ownerPid','ownerThread','checkerPid','claimFileId','scopeStartTick','proofStartTick','receiptWriteBytes'],'V2_GATE_INTEGER')
  hashes(gr,['scope','checkerSourceSha256','gateSourcesSha256','entrySha256','ownerSha256','routeSha256'],'V2_GATE_HASH_TYPE')
  ints(gr,['controlBeforeReceipt','sourceHashBytes','sourceHashReads'],'V2_GATE_INTEGER',0)
  bools(gr,['temporaryResourcesReturned','scopeClaimIntentionallyRetained'],'V2_GATE_RETURN')
  if gr['schema']!='ENTRY_GATE_RETURN_V2' or gr['physicalIO']!='UNPROVEN' or gr['sourceHashBytes']>268435456 or gr['sourceHashReads']>64 or gr['receiptWriteBytes']!=len(gate_raw):fail('V2_GATE_VALUES')
  if type(gr['events']) is not list or len(gr['events'])>64:fail('V2_GATE_EVENTS')
  seen=set()
  for e in gr['events']:
   exact(e,{'event','bytes'},'V2_GATE_EVENT_SCHEMA')
   if type(e['event']) is not str or not 1<=len(e['event'].encode())<=128 or e['event'] in seen or not integer(e['bytes'],0,131072):fail('V2_GATE_EVENT_TYPE')
   seen.add(e['event'])
  if sum(x['bytes'] for x in gr['events'])!=gr['controlBeforeReceipt']:fail('V2_GATE_EVENT_SUM')
  p=dec(preauth_raw,PREAUTH_BYTES,'V2_PREAUTH');policy=dec(policy_raw,PREAUTH_BYTES,'V2_POLICY');pins=load_pins(read_source)
  if type(argv) is not list or len(argv) not in (12,16) or argv[:6]!=[FIXTURE_PY,'-I','-X','utf8','-B',str(B/'tools/facts_entry.py')] or argv[6:12:2]!=['--template','--approved-template-sha256','--policy']:fail('V2_OUTER_ENTRY_ARGV')
  if len(argv)==16 and (mode!='OFFLINE_FIXTURE' or argv[12::2]!=['--fixture-raw-file','--fixture-raw-sha256'] or argv[13]!=str(__import__('pathlib').Path(p['home']).parent/'fixture-facts.raw') or argv[15]!=sha(data)):fail('V2_OUTER_FIXTURE_ARGV')
  bound=utc(rb['boundAtUtc']);collected=utc(r['collectedAtUtc']);validate(preauth_raw,argv[9],policy,pins,now=bound)
  if policy_raw!=enc(policy) or not bound<=collected<utc(p['expiresUtc']):fail('V2_FACT_POLICY_OR_TIME')
  if any(rb[k]!=p[k] for k in ('scope','planId','runId','nonce')) or r['scope']!=p['scope'] or rb['preauthSha256']!=sha(preauth_raw) or r['externalPreauthSha256']!=sha(preauth_raw) or r['runtimeBindingSha256']!=sha(enc(rb)):fail('V2_FACT_BATCH')
  if r['sourceSha256']!=pins['collectorSha256'] or r['planSha256']!=pins['factPlanSha256'] or rb['sourceSealSha256']!=pins['sourceSealSha256'] or rb['binderSha256']!=pins['binderSha256'] or rb['gateSourcesSha256']!=pins['gateSourcesSha256']:fail('V2_FACT_SOURCE')
  if any(gr[k]!=rb[k] for k in ('scope','planId','generation','ownerPid','ownerThread','claimFileId','scopeStartTick','proofStartTick','gateSourcesSha256')) or gr['kind']!=('OFFLINE_FIXTURE' if mode=='OFFLINE_FIXTURE' else 'LIVE_LOCAL_METADATA') or gr['ownerPid']!=identity['pid']:fail('V2_GATE_BINDING')
  expected_claim=str(__import__('pathlib').Path(policy['evidenceRoot']).parent/'cooperative-default-route.lock') if mode=='OFFLINE_FIXTURE' else 'D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-production-runner01\\release\\cooperative-default-route.lock'
  if gr['claimPath']!=expected_claim or gr['entrySha256']!=policy['entrySha256'] or gr['ownerSha256']!=policy['outerOwnerSha256'] or gr['gateSourcesSha256']!=policy['gateSourcesSha256'] or gr['checkerSourceSha256']!=json.loads(read_source(B/'reference/runner-source-seal.json'))['sources']['selfchecks/route_fixture.py' if mode=='OFFLINE_FIXTURE' else 'tools/win32_route.py']:fail('V2_GATE_SOURCE_OR_PATH')
  if sha(gate_raw)!=rb['gateReceiptSha256'] or sha(proof_raw)!=rb['initialProofSha256'] or gr['routeSha256']!=rb['routeProofSha256'] or r['routeProofSha256']!=rb['routeProofSha256'] or r['initialProofSha256']!=rb['initialProofSha256']:fail('V2_GATE_RECEIPT_HASH_CHAIN')
  if pr['schema']!='ANDROID02_CAPTURE_COMPLETION_PROOF_V1' or pr['id']!='pre_sdk_local_gate' or pr['nextId']!='identity' or pr['scope']!=rb['scope'] or pr['controllerPid']!=gr['checkerPid'] or pr['scopeStartTick']!=rb['scopeStartTick'] or pr['captureReceiptSha256']!=sha(gate_raw) or pr['outerReturnSha256']!=sha(gate_raw):fail('V2_INITIAL_PROOF_BINDING')
  ints(pr,['controllerPid','scopeStartTick','proofWriteBytes','batchTextChargedBytesKnown'],'V2_PROOF_INTEGER')
  if not integer(pr['batchBinaryArchiveBytesKnown'],0,0):fail('V2_PROOF_BINARY_LEDGER')
  bools(pr,['controllerExited','toolStreamsReturned','originalResourcesReturnedAtConsole','captureQualifiedAtConsole','approvedForNext','dependencyAccepted','candidateOnlyWriterCloseNotProven'],'V2_INITIAL_PROOF_RETURN');bools(pr,['batchAmountUnknown'],'V2_INITIAL_PROOF_UNKNOWN',False)
  exact(pr['batchGroups'],{'preflight','install','instrument','control','payload','command'},'V2_PROOF_GROUP_SCHEMA')
  for k,v in pr['batchGroups'].items():
   if not integer(v,0,1048576) or (k!='control' and v!=0):fail('V2_PROOF_GROUP_VALUES')
  exact(pr['outerDelta'],{'eventId','nativeWriteBytes','proofWriteBytes','additionalForwardBytes','sourceOwnerSha256','gateSourcesSha256','generation','kind'},'V2_PROOF_DELTA_SCHEMA')
  de=pr['outerDelta'];ints(de,['nativeWriteBytes','proofWriteBytes'],'V2_PROOF_DELTA_INTEGER');ints(de,['additionalForwardBytes'],'V2_PROOF_DELTA_INTEGER',0)
  if de['nativeWriteBytes']!=len(gate_raw) or de['proofWriteBytes']!=len(proof_raw) or de['additionalForwardBytes']!=0 or de['sourceOwnerSha256']!=gr['ownerSha256'] or de['gateSourcesSha256']!=gr['gateSourcesSha256'] or de['generation']!=rb['generation'] or de['kind']!=gr['kind'] or de['eventId']!=sha((rb['scope']+'|pre_sdk_local_gate|'+rb['generation']+'|'+sha(gate_raw)).encode()):fail('V2_PROOF_DELTA_BINDING')
  expected_control=gr['controlBeforeReceipt']+len(gate_raw)+len(proof_raw)
  if pr['proofWriteBytes']!=len(proof_raw) or pr['batchTextChargedBytesKnown']!=expected_control or pr['batchGroups']['control']!=expected_control or not integer(pr['batchSdkChildrenEntered'],0,0) or pr['semanticDependency']!='pre_sdk_local_gate_ACTUAL_RETURN_AND_SEMANTIC_PASS':fail('V2_PROOF_LEDGER_BINDING')
  if not rb['scopeStartTick']<=rb['proofStartTick']<=r['captureStartTick']<=rel['endTick'] or r['captureStartTick']-rb['proofStartTick']>=10000 or r['captureStartTick']-rb['scopeStartTick']>=30000 or rel['endTick']-rb['scopeStartTick']>=90000:fail('V2_ORIGINAL_TICK_WINDOWS')
  if mode=='OFFLINE_FIXTURE':
   calls=out['fixtureConstructorCalls'];audit=out['fixtureAudit']
   if type(calls) is not list or len(calls)!=2 or type(audit) is not list or len(audit)!=2:fail('V2_FIXTURE_CALLS')
   for x in calls:
    exact(x,{'argv','constructorReturned'},'V2_FIXTURE_CALL_SCHEMA');bools(x,['constructorReturned'],'V2_FIXTURE_CALL_RETURN')
   for x in audit:exact(x,{'matches'},'V2_FIXTURE_AUDIT_SCHEMA');bools(x,['matches'],'V2_FIXTURE_AUDIT')
   expected_route=[FIXTURE_PY,'-I','-X','utf8','-B',str(B/'selfchecks/route_fixture.py'),str(__import__('pathlib').Path(p['evidenceRoot'])/'gate-context.json')]
   expected_fact=[FIXTURE_PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py')]+(['COMPLETE'] if len(argv)==12 else ['RAW_FILE',argv[13],argv[15]])
   if calls[0]['argv']!=expected_route or calls[1]['argv']!=expected_fact:fail('V2_FIXTURE_CALL_ARGV')
  return dict(receipt=r,binding=rb,release=rel,gate=gr,proof=pr,raw=data,parsed=parsed,preauth=p,policy=policy,pins=pins)
 except ValueError:raise
 except (KeyError,TypeError,AttributeError,OverflowError):fail('V2_NESTED_FIELD_TYPE')
