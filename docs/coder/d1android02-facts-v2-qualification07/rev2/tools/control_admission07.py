"""Pre-resource UTF8 reservations against the existing control byte ceilings.

Future receipt/console use their existing 8192-byte ceilings, not a guessed
path length. Known input messages use the same builders as materialization.
All values are reservations; this is not evidence of a future OS return.
"""
from pathlib import Path
import copy,json
from entry_gates import encode,sha

def size(d):
 # ConvertTo-Json additionally escapes these Unicode separators. Account for
 # that spelling on every PS-origin message, even where Python emits UTF8.
 s=encode(d).decode().replace('\u0085','\\u0085').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
 return len(s.encode())

def admit(r,template,shapes):
 if shapes.get('schema')!='CONTROL_MESSAGE_SHAPES05_V1' or shapes.get('syntheticReservationOnly') is not True:raise ValueError('CONTROL_ENVELOPE_SCHEMA')
 p,local=r.policy_definition(template);h=str(r.home);root=str(r.root);scope=r.permit['scope'];z='b'*64
 p.update(authorization=dict(path=str(r.home/'release/activation.json'),sha256=z),freshRouteProof=dict(path=str(r.root/'fresh-route.json'),sha256=z))
 activation=r.activation_definition(p,z,z)
 def expand(v,role='identity'):
  if type(v) is dict:return {k:expand(x,role) for k,x in v.items()}
  if type(v) is list:return [expand(x,role) for x in v]
  if type(v) is str:
   for a,b in (('@HOME@',h),('@ROOT@',root),('@SCOPE@',scope),('@ROLE@',role)):v=v.replace(a,b)
  return v
 components={'permit':len(r.permit_bytes),'approval':len(r.approval_bytes),'policy':len(encode(p)),'activation':len(encode(activation)),'sourceSeal':len(encode(dict(schema='PRODUCTION_RUNNER_SOURCE_SEAL_V1',sources=r.permit['sources']))),'localAuthorization':len(encode(local))}
 # Source seal is physically pretty-printed; caller supplies original bytes.
 components['sourceSeal']=r.capacity_source_seal_bytes
 pre=list(r.pre)
 # Original copy read/write + fixed finite fixture records; no file creation.
 for rel in ('tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/route-backend-contract.json'):
  for op in ('copy-read:','copy-write:'):pre.append(dict(event=op+rel,bytes=r.capacity_copy_bytes[rel]))
 if r.fixture:
  pre.extend([dict(event='fixture-budget-marker',bytes=1),dict(event='fixture-payload:4',bytes=4096),dict(event='fixture-payload:5',bytes=2048)])
 pre.extend([dict(event='policy-template-read',bytes=r.capacity_template_bytes),dict(event='local-authorization-write',bytes=components['localAuthorization'])])
 gate=expand(shapes['gate']);gate['events']=pre+[dict(event=n,bytes=131072) for n in ('write:gate-context.json','checker-command','checker-context-read','checker-stream-read','write:gate-stdout.bin','write:gate-stderr.bin','checker-native-metadata-known','write:fresh-route.json')]
 proof=expand(shapes['proof']);proof.update(id='pre_sdk_local_gate',nextId='global_idle',semanticDependency='pre_sdk_local_gate_ACTUAL_RETURN_AND_SEMANTIC_PASS')
 components.update(gate=size(gate),fresh=size(expand(shapes['fresh'])),proof=size(proof),materialization=size(expand(shapes['materialization'])))
 # Both completion proof variants have fixed strings/fields. The initial proof
 # has the larger outerDelta, and all its counters use maximal integer widths.
 caps=dict(permit=32768,approval=8192,policy=65536,activation=8192,sourceSeal=16384,gate=16384,fresh=16384,proof=4096,materialization=16384,localAuthorization=8192)
 def check(name,n,cap):
  if n>cap:raise ValueError('CONTROL_ENVELOPE_'+name.upper()+':'+str(n)+'>'+str(cap))
 for k,n in components.items():check(k,n,caps[k])
 roles=[]
 for i,s in enumerate(r.permit['roles']):
  role=s['id'];request=dict(schema='ANDROID02_CAPTURE_REQUEST_V1',id=role,policySha256=z,scope=scope,evidenceRoot=root,argv=s['argv'],maxTextBytes=s['maxTextBytes'],maxBinaryBytes=0,qualificationSeconds=s['qualificationSeconds'])
  request_n=size(request);admission_n=size(expand(shapes['admission'],role));check('request',request_n,8192);check('admission',admission_n,4096)
  intent_n=size(dict(schema='ANDROID02_CAPTURE_INTENT_V1',request=request,owner='0'*36,controllerPid=2147483647,policySha256=z));check('intent',intent_n,8192)
  argv=['C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-NonInteractive','-File',str(r.home/'tools/capture_android02.ps1'),'-RequestPath',str(r.home/('request-'+role+'.json')),'-PredecessorProofSha',z,'-OwnerAdmissionSha',z]
  native=expand(shapes['native'],role);native['argv']=argv;native_n=size(native);check('native',native_n,16384)
  # All functional ReadJsonExact calls, including policy/request/admission.
  read=components['policy']+request_n+admission_n+components['proof']
  if i==0:
   read+=sum(components[k] for k in ('gate','fresh','permit','approval','sourceSeal','materialization','activation'))
   if not r.fixture:read+=components['activation']+components['fresh']
  else:read+=8192+8192+roles[-1]['nativeBytes'] # receipt + console + native
  # Receipt and console use their full existing protocol caps. Halt record
  # (512) is the fixed schema/reason record; firstFailure is a fixed code.
  record=intent_n+8192+2048
  local=record+2*8192+read
  check('controller_65536',local,65536)
  roles.append(dict(role=role,requestBytes=request_n,admissionBytes=admission_n,intentBytes=intent_n,receiptBytes=8192,consoleBytes=8192,haltBytes=2048,nativeBytes=native_n,functionalReadBytes=read,localControlBytes=local))
 pre_n=sum(e['bytes'] for e in pre)
 post_n=components['permit']+components['approval']+components['fresh']+components['proof']+2*components['activation']+2*components['policy']+components['materialization']
 receiver_n=components['policy']+components['activation']+components['materialization']+components['gate']+components['proof']
 # Exact checker context/argv and complete route field set (its queryStats
 # schema is the same as fresh-route), instead of adding every local cap.
 context=dict(kind=r.kind if not r.fixture else 'OFFLINE_FIXTURE',scope=scope,planId=r.permit['planId'],generation='0'*36,toolPath='D:/Android/SDK/platform-tools/adb.exe',toolSha256=p['toolSha256'],toolBytes=8273560,routeBackend=p['routeBackend'])
 if r.fixture:context.update(fixtureDelay=0,fixtureFault='NONE')
 route=expand(shapes['fresh']);route={k:route[k] for k in ('scope','planId','checkedAtUtc','serverPid','serverCreationUtc','serverImage','serverFileSha256','routingOverrides','sourceSha256','routeBackend','queryStats')}
 route.update(schema='ENTRY_LOCAL_ROUTE_V2',kind=context['kind'],generation='0'*36,endpoint='127.0.0.1:5037',identityStable=False,contextReadBytes=size(context),queryCount=4)
 checker=Path(__file__).resolve().parents[1]/('selfchecks/route_fixture.py' if r.fixture else 'tools/win32_route.py')
 command=['C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-I','-X','utf8','-B',str(checker),str(r.root/'gate-context.json')]
 gate_n=2*size(context)+size(command)+2*size(route)+components['fresh']+(0 if r.fixture else 40960)
 shared=pre_n+post_n+receiver_n+gate_n+components['gate']+components['proof']
 check('shared_262144',shared,262144)
 batch=shared+sum(x['localControlBytes']+x['requestBytes']+x['admissionBytes']+x['nativeBytes']+4096 for x in roles)+8192
 check('batch_1048576',batch,1048576)
 return dict(schema='CONTROL_ENVELOPE_ADMISSION05_V1',stage='BEFORE_GATE_CLAIM_ONCE_MATERIALIZATION_CONTROLLER',utf8=True,futureAmounts='RESERVATIONS_NOT_ORIGINAL_RETURN_EVIDENCE',independentEvidenceRoot=r.permit['globalIdleQualification'].get('evidenceRoot'),home=h,components=components,roles=roles,sharedBytes=shared,batchBytes=batch)
