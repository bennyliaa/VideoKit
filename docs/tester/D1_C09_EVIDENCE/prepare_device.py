import argparse,hashlib,json,pathlib,re,subprocess,tarfile
R=pathlib.Path(r'D:\CodexProjects\VideoKit');B=pathlib.Path(__file__).resolve().parent
ADB=r'D:\Android\SDK\platform-tools\adb.exe'
DEVICES={'phone':('U4999DLBNRR89DOR','PDYM20'),'tablet':('HA1Q6WXR','TB138FC')}
p=argparse.ArgumentParser();p.add_argument('device',choices=DEVICES);p.add_argument('--legacy',action='store_true');args=p.parse_args()
SERIAL,MODEL=DEVICES[args.device];O=B/args.device;O.mkdir(exist_ok=True)
def adb(parts,timeout=60,required=True):
 c=subprocess.run([ADB,'-s',SERIAL]+parts,capture_output=True,timeout=timeout)
 if required and c.returncode:raise RuntimeError((c.stdout+c.stderr).decode(errors='replace'))
 return c.stdout
def txt(parts,**kw):return adb(parts,**kw).decode(errors='replace').strip()
assert json.loads((B/'admission-check.json').read_text())['result']=='DEBUG_G01_STATIC_REVIEW_PASS'
assert txt(['shell','getprop','ro.product.model'])==MODEL
assert int(txt(['shell','getprop','ro.build.version.sdk']))>=31
assert 'arm64-v8a' in txt(['shell','getprop','ro.product.cpu.abilist'])
known={}
for f in (R/'docs/coder').glob('d1*/evidence/freeze-summary.json'):
 s=json.loads(f.read_text(encoding='utf-8'))
 for a in s.get('artifacts',[]):
  if a['path'].endswith('.apk'):known.setdefault(a['sha256'],[]).append((s.get('candidateId'),pathlib.Path(a['path']).name))
packages=txt(['shell','pm','list','packages','-U','com.videokit'])
parsed={m.group(1):int(m.group(2)) for m in re.finditer(r'package:(\S+) uid:(\d+)',packages)}
assert set(parsed)<=set(['com.videokit.app','com.videokit.app.test','com.videokit.worker.spike']),packages
mapping={'com.videokit.app':'app-debug.apk','com.videokit.app.test':'app-debug-androidTest.apk','com.videokit.worker.spike':'worker-debug.apk'}
targets=['com.videokit.worker.spike'] if args.legacy else ['com.videokit.app','com.videokit.app.test']
records=[]
for package in targets:
 name=mapping[package]
 if package not in parsed:records.append(dict(package=package,previous='ABSENT'));continue
 info=adb(['shell','dumpsys','package',package]);(O/(package+'-before-'+('legacy' if args.legacy else 'cpu')+'.txt')).write_bytes(info)
 paths=txt(['shell','pm','path',package]).splitlines();assert len(paths)==1
 path=paths[0].removeprefix('package:').strip();dest=O/('before-'+name)
 adb(['pull',path,str(dest)]);digest=hashlib.sha256(dest.read_bytes()).hexdigest()
 assert digest in known and any(n==name for _,n in known[digest]),(package,digest,'UNKNOWN_DATA_STOP')
 records.append(dict(package=package,uid=parsed[package],oldApkPath=path,sha256=digest,knownCandidates=known[digest],backup=dest.name))
if not args.legacy:
 preflight=dict(serial=SERIAL,model=MODEL,api=txt(['shell','getprop','ro.build.version.sdk']),abi=txt(['shell','getprop','ro.product.cpu.abilist']),pageSize=txt(['shell','getconf','PAGE_SIZE']),space=txt(['shell','df','-k','/data']),packages=parsed,oldIdentities=records)
 if 'com.videokit.app' in parsed:
  backup=adb(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],120)
  (O/'cache-before-c09.tar').write_bytes(backup)
  with tarfile.open(O/'cache-before-c09.tar') as t:preflight['cacheEntries']=[dict(path=m.name,bytes=m.size) for m in t.getmembers()]
  preflight['cacheBackupSha256']=hashlib.sha256(backup).hexdigest()
 (O/'preflight.json').write_text(json.dumps(preflight,ensure_ascii=False,indent=2),encoding='utf-8')
print('IDENTITY_AND_BACKUP_PASS '+args.device,flush=True)
for package in targets:
 name=mapping[package];parts=['install']+(['-r'] if package in parsed else [])+[str(R/'docs/coder/d1c09/artifacts/D1-20261016-C09'/name)]
 output=txt(parts,timeout=120);assert 'Success' in output;print(name+' Success',flush=True)
uids=txt(['shell','pm','list','packages','-U','com.videokit']);(O/('uids-legacy.txt' if args.legacy else 'uids.txt')).write_text(uids,encoding='utf-8')
if args.legacy:
 (O/'legacy-preflight.json').write_text(json.dumps(records,indent=2),encoding='utf-8');raise SystemExit(0)
def own(parts,**kw):return txt(['shell','run-as','com.videokit.app']+parts,**kw)
fixed={'basic.mp4':(349102,'720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9'),'subtitle.avi':(736454656,'3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f')}
assert not own(['ls','files/d1_c09_fixtures'],required=False),'EXISTING_C09_DIRECTORY_STOP'
sources={}
for alias,(size,digest) in fixed.items():
 for old in range(8,1,-1):
  source='files/d1_c0'+str(old)+'_fixtures/'+alias
  stat=own(['stat','-c','%s',source],required=False)
  if stat!=str(size):continue
  actual=own(['sha256sum',source],timeout=180).split()[0]
  assert actual==digest,(source,'SOURCE_HASH_MISMATCH_STOP')
  sources[alias]=source;break
 assert alias in sources,(alias,'NO_TRUSTED_PRIVATE_COPY')
free=int(txt(['shell','df','-k','/data']).splitlines()[-1].split()[3])*1024
assert free>sum(s for s,_ in fixed.values())+268435456
own(['mkdir','files/d1_c09_fixtures'])
fixtures=[]
for alias,(size,digest) in fixed.items():
 target='files/d1_c09_fixtures/'+alias;own(['cp',sources[alias],target],timeout=180)
 assert own(['stat','-c','%s',target])==str(size)
 assert own(['sha256sum',target],timeout=180).split()[0]==digest
 fixtures.append(dict(alias=alias,bytes=size,sha256=digest,sourcePrivatePath=sources[alias],destinationPrivatePath=target,hashMatch=True));print('FIXTURE_PASS '+alias,flush=True)
(O/'fixtures.json').write_text(json.dumps(fixtures,indent=2),encoding='utf-8')
print('CPU_PREPARED '+args.device,flush=True)
