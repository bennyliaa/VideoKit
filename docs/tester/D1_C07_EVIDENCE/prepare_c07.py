import hashlib,json,pathlib,subprocess,tarfile
ROOT=pathlib.Path(r'D:\CodexProjects\VideoKit'); BASE=pathlib.Path(__file__).resolve().parent
ADB=r'D:\Android\SDK\platform-tools\adb.exe'; SERIAL='HA1Q6WXR'
def run(args,timeout=60):
 p=subprocess.run([ADB,'-s',SERIAL]+args,capture_output=True,timeout=timeout)
 if p.returncode: raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 return p.stdout
packages={'com.videokit.app':('app-debug.apk','a01b2b088dc9e8284d308b3bec774d33609870000f634ade228579646a27e969'),'com.videokit.app.test':('app-debug-androidTest.apk','de25e0fe50eb5e0c30e554b67b06a91cd6f5a42f543a4edd756cd935b09e6687'),'com.videokit.worker.spike':('worker-debug.apk','616769985e150841743007379ec456d9e5e00a01792981424778d5c751026e16')}
records=[]
for package,(name,expected) in packages.items():
 info=run(['shell','dumpsys','package',package]);(BASE/(package+'-c06-package.txt')).write_bytes(info)
 paths=run(['shell','pm','path',package]).decode().strip().splitlines();assert len(paths)==1
 path=paths[0].removeprefix('package:').strip()
 destination=BASE/('c06-installed-'+name)
 run(['pull',path,str(destination)])
 actual=hashlib.sha256(destination.read_bytes()).hexdigest();assert actual==expected,(package,actual)
 records.append(dict(package=package,path=path,sha256=actual,backup=str(destination)))
backup=run(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],120)
(BASE/'c06-cache-before-update.tar').write_bytes(backup)
with tarfile.open(BASE/'c06-cache-before-update.tar') as archive:
 names=archive.getnames()
 assert any(n.endswith('.journal') for n in names)
(BASE/'c06-update-preflight.json').write_text(json.dumps(dict(serial=SERIAL,packages=records,cacheBackup='c06-cache-before-update.tar',cacheBackupSha256=hashlib.sha256(backup).hexdigest(),entries=names),indent=2),encoding='utf-8')
captures=[m for m in names if m.startswith('cache/d1_c06_capture_') and m.endswith('.mp4')]
assert len(captures)==2
assert not any(m.startswith('cache/d1_c07_capture_') for m in names)
with tarfile.open(BASE/'c06-cache-before-update.tar') as a:
    assert all(a.getmember(m).size<=2097152 for m in captures)
print('C06_IDENTITY_CACHE_AND_CAPTURE_BUDGET_PASS',flush=True)
for package,(name,_) in packages.items():
 output=run(['install','-r',str(ROOT/'docs/coder/d1c07/artifacts/D1-20261005-C07'/name)],120)
 print(name+' '+output.decode().strip(),flush=True)
print('C07_UPDATE_FINISHED',flush=True)



