"""Independent explicit acceptance inputs. All positives are synthetic only."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,hashlib,json
def sha(b):return hashlib.sha256(b).hexdigest()
def record(name='com.zui.launcher',pkg='com.zui.launcher',uid=10012,state=2,pid=124,token='abcdef',kind='APP',spec=None):
 user=uid//100000;a=uid%100000
 spec=spec or (str(uid) if uid<10000 else 'u'+str(user)+('a'+str(a-10000) if a>=10000 else 's'+str(a)))
 return f'  *{kind}* UID {uid} ProcessRecord{{{token} {pid}:{name}/{spec}}}\n    user #{user} uid={uid}\n    packageList={{{pkg}}}\n    curProcState={state} cached=false\n    mInstr=null\n'
def text(extra='',home=None):
 return 'ANDROID02_GLOBAL_BEGIN\nACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)\n'+(home if home is not None else record())+extra+'ANDROID02_GLOBAL_ACTIVITIES\nACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)\nDisplay #0 (activities from top to bottom):\n  mResumedActivity: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n  mFocusedApp=ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n      * Hist #0: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n          packageName=com.zui.launcher processName=com.zui.launcher\n          app=ProcessRecord{abcdef 124:com.zui.launcher/u0a12}\n          mActivityComponent=com.zui.launcher/.Launcher\n          state=RESUMED stopped=false delayedResume=false finishing=false\n          mVisibleRequested=true mVisible=true\nANDROID02_GLOBAL_COMPLETE\n'
def cases(B):
 pins={p:sha((B/p).read_bytes()) for p in ('reference/runner-source-seal.json','reference/exact-seven-role-plan.json','tools/fact_collector.py','reference/fact-plan.json')};rows=[]
 def qual():
  lo=datetime.now(timezone.utc)-timedelta(seconds=1);hi=lo+timedelta(seconds=300)
  return dict(schema='GLOBAL_IDLE_QUALIFICATION_V1',mode='OFFLINE_FIXTURE',fixtureOnly=True,targetScope='a'*64,targetRunId='D1MA02-FIXTURE',targetSourceSealSha256=pins['reference/runner-source-seal.json'],targetPlanSha256=pins['reference/exact-seven-role-plan.json'],factScope='b'*64,factAuthoritySha256='1'*64,factApprovalSha256='2'*64,factCaptureReceiptSha256='3'*64,factOuterReturnSha256='4'*64,collectorSourceSha256=pins['tools/fact_collector.py'],factPlanSha256=pins['reference/fact-plan.json'],rawSha256='c'*64,rawBytes=1024,routeProofSha256='d'*64,sdkSha256='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f',collectedAtUtc=lo.isoformat(),expiresAtUtc=hi.isoformat(),originalReturn=dict(waitReturned=True,stdoutEOF=True,stderrEOF=True,originalPipesClosed=True,originalHandleClosed=True,controllerReturned=True,unknown=False,exitCode=0),grammar='API31_APP_PERS_V1',serial='HA1Q6WXR',model='TB138FC',api=31,fingerprint='INDEPENDENT_SYNTHETIC_FIXTURE_API31',user=0,home=dict(package='com.zui.launcher',component='com.zui.launcher.Launcher',process='com.zui.launcher',user=0,uid=10012,systemFlag=True),services=[],systemPackages=[dict(package='com.zui.launcher',uid=10012,systemFlag=True)],reviewEvidenceSha256='e'*64)
 def svc(q,pkg='com.fixture.system',name='com.fixture.system:worker',uid=10065,state=5,kind='PERS'):
  q['systemPackages'].append(dict(package=pkg,uid=uid,systemFlag=True));q['services'].append(dict(packages=[pkg],process=name,user=0,uid=uid,kind=kind,state=state,category='NONCONTENDING_SYSTEM_SERVICE',firmware=q['fingerprint'],evidenceSha256='f'*64,factScope=q['factScope'],validFromUtc=q['collectedAtUtc'],validToUtc=q['expiresAtUtc'],range='EXACT_SNAPSHOT'))
 def add(i,t=None,q='DEFAULT',status='BLOCKED_UNPROVEN',reason=None,edit=None,group='independent45'):
  t=text() if t is None else t;q=qual() if q=='DEFAULT' else q
  c=dict(scope='a'*64,runId='D1MA02-FIXTURE',mode='OFFLINE_FIXTURE',rawSha256=sha(t.encode()),rawBytes=len(t.encode()),captureBodyReturned=True,sourceSealSha256=pins['reference/runner-source-seal.json'],planSha256=pins['reference/exact-seven-role-plan.json'],reviewEvidenceSha256='e'*64,nowUtc=datetime.now(timezone.utc).isoformat())
  if edit:edit(c)
  rows.append(dict(id=i,group=group,text=t,qualification=q,context=c,expected=status,expectedReason=reason))
 cached=lambda **kw:record('com.fixture.app:worker','com.fixture.app',10065,16,125,'bad001',**kw)
 add('F01',status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 add('F02',text().replace('ANDROID02_GLOBAL_BEGIN\n',''),reason='GLOBAL_FORMAT_UNPROVEN')
 add('F03',text().replace('cached=false','cached=false ANDROID02_GLOBAL_COMPLETE'),reason='GLOBAL_FORMAT_UNPROVEN')
 add('F04',edit=lambda c:c.update(captureBodyReturned=False),reason='GLOBAL_CAPTURE_RETURN_UNPROVEN')
 add('F05',text().replace('cached=false','cached=false\x00'),reason='GLOBAL_INVALID_CONTROL_CHARACTER')
 add('F06',text(record('com.other','com.other',10065,2,125,'bad001','SYS')),reason='GLOBAL_PROCESS_HEADERS_UNPROVEN')
 q=qual();q['originalReturn']['controllerReturned']=False;add('F07',q=q,reason='GLOBAL_FACT_ORIGINAL_RETURN_UNPROVEN')
 add('P01',text(cached()),status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 add('P02',text(cached().replace(':worker/',':worker:second/')),status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 q=qual();svc(q);add('P03',text(record('com.fixture.system:worker','com.fixture.system',10065,5,125,'bad001','PERS')),q,status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 add('P04',text(cached(kind='SYS')),reason='GLOBAL_PROCESS_HEADERS_UNPROVEN')
 add('P05',text(cached().replace('user #0 uid=10065','user #0 uid=10066')),reason='GLOBAL_PROCESS_USER_UNPROVEN')
 add('P06',text(record('com.fixture.app','com.fixture.app',1010065,16,125,'bad001')),reason='GLOBAL_OTHER_USER_UNPROVEN')
 q=qual();svc(q,'android','system',1000,0);add('P07',text(record('system','android',1000,0,125,'bad001','PERS')),q,status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 add('P08',text(cached(spec='u0ai1')),reason='GLOBAL_ISOLATED_OWNER_UNPROVEN')
 add('P09',text(cached().replace('{com.fixture.app}','{com.fixture.app, com.zui.launcher}')),reason='GLOBAL_SHARED_OWNER_UNPROVEN')
 add('P10',text(cached()+'      curProcState=2\n      packageList={com.zui.launcher}\n'),status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 add('P11',text().replace('curProcState','setProcState'),reason='GLOBAL_PROCESS_STATE_UNPROVEN')
 add('P12',text().replace('    curProcState=2','    curProcState=3\n    curProcState=2'),reason='GLOBAL_PROCESS_STATE_UNPROVEN')
 add('P13',text().replace('curProcState=2','curProcState=2147483648'),reason='GLOBAL_PROCESS_STATE_UNPROVEN')
 add('P14',text(cached().replace('{com.fixture.app}','{com.zui.launcher}')),reason='GLOBAL_PROCESS_PACKAGE_MAPPING_UNPROVEN')
 add('S01',text(record('com.fixture.app','com.fixture.app',10065,2,125,'bad001')),status='BLOCKED_OCCUPIED',reason='ENV_WAIT_FOREIGN_FOREGROUND')
 add('S02',text().replace('mInstr=null','mInstr=ActiveInstrumentation{abc 1 procs}'),status='BLOCKED_OCCUPIED',reason='ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED')
 add('S03',text('Instrumentation #0: ActiveInstrumentation{abc}\n'),status='BLOCKED_OCCUPIED',reason='ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED')
 add('S04',text().replace('mInstr=null','mInstr=unknown'),reason='GLOBAL_INSTRUMENTATION_FORMAT_UNPROVEN')
 add('S05',text(record('com.fixture.app:fg','com.fixture.app',10065,4,125,'bad001')),status='BLOCKED_OCCUPIED',reason='ENV_WAIT_ACTIVE_SERVICE_UNQUALIFIED')
 add('S06',text(record('android','android',1000,0,125,'bad001','PERS')),reason='GLOBAL_CORE_SERVICE_UNPROVEN')
 add('S07',text(cached()),status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 q=qual();svc(q);add('S08',text(record('com.fixture.system:worker','com.fixture.system',10065,5,125,'bad001','PERS')),q,status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 add('S09',text(home=record(state=16)),reason='GLOBAL_HOME_PROCESS_STATE_UNPROVEN')
 add('S10',text(record('android','android',1000,0,125,'bad001','PERS')+'    dir=/system/priv-app/Friendly.apk\n'),reason='GLOBAL_CORE_SERVICE_UNPROVEN')
 add('R01',status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 add('R02',q=None,reason='GLOBAL_QUAL_SCHEMA')
 add('R03',text().replace('  mResumedActivity: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n',''),reason='GLOBAL_RESUME_OR_FOCUS_UNPROVEN')
 add('R04',text().replace('  mFocusedApp=','  topResumedActivity=ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n  mFocusedApp='),reason='ENV_WAIT_MULTIPLE_RESUMED_IDENTITIES_UNPROVEN')
 add('R05',text().replace('mFocusedApp=ActivityRecord{abc','mFocusedApp=ActivityRecord{def'),reason='GLOBAL_FOCUS_RESUME_DISAGREEMENT')
 add('R06',text().replace('  mFocusedApp=','  mResumedActivity: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n  mFocusedApp='),reason='ENV_WAIT_MULTIPLE_RESUMED_IDENTITIES_UNPROVEN')
 add('R07',text().replace('u0 com.zui.launcher/.Launcher','u0 com.fixture.app/.Main'),status='BLOCKED_OCCUPIED',reason='ENV_WAIT_FOREIGN_RESUMED')
 add('R08',text().replace('com.zui.launcher/.Launcher','com.zui.launcher/.Dialog'),reason='GLOBAL_HOME_COMPONENT_UNPROVEN')
 q=qual();q['home']['package']='com.zui.*';add('Q01',q=q,reason='GLOBAL_HOME_FACT_UNPROVEN')
 q=qual();q['targetScope']='c'*64;add('Q02',q=q,reason='GLOBAL_QUAL_SCOPE_OR_SOURCE')
 add('Q03',q=None,reason='GLOBAL_QUAL_SCHEMA')
 q=qual();q['targetSourceSealSha256']='0'*64;add('Q04',q=q,reason='GLOBAL_QUAL_SCOPE_OR_SOURCE')
 archived=(Path('D:/CodexProjects/VideoKit/docs/coder')/'d1android02-global-idle-semantics01/reference/original-global_idle-stdout.bin').read_bytes();assert len(archived)==388784 and sha(archived)=='6eab0a9190438367150182a530395585066826514242dbaf5dc70bb6f49596b0'
 add('H01',archived.decode(),None,reason='GLOBAL_QUAL_SCHEMA');add('H02',archived.decode(),None,reason='GLOBAL_QUAL_SCHEMA')
 assert len(rows)==45
 def extra(i,t=None,q='DEFAULT',status='BLOCKED_UNPROVEN',reason=None,edit=None):add(i,t,q,status,reason,edit,'independent-extra')
 # All missing qualifier keys and nested fields have a precise schema rejection.
 for k in qual():
  q=qual();q.pop(k);extra('DELETE_QUAL_'+k,q=q,reason='GLOBAL_QUAL_SCHEMA')
 for sub in ('originalReturn','home'):
  for k in qual()[sub]:
   q=qual();q[sub].pop(k);extra('DELETE_'+sub+'_'+k,q=q,reason='GLOBAL_QUAL_SCHEMA')
 for k in ('factAuthoritySha256','factApprovalSha256','factCaptureReceiptSha256','factOuterReturnSha256','rawSha256','routeProofSha256'):
  q=qual();q[k]='z'*64;extra('INVALID_HASH_'+k,q=q,reason='GLOBAL_QUAL_HASH')
 for k in ('collectorSourceSha256','factPlanSha256','sdkSha256'):
  q=qual();q[k]='0'*64;extra('WRONG_PRODUCER_'+k,q=q,reason='GLOBAL_FACT_PRODUCER_PIN')
 for k,v,why in [('api',30,'GLOBAL_FIRMWARE_UNPROVEN'),('serial','OTHER','GLOBAL_FIRMWARE_UNPROVEN'),('user',1,'GLOBAL_FIRMWARE_UNPROVEN'),('fixtureOnly',False,'GLOBAL_FIXTURE_MODE_BINDING'),('grammar','API_OTHER','GLOBAL_FIRMWARE_UNPROVEN'),('rawBytes',0,'GLOBAL_FIRMWARE_UNPROVEN')]:
  q=qual();q[k]=v;extra('BAD_QUAL_'+k,q=q,reason=why)
 for k in qual()['originalReturn']:
  q=qual();q['originalReturn'][k]= True if k=='unknown' else (1 if k=='exitCode' else False)
  extra('RETURN_'+k,q=q,reason='GLOBAL_FACT_UNKNOWN_OR_FAILED' if k in ('unknown','exitCode') else 'GLOBAL_FACT_ORIGINAL_RETURN_UNPROVEN')
 for k in ('scope','runId','sourceSealSha256','planSha256','reviewEvidenceSha256'):
  extra('CONTEXT_'+k,reason='GLOBAL_QUAL_SCOPE_OR_SOURCE',edit=lambda c,k=k:c.__setitem__(k,'0'*64))
 extra('CONTEXT_RAW_HASH',reason='GLOBAL_RAW_BINDING',edit=lambda c:c.update(rawSha256='0'*64));extra('CONTEXT_RAW_BYTES',reason='GLOBAL_RAW_BINDING',edit=lambda c:c.update(rawBytes=1))
 for label,elapsed,passed in [('fresh-299',299,True),('expired-300',300,False),('future-minus1',-1,False)]:
  q=qual();now=datetime.fromisoformat(q['collectedAtUtc'])+timedelta(seconds=elapsed)
  extra('TIME_'+label,q=q,status='PASS' if passed else 'BLOCKED_UNPROVEN',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY' if passed else 'GLOBAL_FACT_STALE_OR_FUTURE',edit=lambda c,now=now:c.update(nowUtc=now.isoformat()))
 q=qual();q['expiresAtUtc']=(datetime.fromisoformat(q['collectedAtUtc'])+timedelta(seconds=301)).isoformat();extra('TIME_WINDOW_301',q=q,reason='GLOBAL_FACT_STALE_OR_FUTURE')
 service_text=text(record('com.fixture.system:worker','com.fixture.system',10065,5,125,'bad001','PERS'))
 q=qual();q['systemPackages'].append(dict(package='com.fixture.system',uid=10065,systemFlag=True));extra('SYSTEM_LIST_NOT_PERMISSION',service_text,q,status='BLOCKED_OCCUPIED',reason='ENV_WAIT_ACTIVE_SERVICE_UNQUALIFIED')
 for k in ('packages','process','user','uid','kind','state','category','firmware','evidenceSha256','factScope','validFromUtc','validToUtc','range'):
  q=qual();svc(q);q['services'][0].pop(k);extra('DELETE_SERVICE_'+k,service_text,q,reason='GLOBAL_QUAL_SCHEMA')
 for k,v in [('firmware','OTHER'),('category','SYSTEM'),('factScope','c'*64),('validFromUtc','2000-01-01T00:00:00+00:00'),('validToUtc','2090-01-01T00:00:00+00:00'),('range','ALL'),('state',2),('user',1),('evidenceSha256','bad')]:
  q=qual();svc(q);q['services'][0][k]=v;extra('TAMPER_SERVICE_'+k,service_text,q,reason='GLOBAL_SERVICE_POLICY_UNPROVEN')
 for state in (0,1,4,5,6):
  q=qual();svc(q,state=state);extra('QUALIFIED_SERVICE_STATE_'+str(state),text(record('com.fixture.system:worker','com.fixture.system',10065,state,125,'bad001','PERS')),q,status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 for state in (2,3):extra('FOREIGN_TOP_'+str(state),text(record('com.fixture.app','com.fixture.app',10065,state,125,'bad001')),status='BLOCKED_OCCUPIED',reason='ENV_WAIT_FOREIGN_FOREGROUND')
 for state in (9,11,12):extra('CONTENDING_'+str(state),text(record('com.fixture.app','com.fixture.app',10065,state,125,'bad001')),status='BLOCKED_OCCUPIED',reason='ENV_WAIT_CONTENDING_OPERATION')
 for v in ('-1','20','1.5','text','999999999999999999999'):
  extra('STATE_'+v,text().replace('curProcState=2','curProcState='+v),reason='GLOBAL_OWN_FIELD_FORMAT_UNPROVEN' if v in ('-1','text') else 'GLOBAL_PROCESS_STATE_UNPROVEN')
 # Six-space UID summary after LAST PERS is not that record's current state.
 q=qual();svc(q);extra('LAST_PERS_UID_SUMMARY',service_text.replace('ANDROID02_GLOBAL_ACTIVITIES','  UID states:\n      curProcState=0\n      packageList={evil}\nANDROID02_GLOBAL_ACTIVITIES'),q,status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 extra('FULL_MULTICOLON',text(cached().replace(':worker/',':worker:second:third/')),status='PASS',reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY')
 extra('MULTIUSER_CORE',text(record('android','android',101000,0,125,'bad001','PERS')),reason='GLOBAL_OTHER_USER_UNPROVEN')
 extra('DUPLICATE_PID',text(record('com.fixture.app','com.fixture.app',10065,16,124,'bad001')),reason='GLOBAL_DUPLICATE_PROCESS_IDENTITY_UNPROVEN')
 extra('DUPLICATE_TOKEN',text(record('com.fixture.app','com.fixture.app',10065,16,125,'abcdef')),reason='GLOBAL_DUPLICATE_PROCESS_IDENTITY_UNPROVEN')
 for label,old,new in [('pid','app=ProcessRecord{abcdef 124:','app=ProcessRecord{abcdef 999:'),('token','app=ProcessRecord{abcdef','app=ProcessRecord{other'),('finishing','finishing=false','finishing=true'),('visible','mVisibleRequested=true','mVisibleRequested=false')]:extra('HOME_'+label,text().replace(old,new),reason='GLOBAL_HOME_ACTIVITY_PROCESS_BINDING' if label in ('pid','token') else 'GLOBAL_HOME_ACTIVITY_OWNER_UNPROVEN')
 # Mixed recognized and unsupported top-level records must never be skipped.
 for label,head in [('uid-spacing','*APP* UID10065'),('uid-case','*APP* uid 10065'),('star-spacing','*APP*UID 10065')]:
  prefix='  '+head+' ProcessRecord{bad001 125:com.fixture.app/u0a65}\n    user #0 uid=10065\n    packageList={com.fixture.app}\n    curProcState=2 cached=false\n    mInstr=null\n'
  extra('UNPARSED_PREFIX_'+label,text(home=prefix+record()),reason='GLOBAL_PROCESS_HEADERS_UNPROVEN')
 extra('FLOAT_CACHED_STATE',text(cached().replace('curProcState=16','curProcState=16.5')),reason='GLOBAL_PROCESS_STATE_UNPROVEN')
 return rows
