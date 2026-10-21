import hashlib,json,pathlib,subprocess,tarfile
ROOT=pathlib.Path(r'D:\CodexProjects\VideoKit'); BASE=pathlib.Path(__file__).resolve().parent
ADB=r'D:\Android\SDK\platform-tools\adb.exe'; SERIAL='HA1Q6WXR'
def run(args,timeout=60):
 p=subprocess.run([ADB,'-s',SERIAL]+args,capture_output=True,timeout=timeout)
 if p.returncode: raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 return p.stdout
packages={'com.videokit.app':('app-debug.apk','f2d3a9473f27f5281a0214e04a821bca7a6fc579a5f9a1d9ffb50c539e62e937'),'com.videokit.app.test':('app-debug-androidTest.apk','c70362b629030f4a27e66a51a50e69b5e4834f7e54718d23682ab2b6969a8c13'),'com.videokit.worker.spike':('worker-debug.apk','ad1f9785218bb996c5b25c8f24eeb7e1080101c7690b0ec857f5a51a4d90fdc5')}
records=[]
for package,(name,expected) in packages.items():
 info=run(['shell','dumpsys','package',package]);(BASE/(package+'-c04-package.txt')).write_bytes(info)
 paths=run(['shell','pm','path',package]).decode().strip().splitlines();assert len(paths)==1
 path=paths[0].removeprefix('package:').strip()
 destination=BASE/('c04-installed-'+name)
 run(['pull',path,str(destination)])
 actual=hashlib.sha256(destination.read_bytes()).hexdigest();assert actual==expected,(package,actual)
 records.append(dict(package=package,path=path,sha256=actual,backup=str(destination)))
backup=run(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],120)
(BASE/'c04-cache-before-update.tar').write_bytes(backup)
with tarfile.open(BASE/'c04-cache-before-update.tar') as archive:
 names=archive.getnames()
 assert any(n.endswith('.journal') for n in names)
(BASE/'c04-update-preflight.json').write_text(json.dumps(dict(serial=SERIAL,packages=records,cacheBackup='c04-cache-before-update.tar',cacheBackupSha256=hashlib.sha256(backup).hexdigest(),entries=names),indent=2),encoding='utf-8')
print('C04_IDENTITY_AND_CACHE_BACKUP_PASS',flush=True)
for package,(name,_) in packages.items():
 output=run(['install','-r',str(ROOT/'docs/coder/d1c05/artifacts/D1-20261005-C05'/name)],120)
 print(name+' '+output.decode().strip(),flush=True)
print('C05_UPDATE_FINISHED',flush=True)

