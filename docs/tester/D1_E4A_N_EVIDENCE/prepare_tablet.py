import pathlib,subprocess,json,hashlib,shutil,datetime
R=pathlib.Path(__file__).resolve().parents[3];E=pathlib.Path(__file__).resolve().parent;O=E/'tablet';ADB=r'D:\Android\SDK\platform-tools\adb.exe';S='HA1Q6WXR'
def run(args,name,timeout=60,ok=True):
 p=subprocess.run([ADB,'-s',S]+args,capture_output=True,timeout=timeout);(O/(name+'.txt')).write_bytes(p.stdout+p.stderr)
 if ok and p.returncode:raise RuntimeError(name+' failed')
 return p.stdout.decode(errors='replace').strip()
def own(args,name,**kw):return run(['shell','run-as','com.videokit.app']+args,name,**kw)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
dump=(O/'admitted-transport/app-package.txt').read_text();assert 'enabled=0' in dump
assert (O/'admitted-transport/model.txt').read_text().strip()=='TB138FC'
assert int((O/'admitted-transport/api.txt').read_text())>=31
assert 'arm64-v8a' in (O/'admitted-transport/abi.txt').read_text()
listing=own(['ls','-lan','files','cache'],'correct-private-before')
assert 'e4a_output_budget' not in listing and 'e4a_outputs' not in listing and 'e4_fixtures' not in listing
for pkg,label in [('com.videokit.app','app'),('com.videokit.app.test','test')]:
 paths=run(['shell','pm','path',pkg],label+'-old-path').splitlines();assert len(paths)==1
 remote=paths[0].removeprefix('package:');dst=O/(label+'-before.apk');assert not dst.exists()
 run(['pull',remote,str(dst)],label+'-backup')
 p=subprocess.run([r'D:\Android\Android Studio\jbr\bin\java.exe','-jar',r'D:\Android\SDK\build-tools\36.0.0\lib\apksigner.jar','verify','--print-certs',str(dst)],capture_output=True,timeout=30)
 (O/(label+'-before-signature.txt')).write_bytes(p.stdout+p.stderr)
 assert p.returncode==0 and b'5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f' in p.stdout
cache=subprocess.run([ADB,'-s',S,'exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],capture_output=True,timeout=45)
assert cache.returncode==0 and len(cache.stdout)<67108864
(O/'cache-before.tar').write_bytes(cache.stdout)
fixtures=[('basic.mp4','imgs_and_videos/videos/sample.mp4',349102,'720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9'),('subtitle.avi','02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi',736454656,'3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f')]
for alias,rel,n,h in fixtures:
 p=R/'test_media'/rel;assert p.stat().st_size==n and sha(p)==h
(O/'host-source-verified.json').write_text(json.dumps({'readBytes':736803758,'fixtures':fixtures},indent=2),encoding='utf-8')
print('HOST_FIXTURES_VERIFIED',flush=True)
A=R/'docs/coder/d1e4a/artifacts/D1-20261017-E4A/final'
for name,h in [('app-debug.apk','e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f'),('app-debug-androidTest.apk','1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be')]:
 assert sha(A/name)==h
 assert run(['install','-r','-t',str(A/name)],'install-'+name,timeout=120)=='Success'
print('FINAL_APKS_INSTALLED_KEEP_DATA',flush=True)
own(['mkdir','files/e4_fixtures'],'mkdir-fixtures')
for alias,rel,n,h in fixtures:
 target='files/e4_fixtures/'+alias
 p=subprocess.Popen([ADB,'-s',S,'exec-in','run-as','com.videokit.app','tee',target],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 with (R/'test_media'/rel).open('rb') as f:shutil.copyfileobj(f,p.stdin,1048576)
 p.stdin.close();p.stdin=None;_,err=p.communicate(timeout=120);(O/('transfer-'+alias+'.txt')).write_bytes(err);assert p.returncode==0
 assert own(['stat','-c','%s',target],'size-'+alias)==str(n)
 assert own(['sha256sum',target],'hash-'+alias,timeout=120).split()[0]==h
 print('FIXTURE_READY '+alias,flush=True)
(O/'prepared.json').write_text(json.dumps({'at':datetime.datetime.now().astimezone().isoformat(),'copyBytes':736803758,'hostHashBytes':736803758,'devicePreprovisionHashBytes':736803758,'oldCacheBackupBytes':len(cache.stdout),'budgetIdentity':'730a73e1-50e1-4198-a515-047104f00e31','batch':'D1-E4A-N-TABLET-20261017','ready':True},indent=2),encoding='utf-8')
