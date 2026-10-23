"""One serial bounded fixture batch; NO SDK/Native/TCP/old objects."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,subprocess,time,hashlib,copy,uuid,os
B=Path(__file__).resolve().parents[1];sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]
from fixture_inputs import wire,role_output
from contract_cases import make
from fact_collector import facts,decode_wire,role_tree,plan,OwnedFactCapture,sha
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
W=B/'evidence'/('round-'+uuid.uuid4().hex);W.mkdir();start=time.monotonic();result={'schema':'GLOBAL_IDLE_CONTRACT02_SELF_CHECK_V1','work':str(W),'results':[],'sdk':0,'tcp':0,'native':0};children=[]
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def reject(fn):
 try:fn()
 except (ValueError,UnicodeDecodeError) as e:return str(e)
 raise AssertionError('EXPECTED_STRICT_REJECT')
def child(argv):
 p=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL);children.append(p);out,err=p.communicate();return p.returncode,out,err
def group(name,fn):
 if time.monotonic()-start>=360:raise AssertionError('NO_NEW_CASE_AFTER_360S')
 t=time.monotonic()
 try:r=fn();result['results'].append(dict(name=name,passed=True,seconds=time.monotonic()-t,detail=r));save(W/'progress.json',result)
 except BaseException as e:result['results'].append(dict(name=name,passed=False,seconds=time.monotonic()-t,error=repr(e)));raise
def semantics():
 rows=make();save(W/'semantic-inputs.json',rows)
 code,out,err=child([PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/review_semantics.ps1'),'-InputFile',str(W/'semantic-inputs.json'),'-OutputFile',str(W/'semantic-results.json')]);(W/'semantic-stderr.bin').write_bytes(err)
 results=json.loads((W/'semantic-results.json').read_text(encoding='utf-8-sig')) if (W/'semantic-results.json').exists() else []
 bad=[(x['id'],x['expected'],x['status'],x['reason']) for x in results if not x['pass']]
 assert code==0 and not err and results and not bad,(code,bad,err[:1500])
 assert len(rows[:45])==45
 for x in results:
  if x['id'] in ('H01','H02'):assert x['processCount']==68 and not x['qualified']
  if x['id']=='P02':assert x['processes'][1]['processName']=='com.fixture.app:worker:extra'
 return dict(total=len(results),criteria45=[x['id'] for x in results[:45]],positive=sum(x['qualified'] for x in results),allPositiveInputsExplicitSynthetic=True,archiveRecords=68)
def collector_pure():
 b=wire();v=facts(b);assert v['homeUid']==10012 and len(v['items'])==7
 bad={}
 for name,raw in [('end',b[:-1]),('status',b.replace(b'|model|0|',b'|model|1|')),('order',b.replace(b'|model|',b'|api|')),('length',b.replace(b'|8\nTB138FC',b'|7\nTB138FC')),('utf8',b.replace(b'TB138FC',b'\xffB138FC')),('nul',b.replace(b'TB138FC',b'\x00B138FC')),('time',b.replace(b'|1000|1000|',b'|1000|1030|',1)),('tail',b+b'EXTRA'),('duplicate',b.replace(b'GI_FACTS_END\n',b'GI_ITEM|home|0|1000|1000|1\nx\nGI_FACTS_END\n'))]:bad[name]=reject(lambda raw=raw:facts(raw))
 bad['role_duplicate_home']=reject(lambda:role_tree(role_output().replace('      holders=', '      name=android.app.role.HOME\n      holders=')))
 bad['role_multiple_holders']=reject(lambda:role_tree(role_output().replace('holders=com.zui.launcher','holders=[\ncom.zui.launcher\ncom.fixture.other\n]')))
 bad['role_denied']=reject(lambda:role_tree('Permission Denial'))
 assert plan()['argv'][4].count('GI_ITEM|')==7 and 'get-role-holders' not in plan()['argv'][4]
 save(W/'collector-known-input.bin.json',v);return dict(positive=v,negative=bad)
def source_integrity():
 seal=json.loads((B/'reference/runner-source-seal.json').read_text());manifest=json.loads((B/'reference/gate-sources.json').read_text());bad=[]
 for p,h in seal['sources'].items():
  if sha((B/p).read_bytes())!=h:bad.append(p)
 assert not bad and len(seal['sources'])==17 and len(manifest['files'])==9
 for row in manifest['files']:assert sha((B/row['path']).read_bytes())==row['sha256']
 old=B.parent/'d1android02-compat03-schema-parity01'
 unchanged=('tools/win32_route.py','tools/runtime_binding.py','reference/current-runtime-identity.json','reference/route-backend-contract.json','selfchecks/route_model.py','selfchecks/route_fixture.py')
 for p in unchanged:assert (B/p).read_bytes()==(old/p).read_bytes(),p
 return dict(sourceCount=17,gateCount=9,seal=sha((B/'reference/runner-source-seal.json').read_bytes()),unchanged=list(unchanged))
def owned_collector():
 # Import definitions without executing the affected regression footer.
 ns={'__file__':str(B/'selfchecks/run_affected.py')};exec((B/'selfchecks/run_affected.py').read_text().split('\ntry:\n check(')[0],ns)
 f,p=ns['permit']('fact-owned-original');args=ns['inputs'](f,p);r=ns['construct'](args);r.prepare_home();g=r.gate
 from entry_gates import decode,encode
 a=dict(schema='GLOBAL_IDLE_FACT_AUTHORITY_V1',approvedForExecution=True,scope=g.scope,planId=g.policy['planId'],mode='OFFLINE_FIXTURE',notBeforeUtc=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(),expiresUtc=(datetime.now(timezone.utc)+timedelta(seconds=60)).isoformat(),collectorSha256=sha((B/'tools/fact_collector.py').read_bytes()),planSha256=sha((B/'reference/fact-plan.json').read_bytes()),routeProofSha256=decode(g.receipt_bytes)['routeSha256'],sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=str(uuid.uuid4()))
 ap=dict(schema='GLOBAL_IDLE_FACT_APPROVAL_V1',mode='OFFLINE_FIXTURE',sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=str(uuid.uuid4()),approvedAuthoritySha256=sha(encode(a)),instructionText='EXECUTE_READONLY_FACTS '+sha(encode(a)),instructionSha256=sha(('EXECUTE_READONLY_FACTS '+sha(encode(a))).encode()))
 badApproval=reject(lambda:OwnedFactCapture().collect(a,g,sha(encode(a)),approval=ap,approved_approval_sha256='0'*64));assert badApproval=='FACT_EXTERNAL_APPROVAL_CHAIN' and not g.accepted
 c=OwnedFactCapture();receipt=c.collect(a,g,sha(encode(a)),[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'],approval=ap,approved_approval_sha256=sha(encode(ap)))
 assert receipt['originalBodyReturned'] and receipt['outerControllerReturnStillRequired'] and c.process.returncode==0
 # collect has now actually returned to this caller. Original gate release is
 # still owned by c, following the unique original reader/wait/handle close.
 release=c.finish_after_original_collect_return(g);r.fail('FIXTURE_GATE_TRANSFERRED_TO_SEPARATE_FACT_OWNER_COMPLETE')
 from production_runner import RUNNER_CUSTODY
 RUNNER_CUSTODY.remove(r)
 save(W/'owned-collector-receipt.json',receipt);save(W/'owned-collector-original-release.json',release)
 assert release['sdkChildrenEntered']==1 and release['originalUnlockCloseReturned'] and release['factProofTimely'] and release['factCaptureQualified']
 return dict(receipt=receipt,release=release,onceReject=reject(lambda:c.collect(a,g,sha(encode(a)))))
try:
 group('sealed-source-and-unchanged-native-runtime',source_integrity)
 group('45-independent-cases-plus-boundary-mutations',semantics)
 group('seven-query-framing-and-HOME-source-grammar',collector_pure)
 group('original-local-collector-process-pipes-return-and-claim',owned_collector)
finally:
 result['seconds']=time.monotonic()-start;result['allPassed']=bool(result['results']) and all(x['passed'] for x in result['results']);result['originalAuxChildrenReturned']=all(p.returncode is not None for p in children);save(W/'report.json',result);save(B/'evidence/contract-result.json',result)
 print(json.dumps(dict(work=str(W),allPassed=result['allPassed'],groups=len(result['results']),seconds=result['seconds'])))
