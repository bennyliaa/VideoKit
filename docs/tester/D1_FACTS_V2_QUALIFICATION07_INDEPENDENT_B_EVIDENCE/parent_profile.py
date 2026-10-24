from pathlib import Path
import subprocess
from parent_policy import validate_plan,audit_decision
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
def plan(argv,R):
 p=dict(schema='OWNED_CAPTURE_PLAN_V1',profile='python_ok' if argv[0]==PY else 'powershell_ok',executable=argv[0],argv=list(argv),commandLine=subprocess.list2cmdline(argv),cwd=str(R),env=dict(SystemRoot=str(Path('C:/Windows')),WINDIR=str(Path('C:/Windows')),TEMP=str(R),TMP=str(R)),shell=False,closeFds=True);validate_plan(p,p);return p
def checks(p):
 a=(p['executable'],p['commandLine'],p['cwd'],p['env']);rows=[]
 for label,args,expected in [('exact',a,True),('applicationName-None',(None,*a[1:]),False),('foreign-program',('C:/foreign.exe',*a[1:]),False),('extra-command',(a[0],a[1]+' --extra',*a[2:]),False),('wrong-cwd',(a[0],a[1],str(Path(p['cwd']).parent),a[3]),False),('wrong-env',(*a[:3],{}),False)]:
  d=audit_decision('subprocess.Popen',args,p,p,active=True,same_owner=True,event_unused=True);assert d['allowed']==expected;rows.append(dict(name=label,result=d,pureOnly=True))
 return rows
def preflight(R):
 profiles=[plan([PY,'-I','-X','utf8','-B',str(R/'worker.py'),'0'*64],R),plan([PS,'-NoProfile','-NonInteractive','-File',str(R/'host.ps1'),'-InputFile',str(R/'input-index.json'),'-OutputFile',str(R/'semantic-results.json')],R)]
 return dict(actualConstructors=0,profiles=profiles,checks=[checks(p) for p in profiles],windowsAudit='Observe only, never raise after temporary creation. All real argv/cwd/env checked before constructor. None applicationName/string commandLine represented as raw four-tuple, not argv array.')
