"""One externally authorized T1P tablet batch; preserves its interpreter on unknown owners."""
from pathlib import Path
import sys,json,hashlib,datetime,time
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B/'evidence/close-freeze.json')=='954288092916e5281c7a50183adc9041e82c05d16cfe6fd6cd5013fb75139c0f'
seal=json.loads((B/'evidence/close-freeze.json').read_text())
for row in seal['immutable']:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
sys.path.insert(0,str(B/'tools'))
import exact_process as ep
import fixture_transfer as ft
assert Path(ep.__file__).resolve()==B/'tools/exact_process.py'
assert Path(ft.__file__).resolve()==B/'tools/fixture_transfer.py'
plan=json.loads((B/'tools/tablet-preload-plan.json').read_text());ADB=plan['adb'];S=plan['serial'];assert S=='HA1Q6WXR'
assert not (E/'batch-start.json').exists()
def now():return datetime.datetime.now().astimezone().isoformat()
def logbudget():
 n=sum(p.stat().st_size for p in E.rglob('*') if p.is_file());assert n<8388608-524288,'EVIDENCE_BUDGET_STOP'
def new(name,value):
 logbudget()
 with (E/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
new('batch-start.json',{'at':now(),'batch':plan['proposal'],'externalAuthority':'docs/milestones/D1_E4A_T1P_TESTER_REQUIREMENTS_V1.0.md','toolImports':{'exact_process':str(ep.__file__),'fixture_transfer':str(ft.__file__)},'frozenJsonChanged':False})
records=[];results=[];backends=[];failure=None
def cmd(args,name):
 logbudget();p=ep.collect([ADB,'-s',S]+args,ep.Limits(timeout=120,stdout_cap=65536,stderr_cap=65536));records.append({'name':name,'result':p});new(name+'.json',p)
 data=ep.stdout_bytes(p)
 if p['stderr']['bytes']:raise RuntimeError('PREFLIGHT_STDERR_'+name)
 return data.decode('utf-8','strict').strip()
def remote(script,name):return cmd(ft.run_as_argv(ADB,S,'shell',script)[3:],name)
try:
 assert cmd(['get-state'],'connection')=='device'
 assert cmd(['shell','getprop','ro.product.model'],'model')=='TB138FC'
 assert int(cmd(['shell','getprop','ro.build.version.sdk'],'api'))>=31
 assert 'arm64-v8a' in cmd(['shell','getprop','ro.product.cpu.abilist'],'abi')
 assert cmd(['shell','am','get-current-user'],'user')=='0'
 for pkg,h in [('com.videokit.app','e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f'),('com.videokit.app.test','1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be')]:
  path=cmd(['shell','pm','path',pkg],pkg+'-path');assert path.startswith('package:') and '\n' not in path
  assert cmd(['shell','sha256sum',path[8:]],pkg+'-sha').split()[0]==h
 dump=cmd(['shell','dumpsys','package','com.videokit.app'],'package-state')
 assert 'installed=true hidden=false suspended=false' in dump and ('enabled=0' in dump or 'enabled=1' in dump)
 space=cmd(['shell','df','-k','/data'],'space');free=int(space.splitlines()[-1].split()[3])*1024
 assert free>=plan['budgets']['additionalPayloadSpaceBytes']+268435456
 script="set -e; test \"$(id -u)\" = 10221; test \"$(pwd)\" = /data/user/0/com.videokit.app; test -d files; test ! -L files; test -d files/e4_fixtures; test ! -L files/e4_fixtures; test -r files/e4_fixtures; test -w files/e4_fixtures; id; pwd; /system/bin/toybox stat -c '%u %a %F' -- files/e4_fixtures; ls -lan files/e4_fixtures; if [ -e files/e4a_output_budget/operation.pending ]; then printf 'PRIOR_PENDING\\n'; else printf 'NO_PRIOR_PENDING\\n'; fi; set -C; cat /dev/null"
 roles=remote(script,'roles-and-noclobber');assert 'NO_PRIOR_PENDING' in roles and '10221' in roles
 for tool in ['mv','stat','sha256sum']:
  helptext=remote('/system/bin/toybox '+tool+' --help','toybox-'+tool)
  if tool=='mv':assert '-n' in helptext or '[-' in helptext and 'n' in helptext
 new('preflight-admitted.json',{'at':now(),'serial':S,'user':0,'appUid':10221,'installedFinalApksVerified':True,'enabled':True,'freeBytes':free,'newPayloadBytes':736803758,'retainedResidualBytes':81407,'marginBytes':268435456,'sourceOpened':False})
 print('PREFLIGHT_ADMITTED',flush=True)
 for item in plan['files']:
  logbudget();backend=ft.AdbBackend(ADB,S,execution_authorized=True,timeout=item['timeoutSeconds']);backends.append(backend)
  old=item['residual'];print('START_ONCE '+item['alias']+' '+now(),flush=True)
  result=ft.provision_once(backend,item['source'],ft.FileProof(item['bytes'],item['sha256']),item['final'],item['temp'],E,attempt_id=item['attemptId'],residual=ft.FileProof(old['bytes'],old['sha256']) if old else None,archive_path=item['archive'])
  results.append(result);new(item['alias']+'-backend-logs.json',backend.logs)
  print('RESULT '+item['alias']+' '+result['status']+' '+str(result.get('firstFailure')),flush=True)
  if result['status']!='FIXTURE_ADMITTED':break
except Exception as error:
 failure={'type':type(error).__name__,'message':str(error)};print('STOP '+repr(failure),flush=True)
for index,backend in enumerate(backends):
 if not (E/(plan['files'][index]['alias']+'-backend-logs.json')).exists():new(plan['files'][index]['alias']+'-backend-logs.json',backend.logs)
retained=ep.retained_owners()
new('batch-result.json',{'at':now(),'batch':plan['proposal'],'results':results,'failure':failure,'retainedOriginalProcessOwners':retained,'status':'BOTH_FIXTURES_ADMITTED' if len(results)==2 and all(x['status']=='FIXTURE_ADMITTED' for x in results) else 'STOPPED_NOT_FULLY_ADMITTED','preflightCommands':len(records),'nextProductTestsAuthorized':False})
print('BATCH_FINISHED retained='+str(retained),flush=True)
if retained:
 print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED_DO_NOT_TERMINATE',flush=True)
 while True:time.sleep(1)
