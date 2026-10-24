"""Full independent 45-case mapping plus strict mutations and real conditional positives."""
from pathlib import Path
import copy,json,sys,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fixture_inputs import qualification,record,text,context,service
B=Path(__file__).resolve().parents[1]
def make():
 rows=[]
 def add(i,t=None,q='DEFAULT',expected='BLOCKED_UNPROVEN',edit=None):
  t=text() if t is None else t;q=qualification() if q=='DEFAULT' else q;c=context(t,q)
  if edit:edit(c)
  rows.append(dict(id=i,text=t,qualification=q,context=c,expected=expected))
 add('F01',expected='PASS')
 add('F02',text().replace('ANDROID02_GLOBAL_BEGIN\n',''))
 add('F03',text().replace('cached=false','cached=false ANDROID02_GLOBAL_COMPLETE'))
 add('F04',edit=lambda c:c.update(captureBodyReturned=False))
 add('F05',text().replace('cached=false','cached=false\x00'))
 add('F06',text(home='  *UNKNOWN* UID 1 ProcessRecord{a 1:x/1}\n'))
 q=qualification();q['originalReturn']['controllerReturned']=False;add('F07',q=q)
 foreign=lambda name='com.fixture.app:worker',pkg='com.fixture.app',**kw:record(name,pkg,10065,16,125,'abcde1',**kw)
 add('P01',text(foreign()),expected='PASS')
 add('P02',text(foreign(name='com.fixture.app:worker:extra')),expected='PASS')
 q=qualification();service(q);add('P03',text(record('com.fixture.system:worker','com.fixture.system',10065,5,125,'abcde1','PERS')),q,expected='PASS')
 add('P04',text(foreign(kind='SYS')))
 add('P05',text(foreign().replace('user #0 uid=10065','user #0 uid=10066')))
 add('P06',text(record('com.fixture.app','com.fixture.app',1010065,2,125,'abcde1')))
 q=qualification();service(q,pkg='android',name='system',uid=1000,state=0);add('P07',text(record('system','android',1000,0,125,'abcde1','PERS')),q,expected='PASS')
 add('P08',text(foreign(spec='u0ai1')))
 add('P09',text(foreign(pkg='com.fixture.app, com.zui.launcher')))
 add('P10',text(foreign()+'      curProcState=2\n      packageList={com.zui.launcher}\n'),expected='PASS')
 add('P11',text().replace('curProcState','setProcState'))
 add('P12',text().replace('    curProcState=2','    curProcState=3\n    curProcState=2'))
 add('P13',text().replace('curProcState=2','curProcState=2147483648'))
 add('P14',text(foreign(pkg='com.zui.launcher')))
 add('S01',text(record('com.fixture.app','com.fixture.app',10065,2,125,'abcde1')),expected='BLOCKED_OCCUPIED')
 add('S02',text().replace('mInstr=null','mInstr=ActiveInstrumentation{abc 1 procs}'),expected='BLOCKED_OCCUPIED')
 add('S03',text(extra='Instrumentation #0: ActiveInstrumentation{abc}\n'),expected='BLOCKED_OCCUPIED')
 add('S04',text().replace('mInstr=null','mInstr=unknown'))
 add('S05',text(record('com.fixture.app:service','com.fixture.app',10065,4,125,'abcde1')),expected='BLOCKED_OCCUPIED')
 add('S06',text(record('android','android',1000,0,125,'abcde1','PERS')))
 add('S07',text(foreign()),expected='PASS')
 q=qualification();service(q);add('S08',text(record('com.fixture.system:worker','com.fixture.system',10065,5,125,'abcde1','PERS')),q,expected='PASS')
 add('S09',text(home=record(state=16)))
 add('S10',text(record('android','android',1000,0,125,'abcde1','PERS')+'    dir=/system/priv-app/LooksSafe.apk\n'))
 add('R01',expected='PASS')
 add('R02',q=None)
 add('R03',text().replace('  mResumedActivity: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n',''))
 add('R04',text().replace('  mFocusedApp=', '  topResumedActivity=ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n  mFocusedApp='))
 add('R05',text().replace('mFocusedApp=ActivityRecord{abc','mFocusedApp=ActivityRecord{def'))
 add('R06',text().replace('  mFocusedApp=', '  mResumedActivity: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n  mFocusedApp='))
 add('R07',text().replace('u0 com.zui.launcher/.Launcher','u0 com.fixture.app/.Main'),expected='BLOCKED_OCCUPIED')
 add('R08',text().replace('com.zui.launcher/.Launcher','com.zui.launcher/.Dialog'))
 q=qualification();q['home']['package']='com.zui.*';add('Q01',q=q)
 q=qualification();q['targetScope']='c'*64;add('Q02',q=q,edit=lambda c:c.update(scope='a'*64))
 add('Q03',q=None)
 q=qualification();q['targetSourceSealSha256']='0'*64;add('Q04',q=q,edit=lambda c:c.update(sourceSealSha256='a'*64))
 archived=(Path('D:/CodexProjects/VideoKit/docs/coder')/'d1android02-global-idle-semantics01/reference/original-global_idle-stdout.bin').read_bytes()
 assert len(archived)==388784 and hashlib.sha256(archived).hexdigest()=='6eab0a9190438367150182a530395585066826514242dbaf5dc70bb6f49596b0'
 add('H01',archived.decode('utf-8'),None);add('H02',archived.decode('utf-8'),None)
 # Each extension verifies a distinct boundary, no generic EXPECT_ANY_REJECT.
 for value in ('-1','1.5','x','20','999999999999999999999','2\n    curProcState=-1'):
  add('X_STATE_'+value.replace('\n','_'),text().replace('curProcState=2','curProcState='+value))
 for name in ('waitReturned','stdoutEOF','stderrEOF','originalPipesClosed','originalHandleClosed'):
  q=qualification();q['originalReturn'][name]=False;add('X_RETURN_'+name,q=q)
 q=qualification();q['originalReturn']['unknown']=True;add('X_RETURN_UNKNOWN',q=q)
 for k,v in [('api',30),('grammar','UNKNOWN'),('collectorSourceSha256','0'*64),('factPlanSha256','0'*64),('sdkSha256','0'*64),('expiresAtUtc','2000-01-01T00:00:00+00:00'),('fixtureOnly',False)]:
  q=qualification();q[k]=v;add('X_FACT_'+k,q=q)
 add('X_RAW_SIZE',edit=lambda c:c.update(rawBytes=1));add('X_RAW_HASH',edit=lambda c:c.update(rawSha256='0'*64))
 add('X_OTHER_DISPLAY',text().replace('Display #0','Display #1'))
 add('X_EXTRA_DISPLAY',text().replace('ANDROID02_GLOBAL_COMPLETE','Display #1 (activities from top to bottom):\nANDROID02_GLOBAL_COMPLETE'))
 add('X_FOCUS_DISPLAY',text().replace('ANDROID02_GLOBAL_COMPLETE','  displayId=1\nANDROID02_GLOBAL_COMPLETE'))
 add('X_UID_SUMMARY',text(foreign()+'  Process OOM control (2 total):\n      curProcState=0\n  UID states:\n      curProcState=3\n'),expected='PASS')
 add('X_PID_DUP',text(record('com.fixture.app','com.fixture.app',10065,16,124,'abcde1')))
 add('X_TOKEN_DUP',text(record('com.fixture.app','com.fixture.app',10065,16,125,'abcdef')))
 add('X_CORE_OTHER_USER',text(record('android','android',101000,0,125,'abcde1','PERS')))
 add('X_UNICODE',text().replace('com.zui.launcher','com.zui.ｌauncher'))
 add('X_CASE',text().replace('com.zui.launcher','com.Zui.launcher'),expected='BLOCKED_OCCUPIED')
 add('X_NULL_SUFFIX',text().replace('mInstr=null','mInstr=nullSuffix'))
 add('X_MALFORMED_INSTR',text(extra='Instrumentation #x: unknown\n'))
 for field,value in [('process','com.fixture.system:other'),('uid',10066),('kind','APP'),('state',4),('firmware','OTHER_FW'),('evidenceSha256','bad'),('range','ALL_FIRMWARE')]:
  q=qualification();service(q);q['services'][0][field]=value
  add('X_SERVICE_'+field,text(record('com.fixture.system:worker','com.fixture.system',10065,5,125,'abcde1','PERS')),q,expected='BLOCKED_OCCUPIED' if field in ('process','kind','state') else 'BLOCKED_UNPROVEN')
 q=qualification();q['mode']='LIVE';q['fixtureOnly']=False;add('X_FIXTURE_TO_LIVE',q=q)
 for label,old,new in [('token','app=ProcessRecord{abcdef','app=ProcessRecord{bad'),('pid','app=ProcessRecord{abcdef 124:','app=ProcessRecord{abcdef 999:'),('owner','processName=com.zui.launcher','processName=com.zui.launcher:other'),('state','state=RESUMED','state=PAUSED'),('visible','mVisibleRequested=true','mVisibleRequested=false')]:
  add('X_HIST_'+label,text().replace(old,new))
 for field in ('factAuthoritySha256','factApprovalSha256','factCaptureReceiptSha256','factOuterReturnSha256'):
  q=qualification();q.pop(field);add('X_MISSING_'+field,q=q)
 q=qualification();q['rawBytes']=139265;add('X_FACT_STDOUT_BOUND',q=q)
 q=qualification();q['collectedAtUtc']=q['collectedAtUtc'].replace('+00:00','');add('X_FACT_NAIVE_START',q=q)
 q=qualification();q['expiresAtUtc']=q['expiresAtUtc'].replace('+00:00','');add('X_FACT_NAIVE_END',q=q)
 q=qualification();q['systemPackages'].append(dict(package='com.zui.launcher',uid=10013,systemFlag=True));add('X_FACT_DUP_SYSTEM_PACKAGE',q=q)
 return rows
