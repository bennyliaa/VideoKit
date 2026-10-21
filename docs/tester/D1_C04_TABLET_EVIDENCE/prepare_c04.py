import hashlib,json,pathlib,subprocess,tarfile
ROOT=pathlib.Path(r'D:\CodexProjects\VideoKit'); BASE=pathlib.Path(__file__).resolve().parent
ADB=r'D:\Android\SDK\platform-tools\adb.exe'; SERIAL='HA1Q6WXR'
def run(args,timeout=60):
 p=subprocess.run([ADB,'-s',SERIAL]+args,capture_output=True,timeout=timeout)
 if p.returncode: raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 return p.stdout
packages={'com.videokit.app':('app-debug.apk','efe83f6b27df9d268374008af038c68d545508cec13cb35e118ae973fc0e66ac'),'com.videokit.app.test':('app-debug-androidTest.apk','8b0f3f2a316f22395505782090533f4fc0f84ddd89227282f31fa5aec505466d'),'com.videokit.worker.spike':('worker-debug.apk','1bc6b4785884bf86d998e46f46856c3f55d787bfe1acf341d6b7e3ccf01e7503')}
records=[]
for package,(name,expected) in packages.items():
 info=run(['shell','dumpsys','package',package]);(BASE/(package+'-c03-package.txt')).write_bytes(info)
 paths=run(['shell','pm','path',package]).decode().strip().splitlines();assert len(paths)==1
 path=paths[0].removeprefix('package:').strip()
 destination=BASE/('c03-installed-'+name)
 run(['pull',path,str(destination)])
 actual=hashlib.sha256(destination.read_bytes()).hexdigest();assert actual==expected,(package,actual)
 records.append(dict(package=package,path=path,sha256=actual,backup=str(destination)))
backup=run(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],120)
(BASE/'c03-cache-before-update.tar').write_bytes(backup)
with tarfile.open(BASE/'c03-cache-before-update.tar') as archive:
 names=archive.getnames()
 assert any(n.endswith('.journal') for n in names)
(BASE/'c03-update-preflight.json').write_text(json.dumps(dict(serial=SERIAL,packages=records,cacheBackup='c03-cache-before-update.tar',cacheBackupSha256=hashlib.sha256(backup).hexdigest(),entries=names),indent=2),encoding='utf-8')
print('C03_IDENTITY_AND_CACHE_BACKUP_PASS',flush=True)
for package,(name,_) in packages.items():
 output=run(['install','-r',str(ROOT/'docs/coder/d1c04/artifacts/D1-20261005-C04'/name)],120)
 print(name+' '+output.decode().strip(),flush=True)
print('C04_UPDATE_FINISHED',flush=True)
