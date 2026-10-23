from pathlib import Path
import subprocess
from profile import plan,checks,PY,PS
from capture_policy import snapshot
def inside(p,W):return Path(p).is_absolute() and Path(p).is_relative_to(W) and '..' not in Path(p).parts
def candidate_shape(a,B,W):
 if type(a) is not list or any(type(x) is not str for x in a):return False
 if a==[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE']:return True
 if len(a)==7 and a[:6]==[PY,'-I','-X','utf8','-B',str(B/'selfchecks/route_fixture.py')]:return inside(a[6],W) and Path(a[6]).name=='gate-context.json' and Path(a[6]).parent.name=='outputs'
 if len(a)==11 and a[:4]==[PS,'-NoProfile','-NonInteractive','-File']:
  sp=Path(a[4]);req=Path(a[6]);role=req.stem.removeprefix('request-')
  return inside(sp,W) and sp.name=='capture_android02.ps1' and sp.parent.name=='tools' and req.parent==sp.parent.parent and req.name=='request-'+role+'.json' and role in ('identity','global_idle','app_absence','test_absence','install_app','install_test','scope_all') and a[5]=='-RequestPath' and a[7]=='-PredecessorProofSha' and a[9]=='-OwnerAdmissionSha' and all(len(x)==64 and all(c in '0123456789abcdef' for c in x) for x in (a[8],a[10]))
 return False
def own_shape(a,B,W):
 if type(a) is not list:return False
 if len(a)==7 and a[:5]==[PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/prestart_lifetimes.ps1')]:return a[5]=='-OutputFile' and inside(a[6],W)
 if len(a)==5 and a[:4]==[PS,'-NoProfile','-NonInteractive','-File']:return inside(a[4],W) and Path(a[4]).name=='post-guard-host.ps1'
 if a[:6]!=[PY,'-I','-X','utf8','-B',str(B/'tools/production_runner.py')]:return False
 tail=a[6:]
 if tail in ([],['--mode','live']):return True
 return len(tail)==10 and tail[::2]==['--mode','--permit','--permit-sha256','--approval','--approval-sha256'] and tail[1] in ('fixture','live') and all(inside(tail[i],W) for i in (3,7)) and all(len(tail[i])==64 and all(c in '0123456789abcdef' for c in tail[i]) for i in (5,9))
def pure_review(R,B,W):
 rows=[]
 def check(name,value,expected):assert value is expected,(name,value,expected);rows.append(dict(name=name,actual=value,expected=expected,pureOnly=True))
 own=[[PY,'-I','-X','utf8','-B',str(R/'worker.py'),'a'*64],[PY,'-I','-X','utf8','-B',str(B/'tools/production_runner.py'),'--mode','fixture','--permit',str(W/'x/permit.json'),'--permit-sha256','a'*64,'--approval',str(W/'x/approval.json'),'--approval-sha256','b'*64],[PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/prestart_lifetimes.ps1'),'-OutputFile',str(W/'prestart.json')]]
 for a in own:
  p=plan(a,R);ds=checks(p)
  for d in ds:check('own-'+d['name'],d['result']['allowed'],d['name']=='exact')
 candidates=[[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'],[PY,'-I','-X','utf8','-B',str(B/'selfchecks/route_fixture.py'),str(W/'x/h/outputs/gate-context.json')],[PS,'-NoProfile','-NonInteractive','-File',str(W/'x/h/tools/capture_android02.ps1'),'-RequestPath',str(W/'x/h/request-identity.json'),'-PredecessorProofSha','a'*64,'-OwnerAdmissionSha','b'*64]]
 for a in candidates:
  check('candidate-positive',candidate_shape(a,B,W),True)
  for label,b in [('extra',a+['X']),('SDK',['D:/Android/SDK/platform-tools/adb.exe',*a[1:]]),('other-branch',['C:/Foreign/python.exe',*a[1:]])]:check(label,candidate_shape(b,B,W),False)
  check('raw-None-string-complete',snapshot((None,subprocess.list2cmdline(a),None,None))['complete'],True)
 return rows
