"""One independent OFFLINE batch; all source/profile/input pins frozen first."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,os,json,time,copy,uuid,threading,subprocess,hashlib,traceback
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));B=Path('D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-readonly-facts-preauth01')
from self_io import save as rawsave,read,sha,known,READS
from controller import order
from native_identity import own_identity
from driver_guard import Registry,PY,PS,ORIGINAL
from self_observer import Observer,CUSTODY as AUX
from write_guard import allowed,install,EVENTS as WRITES
from host_context import snapshot
def main(h):
 o=order(h);W=R/'work';ident=own_identity();ident['nonce']=o['nonce'];ident['hostContext']=snapshot();rawsave(R/'worker-self.json',ident);start=time.monotonic()
 while not (R/'worker-admit.json').exists():
  if time.monotonic()-start>8:return 2
  time.sleep(.025)
 assert json.loads(read(R/'worker-admit.json'))==dict(orderSha256=h,selfSha256=sha(read(R/'worker-self.json')))
 start=json.loads(read(R.parent/'batch-start.json'))['monotonic']
 sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]
 import fact_preauth as fp,entry_gates as eg,fact_collector as fc,win32_route as wr
 from independent_models import matrix
 reg=Registry(json.loads(read(R/'reference/profile.json')),start);captures=[];tickets=[];gates=[];factCaptures=[];groups=[];stopReasons=[]
 def save(p,d):allowed(p);return rawsave(p,d)
 def stop(reason):
  stopReasons.append(reason);reg.stop=True
  if not (R/'stop.json').exists():save(R/'stop.json',dict(reason=reason,stopNew=True,noKillOrSecondClose=True))
 def child(argv,qual=False):
  root=W/('collect-'+str(len(captures)));allowed(root);root.mkdir()
  env=reg.p['qualificationEnv'] if qual else None;cwd=reg.p['qualificationCwd'] if qual else None
  k=dict(executable=argv[0],cwd=cwd,env=env,shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);reg.check(argv,k)
  c=Observer(argv,argv[0],cwd,env,root,stop,window=5 if qual else 90);captures.append(c);receipt=c.collect();save(root/'observed.json',receipt)
  if receipt['errors'] or receipt['expired'] or not receipt['streamsAndOriginalHandleCloseReturned']:stop('AUXILIARY_RETURN_NOT_QUALIFIED')
  return receipt['exitCode'],bytes(c.buffers[0]),bytes(c.buffers[1])
 ns=dict(Path=Path,datetime=datetime,timezone=timezone,timedelta=timedelta,sys=sys,os=os,json=json,time=time,copy=copy,uuid=uuid,threading=threading,subprocess=subprocess,hashlib=hashlib,H=R,B=B,W=W,PY=PY,PS=PS,PreparedFacts=fp.PreparedFacts,validate=fp.validate,load_pins=fp.load_pins,encode=fp.encode,decode=fp.decode,LIMITS=fp.LIMITS,binding_bytes=fp.binding_bytes,GateSession=eg.GateSession,OwnedFactCapture=fc.OwnedFactCapture,validate_fixture_argv=fc.validate_fixture_argv,ENV=fc.ENV,sha=fp.sha,child=child,save=save)
 exec(compile(read(R/'reused_checks.py').decode(),'<selected-inert-checks-no-main>','exec'),ns)
 def inputs(name):return ns['inputs'](name)
 def reject(fn,reason):return ns['reject'](fn,reason)
 def qualify():
  rows=[]
  for argv,code in [([PY,'-I','-X','utf8','-B',str(R/'driver/reuse/owned_child.py'),'ok'],0),([PY,'-I','-X','utf8','-B',str(R/'driver/reuse/owned_child.py'),'fail'],7),([PS,'-NoProfile','-NonInteractive','-File',str(R/'driver/reuse/owned_child.ps1')],0)]:
   c,b,e=child(argv,True);assert c==code and not e and not captures[-1].expired;rows.append(dict(exitCode=c,allOriginalsReturned=True,knownNonzero=c==7))
  return rows
 def independent():
  p,t,pins=inputs('pure');d=matrix(fp,p,t,pins);save(W/'independent-template-matrix.json',d);assert not d['bad'],d['bad'][:3];return dict(total=d['total'],bad=0)
 def semantic():
  shards=json.loads(read(R/'reference/semantic-shards.json'));allRows=[]
  for s in shards:
   assert sha(read(s['input']))==s['sha256'];code,b,e=child(s['argv']);d=json.loads(Path(s['output']).read_text(encoding='utf-8-sig'));bad=[x for x in d if not x['pass']];assert code==0 and not e and len(d)==s['rows'] and not bad,(code,bad[:3],e[:1000]);allRows.extend(d)
  assert len(allRows)==346;save(W/'semantics-results-combined.json',allRows);return dict(total=346,bad=0,shards=len(shards),original45Included=True,original175Included=True,independentPositive17Included=True,sourceSet='CURRENT_20_NOT_INHERITED_A',positive=sum(x['qualified'] for x in allRows))
 def finish(g,c):
  if g is None:return dict(claimNeverCreated=True)
  if getattr(c,'unknown',False):stop('FACT_ORIGINAL_UNKNOWN');return None
  if getattr(c,'bodyReturned',False):return c.finish_after_original_collect_return(g)
  if g.released:return dict(alreadyReleased=True)
  if not c.entered and g.lease is not None and not g.lease.closed:return g.release()
  stop('NO_KNOWN_ORIGINAL_RELEASE_PATH');return None
 def new_original():
  p,t,pins=inputs('new-original');raw=fp.encode(t);ticket=fp.PreparedFacts(raw,fp.sha(raw),p);tickets.append(ticket);c=fc.OwnedFactCapture();factCaptures.append(c);g=None;neg=[];rec=None;binding=None
  neg.append(reject(lambda:ticket.current(None),'PREAUTH_ORIGINAL_PREPARED_GATE'))
  try:
   g=ticket.prepare();gates.append(g)
   neg.append(reject(ticket.prepare,'PREAUTH_PREPARE_ONCE'))
   other=eg.GateSession.__new__(eg.GateSession);neg.append(reject(lambda:ticket.current(other),'PREAUTH_ORIGINAL_PREPARED_GATE'))
   ownerErrors=[]
   def wrong_thread():
    try:ticket.current(g)
    except ValueError as e:ownerErrors.append(str(e))
   th=threading.Thread(target=wrong_thread);th.start();th.join();assert ownerErrors==['PREAUTH_ORIGINAL_OWNER'];neg.extend(ownerErrors)
   binding=ticket.bind(g);bound=fp.decode(binding)
   neg.append(reject(lambda:ticket.bind(g),'PREAUTH_BIND_ONCE'))
   for k in bound:
    for op in ['delete','null']:
     bad=copy.deepcopy(bound)
     if op=='delete':bad.pop(k)
     else:bad[k]=None
     neg.append(dict(field=k,operation=op,inputSha256=fp.sha(fp.encode(bad)),reason=reject(lambda bad=bad:ticket.receive(g,fp.encode(bad),fc.OwnedFactCapture()),'PREAUTH_BINDING_ONCE_BYTES'),phase='ORIGINAL_GATE_BEFORE_RECEIVE_ENTERED'))
   assert not getattr(ticket,'receiveEntered',False)
   rec=ticket.receive(g,binding,c,[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'])
  finally:release=finish(g or ticket.gate,c)
  assert rec['schema']=='GLOBAL_IDLE_FACT_CAPTURE_V2' and rec['authorizationKind']=='GLOBAL_IDLE_FACT_PREAUTH_V1' and 'authoritySha256' not in rec and 'approvalSha256' not in rec
  assert rec['externalPreauthSha256']==fp.sha(raw) and rec['runtimeBindingSha256']==fp.sha(binding) and release['originalUnlockCloseReturned'] and release['factCaptureQualified'] and release['factProofTimely'] and release['sdkChildrenEntered']==1
  neg.append(reject(lambda:ticket.receive(g,binding,fc.OwnedFactCapture()),'PREAUTH_ORIGINAL_PREPARED_GATE'));neg.append(reject(g.release,'RELEASE_ONCE'))
  actual=fp.decode(binding);assert actual['ownerPid']==g.pid and actual['ownerThread']==g.thread and actual['claimFileId']==g.file_id and actual['generation']==g.generation and actual['scopeStartTick']==g.start_tick and actual['proofStartTick']==g.proof_start_tick and actual['initialProofSha256']==g.proof_hash
  d=dict(receipt=rec,release=release,binding=actual,negative=neg,proofReturnSeconds=time.monotonic()-c.bodyReturnTick,sourceBytes=g.source_bytes,sourceReads=g.source_reads,controlBytes=sum(x['bytes'] for x in g.events)+g.carry,events=g.events,allFactThreadsJoined=all(not x.is_alive() for x in c.held if isinstance(x,threading.Thread)),originalFactHandleClosed=c.handleClosed)
  save(W/'new-original-result.json',d)
  rawWire=bytes(c.buf[0]);wire=[]
  for name,bad,expected in [('bad-header',b'X'+rawWire[1:],'FACT_BEGIN'),('truncated-end',rawWire[:-1],'FACT_END_OR_DURATION'),('wrong-query',rawWire.replace(b'GI_ITEM|model|',b'GI_ITEM|extra|',1),'FACT_ORDER_OR_FRAME'),('extra-tail',rawWire+b'X','FACT_END_OR_DURATION')]:
   try:fc.facts(bad);reason='UNEXPECTED_ACCEPT'
   except (ValueError,TypeError,KeyError) as e:reason=str(e)
   assert reason==expected,(name,reason,expected);wire.append(dict(case=name,reason=reason,expectedReason=expected,phase='CURRENT_DECODE_WIRE',pureCurrentCollector=True))
  save(W/'wire-negative.json',wire);return d
 def wrong_capture():
  p,t,pins=inputs('wrong-receiver');ticket=fp.PreparedFacts(fp.encode(t),fp.sha(fp.encode(t)),p);tickets.append(ticket);g=None;c=fc.OwnedFactCapture();factCaptures.append(c)
  try:
   g=ticket.prepare();gates.append(g);binding=ticket.bind(g);reason=reject(lambda:ticket.receive(g,binding,object()),'PREAUTH_ORIGINAL_CAPTURE');assert ticket.receiveEntered and not c.entered
   reason2=reject(lambda:ticket.receive(g,binding,c),'PREAUTH_BINDING_ONCE_BYTES')
  finally:release=finish(g or ticket.gate,c)
  assert release['originalUnlockCloseReturned'] and release['sdkChildrenEntered']==0
  d=dict(reason=reason,reentryReason=reason2,release=release,sourceBytes=g.source_bytes,sourceReads=g.source_reads,controlBytes=sum(x['bytes'] for x in g.events)+g.carry,events=g.events);save(W/'wrong-receiver-result.json',d);return d
 def legacy():
  p,t,pins=inputs('legacy-original');root=Path(p['evidenceRoot']);allowed(root);root.mkdir(parents=True);g=eg.GateSession(root.parent,policy=p);gates.append(g);c=fc.OwnedFactCapture();factCaptures.append(c);rec=None
  try:
   g.prepare();now=datetime.now(timezone.utc);a=dict(schema='GLOBAL_IDLE_FACT_AUTHORITY_V1',approvedForExecution=True,scope=g.scope,planId=p['planId'],mode='OFFLINE_FIXTURE',notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=80)).isoformat(),collectorSha256=pins['collectorSha256'],planSha256=pins['factPlanSha256'],routeProofSha256=eg.decode(g.receipt_bytes)['routeSha256'],sourceThreadId=t['sourceThreadId'],sourceTurnId=str(uuid.uuid4()));ah=fp.sha(fp.encode(a));instruction='EXECUTE_READONLY_FACTS '+ah
   approval=dict(schema='GLOBAL_IDLE_FACT_APPROVAL_V1',mode='OFFLINE_FIXTURE',sourceThreadId=t['sourceThreadId'],sourceTurnId=str(uuid.uuid4()),approvedAuthoritySha256=ah,instructionText=instruction,instructionSha256=fp.sha(instruction.encode()));ph=fp.sha(fp.encode(approval))
   neg=[reject(lambda:fc.OwnedFactCapture().collect(a,g,'0'*64,approval=approval,approved_approval_sha256=ph),'FACT_PRIOR_APPROVAL_HASH'),reject(lambda:fc.OwnedFactCapture().collect(a,g,ah,approval=approval,approved_approval_sha256='0'*64),'FACT_EXTERNAL_APPROVAL_CHAIN')]
   rec=c.collect(a,g,ah,[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'],approval=approval,approved_approval_sha256=ph)
  finally:release=finish(g,c)
  assert rec['schema']=='GLOBAL_IDLE_FACT_CAPTURE_V1' and rec['authoritySha256']==ah and rec['approvalSha256']==ph and 'externalPreauthSha256' not in rec and release['factCaptureQualified'];neg.append(reject(lambda:c.collect(a,g,ah),'FACT_ONCE'))
  d=dict(receipt=rec,release=release,negative=neg,sourceBytes=g.source_bytes,sourceReads=g.source_reads,controlBytes=sum(x['bytes'] for x in g.events)+g.carry);save(W/'legacy-result.json',d);return d
 def cli():
  rows=[];calls=json.loads(read(R/'reference/cli-calls.json'))
  for row in calls:
   c,b,e=child(row['argv']);assert c==row['exitCode'],(row['name'],c,b,e)
   if row['name']=='complete':
    d=fp.decode(b);assert not e and d['receipt']['schema']=='GLOBAL_IDLE_FACT_CAPTURE_V2' and d['release']['factCaptureQualified'] and d['qualificationIssued'] is False and d['outerProcessReturnStillRequired'] and len(d['fixtureConstructorCalls'])==2 and all(x['matches'] for x in d['fixtureAudit']);save(W/'explicit-cli-observed-return.json',dict(originalWaitReadersStreamsHandleReturned=True,result=d))
   elif row['reason']:
    d=json.loads(b);assert d['reason']==row['reason'],(row['name'],d)
   else:assert b'usage:' in e and not b
   rows.append(dict(name=row['name'],exitCode=c,expectedReason=row['reason'],allOriginalsReturned=True,rawCounts=captures[-1].counts))
  save(W/'cli-results.json',rows);return rows
 def intact():
  return known() and not AUX and not eg.CUSTODY and not fc.CUSTODY and not wr.CUSTODY and all(c.returned for c in captures) and all(g.released and g.lease.closed and all(not t.is_alive() for t in g.pending) for g in gates) and all(not c.unknown for c in factCaptures)
 install(reg);sys.addaudithook(reg.observe);subprocess.Popen=reg.construct
 for x in reg.p['allPlannedCalls']:reg.check(x['argv'],x['kwargs'])
 for label,fn in [('driver-qualification',qualify),('developer-template-replay',ns['pure_templates']),('independent-two-layer-template',independent),('current-source-346-semantics',semantic),('original-preStart13',ns['prestart']),('actual-original-V2-binding',new_original),('actual-wrong-receiver-once',wrong_capture),('legacy-V1',legacy),('explicit-CLI-and-replay',cli)]:
  if reg.stop or stopReasons or time.monotonic()-start>=240:groups.append(dict(name=label,status='NOT_RUN'));continue
  before=time.monotonic()
  try:d=fn();groups.append(dict(name=label,status='PASS',seconds=time.monotonic()-before,detail=d))
  except BaseException as e:groups.append(dict(name=label,status='FAIL',seconds=time.monotonic()-before,error=repr(e),traceback=traceback.format_exc()))
  save(R/('group-'+str(len(groups))+'.json'),groups[-1])
  if not intact():stop('ORIGINAL_RESOURCES_NOT_KNOWN_RETURNED')
  if label=='driver-qualification' and groups[-1]['status']!='PASS':stop('QUALIFICATION_FAILED')
 subprocess.Popen=ORIGINAL
 final=dict(schema='PREAUTH01_INDEPENDENT_B_RESULT_V1',batch=o['batch'],groups=groups,allPassed=all(x['status']=='PASS' for x in groups),allOwnStartedOriginalsReturned=intact(),newUnknown=not intact(),seconds=time.monotonic()-start,registryCalls=reg.calls,audit=reg.events,writeOperations=WRITES,stopReasons=stopReasons,auxOriginalReceipts=[dict(identity=c.identity,returned=c.returned,counts=c.counts,expired=c.expired) for c in captures],gateSummaries=[dict(scope=g.scope,generation=g.generation,released=g.released,sourceBytes=g.source_bytes,sourceReads=g.source_reads,leaseClosed=g.lease.closed,pending=sum(t.is_alive() for t in g.pending)) for g in gates],custody=dict(aux=len(AUX),gate=len(eg.CUSTODY),facts=len(fc.CUSTODY),route=len(wr.CUSTODY)),actualParentPopen=len(reg.calls),actualNestedCLI=2 if any(x['name']=='explicit-CLI-and-replay' and x['status']=='PASS' for x in groups) else 'SEE_CLI_RECEIPT',dotNetChildPreplanned=1,outerWorker=1,actualSDK=0,actualNativeRoute=0,actualTCP=0,actualDevice=0,actualGit=0,qualificationV2='NOT_IMPLEMENTED_NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 save(R/'worker-final.json',final);print(json.dumps(dict(allPassed=final['allPassed'],groups=len(groups),newUnknown=final['newUnknown'],seconds=final['seconds'])))
 if final['newUnknown']:
  while True:time.sleep(.1)
 return 0 if final['allPassed'] else 2
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
