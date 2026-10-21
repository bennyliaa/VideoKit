import argparse,hashlib,importlib.util,json,pathlib,re,subprocess,tarfile
R=pathlib.Path(r'D:\CodexProjects\VideoKit');B=pathlib.Path(__file__).resolve().parent;ADB=r'D:\Android\SDK\platform-tools\adb.exe'
spec=importlib.util.spec_from_file_location('guard',R/'docs/coder/d1c10/tools/device_guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
p=argparse.ArgumentParser();p.add_argument('device',choices=['phone','tablet']);p.add_argument('--legacy',action='store_true');a=p.parse_args();SERIAL,MODEL={'phone':('U4999DLBNRR89DOR','PDYM20'),'tablet':('HA1Q6WXR','TB138FC')}[a.device];O=B/a.device;O.mkdir(exist_ok=True)
def run(parts,timeout=60,required=True):
 r=subprocess.run([ADB,'-s',SERIAL]+parts,capture_output=True,timeout=timeout)
 if required and r.returncode:raise RuntimeError('ADB_COMMAND_NONZERO '+str(parts)+(r.stdout+r.stderr).decode(errors='replace'))
 return r.stdout
def text(parts,**kw):return run(parts,**kw).decode(errors='replace').strip()
assert json.loads((B/'admission-check.json').read_text())['result']=='DEBUG_G01_PASS'
assert text(['shell','getprop','ro.product.model'])==MODEL
api=int(text(['shell','getprop','ro.build.version.sdk']));abi=text(['shell','getprop','ro.product.cpu.abilist']);assert api>=31 and 'arm64-v8a' in abi
user=text(['shell','am','get-current-user']);assert user.isdigit()
pkgtext=text(['shell','pm','list','packages','-U','com.videokit']);uids={m.group(1):int(m.group(2)) for m in re.finditer(r'package:(\S+) uid:(\d+)',pkgtext)}
assert set(uids)<=set(['com.videokit.app','com.videokit.app.test','com.videokit.worker.spike'])
known={}
for f in (R/'docs/coder').glob('d1*/evidence/freeze-summary.json'):
 s=json.loads(f.read_text())
 for artifact in s.get('artifacts',[]):
  if artifact['path'].endswith('.apk'):known.setdefault(artifact['sha256'],[]).append((s['candidateId'],pathlib.Path(artifact['path']).name))
mapping={'com.videokit.app':'app-debug.apk','com.videokit.app.test':'app-debug-androidTest.apk','com.videokit.worker.spike':'worker-debug.apk'}
targets=['com.videokit.worker.spike'] if a.legacy else ['com.videokit.app','com.videokit.app.test'];identities=[];appdump=text(['shell','dumpsys','package','com.videokit.app'])
for package in targets:
 name=mapping[package]
 if package not in uids:identities.append(dict(package=package,previous='ABSENT'));continue
 dump=run(['shell','dumpsys','package',package]);(O/(package+'-before-'+('legacy' if a.legacy else 'cpu')+'.txt')).write_bytes(dump)
 paths=text(['shell','pm','path',package]).splitlines();assert len(paths)==1;path=paths[0].removeprefix('package:').strip();dst=O/('before-'+name);assert not dst.exists();run(['pull',path,str(dst)])
 h=hashlib.sha256(dst.read_bytes()).hexdigest();assert h in known and any(n==name for _,n in known[h])
 identities.append(dict(package=package,uid=uids[package],sha256=h,knownCandidate=known[h],backup=dst.name,path=path))
if not a.legacy:
 cache=run(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],120);(O/'cache-before-c10.tar').write_bytes(cache)
 with tarfile.open(O/'cache-before-c10.tar') as t:members=[dict(path=m.name,bytes=m.size) for m in t.getmembers()]
 facts=dict(serial=SERIAL,model=MODEL,api=api,abi=abi,user=int(user),pageSize=text(['shell','getconf','PAGE_SIZE']),space=text(['shell','df','-k','/data']),packages=uids,oldIdentities=identities,cacheEntries=members,cacheBackupSha256=hashlib.sha256(cache).hexdigest())
 (O/'preflight.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
try:guard.installed_state(appdump,int(user))
except guard.EnvironmentBlocked as e:
 (O/'environment.json').write_text(json.dumps(dict(state='ENVIRONMENT_BLOCKED',code=str(e),noInstall=True,noInstrumentation=True,noEnableAttempt=True),indent=2),encoding='utf-8');print('ENVIRONMENT_BLOCKED '+str(e),flush=True);raise SystemExit(3)
for package in targets:
 name=mapping[package];output=text(['install']+(['-r'] if package in uids else [])+[str(B/'candidate'/name)],timeout=120);assert 'Success' in output;print(name+' Success',flush=True)
(O/('uids-legacy.txt' if a.legacy else 'uids.txt')).write_text(text(['shell','pm','list','packages','-U','com.videokit']),encoding='utf-8')
ready=guard.require_ready(SERIAL,lambda parts:text(parts,timeout=20));(O/'environment-ready.json').write_text(json.dumps(ready,indent=2),encoding='utf-8')
if a.legacy:
 (O/'legacy-preflight.json').write_text(json.dumps(identities,indent=2),encoding='utf-8');raise SystemExit(0)
def own(parts,**kw):return text(['shell','run-as','com.videokit.app']+parts,**kw)
assert not own(['ls','files/d1_c10_fixtures'],required=False),'EXISTING_C10_FIXTURE_STOP'
fixtures={'basic.mp4':(349102,'720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9'),'subtitle.avi':(736454656,'3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f')};sources={}
for alias,(size,digest) in fixtures.items():
 for prior in range(9,1,-1):
  source='files/d1_c0'+str(prior)+'_fixtures/'+alias
  if own(['stat','-c','%s',source],required=False)!=str(size):continue
  assert own(['sha256sum',source],timeout=180).split()[0]==digest;sources[alias]=source;break
 assert alias in sources
free=int(text(['shell','df','-k','/data']).splitlines()[-1].split()[3])*1024;assert free>736803758+736454656+268435456
own(['mkdir','files/d1_c10_fixtures']);out=[]
for alias,(size,digest) in fixtures.items():
 target='files/d1_c10_fixtures/'+alias;own(['cp',sources[alias],target],timeout=180);assert own(['stat','-c','%s',target])==str(size);assert own(['sha256sum',target],timeout=180).split()[0]==digest
 out.append(dict(alias=alias,bytes=size,sha256=digest,source=sources[alias],target=target));print('FIXTURE_PASS '+alias,flush=True)
(O/'fixtures.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('PREPARATION_READY '+a.device,flush=True)
