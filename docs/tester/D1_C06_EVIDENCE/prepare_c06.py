import hashlib,json,pathlib,subprocess,tarfile
ROOT=pathlib.Path(r'D:\CodexProjects\VideoKit'); BASE=pathlib.Path(__file__).resolve().parent
ADB=r'D:\Android\SDK\platform-tools\adb.exe'; SERIAL='HA1Q6WXR'
def run(args,timeout=60):
 p=subprocess.run([ADB,'-s',SERIAL]+args,capture_output=True,timeout=timeout)
 if p.returncode: raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 return p.stdout
packages={'com.videokit.app':('app-debug.apk','4639989459c9c9ec5491e71ebe0d52ae35f705c3dbe6f24b5262a1cab9258fd9'),'com.videokit.app.test':('app-debug-androidTest.apk','abc7c2cd56ecab256567dfbe6c22f45b9780f5466d9c90c146c2627ae04b790d'),'com.videokit.worker.spike':('worker-debug.apk','591f8de03b48121e68d4a13d2d3b3a152b4b6a3044fc78e81c915cc86d0ea5b6')}
records=[]
for package,(name,expected) in packages.items():
 info=run(['shell','dumpsys','package',package]);(BASE/(package+'-c05-package.txt')).write_bytes(info)
 paths=run(['shell','pm','path',package]).decode().strip().splitlines();assert len(paths)==1
 path=paths[0].removeprefix('package:').strip()
 destination=BASE/('c05-installed-'+name)
 run(['pull',path,str(destination)])
 actual=hashlib.sha256(destination.read_bytes()).hexdigest();assert actual==expected,(package,actual)
 records.append(dict(package=package,path=path,sha256=actual,backup=str(destination)))
backup=run(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],120)
(BASE/'c05-cache-before-update.tar').write_bytes(backup)
with tarfile.open(BASE/'c05-cache-before-update.tar') as archive:
 names=archive.getnames()
 assert any(n.endswith('.journal') for n in names)
(BASE/'c05-update-preflight.json').write_text(json.dumps(dict(serial=SERIAL,packages=records,cacheBackup='c05-cache-before-update.tar',cacheBackupSha256=hashlib.sha256(backup).hexdigest(),entries=names),indent=2),encoding='utf-8')
print('C05_IDENTITY_AND_CACHE_BACKUP_PASS',flush=True)
for package,(name,_) in packages.items():
 output=run(['install','-r',str(ROOT/'docs/coder/d1c06/artifacts/D1-20261005-C06'/name)],120)
 print(name+' '+output.decode().strip(),flush=True)
print('C06_UPDATE_FINISHED',flush=True)


