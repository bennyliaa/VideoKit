"""SYNTHETIC OFFLINE_FIXTURE qualification. Never current device evidence."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
B=Path('D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix')
def sha(b):return hashlib.sha256(b).hexdigest()
def qualification(scope='a'*64,run='D1MA02-FIXTURE',now=None):
 now=now or datetime.now(timezone.utc);lo=(now-timedelta(seconds=1)).isoformat();hi=(now+timedelta(seconds=299)).isoformat()
 seal=sha((B/'reference/runner-source-seal.json').read_bytes());plan=sha((B/'reference/exact-seven-role-plan.json').read_bytes())
 return dict(schema='GLOBAL_IDLE_QUALIFICATION_V1',mode='OFFLINE_FIXTURE',fixtureOnly=True,targetScope=scope,targetRunId=run,targetSourceSealSha256=seal,targetPlanSha256=plan,factScope='b'*64,factAuthoritySha256='1'*64,factApprovalSha256='2'*64,factCaptureReceiptSha256='3'*64,factOuterReturnSha256='4'*64,collectorSourceSha256=sha((B/'tools/fact_collector.py').read_bytes()),factPlanSha256=sha((B/'reference/fact-plan.json').read_bytes()),rawSha256='c'*64,rawBytes=1024,routeProofSha256='d'*64,sdkSha256='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f',collectedAtUtc=lo,expiresAtUtc=hi,originalReturn=dict(waitReturned=True,stdoutEOF=True,stderrEOF=True,originalPipesClosed=True,originalHandleClosed=True,controllerReturned=True,unknown=False,exitCode=0),grammar='API31_APP_PERS_V1',serial='HA1Q6WXR',model='TB138FC',api=31,fingerprint='SYNTHETIC_FIXTURE_FIRMWARE_API31',user=0,home=dict(package='com.zui.launcher',component='com.zui.launcher.Launcher',process='com.zui.launcher',user=0,uid=10012,systemFlag=True),services=[],systemPackages=[dict(package='com.zui.launcher',uid=10012,systemFlag=True)],reviewEvidenceSha256='e'*64)
def record(name='com.zui.launcher',pkg='com.zui.launcher',uid=10012,state=2,pid=124,token='abcdef',kind='APP',user=None,spec=None):
 u=uid//100000 if user is None else user;a=uid%100000;spec=spec or (str(uid) if uid<10000 else 'u'+str(u)+('a'+str(a-10000) if a>=10000 else 's'+str(a)))
 return f'  *{kind}* UID {uid} ProcessRecord{{{token} {pid}:{name}/{spec}}}\n    user #{u} uid={uid}\n    packageList={{{pkg}}}\n    curProcState={state} cached=false\n    mInstr=null\n'
def home_detail():return '      * Hist #0: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n          packageName=com.zui.launcher processName=com.zui.launcher\n          app=ProcessRecord{abcdef 124:com.zui.launcher/u0a12}\n          mActivityComponent=com.zui.launcher/.Launcher\n          state=RESUMED stopped=false delayedResume=false finishing=false\n          mVisibleRequested=true mVisible=true\n'
def text(extra='',home=None):return 'ANDROID02_GLOBAL_BEGIN\nACTIVITY MANAGER RUNNING PROCESSES (dumpsys activity processes)\n'+(home or record())+extra+'ANDROID02_GLOBAL_ACTIVITIES\nACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)\nDisplay #0 (activities from top to bottom):\n  mResumedActivity: ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n  mFocusedApp=ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\n'+home_detail()+'ANDROID02_GLOBAL_COMPLETE\n'
def service(q,pkg='com.fixture.system',name='com.fixture.system:worker',uid=10065,state=5,kind='PERS'):
 q['systemPackages'].append(dict(package=pkg,uid=uid,systemFlag=True));q['services'].append(dict(packages=[pkg],process=name,user=0,uid=uid,kind=kind,state=state,category='NONCONTENDING_SYSTEM_SERVICE',firmware=q['fingerprint'],evidenceSha256='f'*64,factScope=q['factScope'],validFromUtc=q['collectedAtUtc'],validToUtc=q['expiresAtUtc'],range='EXACT_SNAPSHOT'))
def context(t,q=None):
 q=q or qualification();raw=t.encode();return dict(scope=q['targetScope'],runId=q['targetRunId'],mode='OFFLINE_FIXTURE',rawSha256=sha(raw),rawBytes=len(raw),captureBodyReturned=True,sourceSealSha256=q['targetSourceSealSha256'],planSha256=q['targetPlanSha256'],reviewEvidenceSha256=q['reviewEvidenceSha256'],nowUtc=datetime.now(timezone.utc).isoformat())
def role_output(home='com.zui.launcher'):
 return 'ROLE STATE (dumpsys role):\n{\n  user_states={\n    user_id=0\n    version=1\n    packages_hash=FIXTURE_HASH\n    roles={\n      name=android.app.role.HOME\n      holders='+home+'\n    }\n  }\n}\n'
def wire():
 outs=['TB138FC\n','31\n','SYNTHETIC_FIXTURE_FIRMWARE_API31\n','0\n','package:com.zui.launcher uid:10012\n',role_output(),'com.zui.launcher/.Launcher\n'];ids=['model','api','firmware','user','system','role','home'];b=b'GI_FACTS_V1\n'
 for i,o in zip(ids,outs):
  raw=o.encode();b+=f'GI_ITEM|{i}|0|1000|1000|{len(raw)}\n'.encode()+raw+b'\n'
 return b+b'GI_FACTS_END\n'
