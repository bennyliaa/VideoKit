from pathlib import Path
import subprocess,json,sys
B=Path(__file__).resolve().parents[1];E=B/'evidence'/sys.argv[1];E.mkdir(exist_ok=False);PS=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
for name,script in [('outer-budget','measure_budget.ps1'),('static-policy','check_static.ps1')]:
 cmd=[str(PS),'-NoProfile','-File',str(B/'tools'/script),'-Candidate',str(B)]
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(cmd,stdout=so,stderr=se)
  try:code=p.wait(timeout=20)
  except subprocess.TimeoutExpired:(E/(name+'.pending.json')).write_text(json.dumps(dict(pid=p.pid,sameOriginalParentCustody=True,killed=False)));code=p.wait()
 (E/(name+'.exit.json')).write_text(json.dumps(dict(argv=cmd,pid=p.pid,exitCode=code,naturalReturn=True,filesCloseReturned=True),indent=2)+'\n');assert code==0,(E/(name+'.stderr.txt')).read_text();print(name,'PASS')
budget=json.loads((E/'outer-budget.stdout.txt').read_text(encoding='utf-8-sig'));assert budget['status']=='PASS' and budget['totalUpperBound']==8157 and budget['remaining']==35
