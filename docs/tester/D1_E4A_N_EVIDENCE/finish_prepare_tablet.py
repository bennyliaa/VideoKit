import pathlib,subprocess,json,hashlib,shutil,datetime
R=pathlib.Path(__file__).resolve().parents[3];E=pathlib.Path(__file__).resolve().parent;O=E/'tablet';ADB=r'D:\Android\SDK\platform-tools\adb.exe';S='HA1Q6WXR'
def run(args,name,timeout=60):
 p=subprocess.run([ADB,'-s',S]+args,capture_output=True,timeout=timeout);(O/(name+'.txt')).write_bytes(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(name+' failed')
 return p.stdout.decode(errors='replace').strip()
def own(args,name,**kw):return run(['shell','run-as','com.videokit.app']+args,name,**kw)
assert (O/'install-app-debug.apk.txt').read_text().strip().endswith('Success')
run(['shell','dumpsys','package','com.videokit.app'],'app-after-update')
assert 'versionName=D1-E4A' in (O/'app-after-update.txt').read_text()
A=R/'docs/coder/d1e4a/artifacts/D1-20261017-E4A/final/app-debug-androidTest.apk'
assert hashlib.sha256(A.read_bytes()).hexdigest()=='1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be'
assert run(['install','-r','-t',str(A)],'install-app-debug-androidTest.apk',timeout=120).endswith('Success')
print('FINAL_APKS_INSTALLED_KEEP_DATA',flush=True)
fixtures=json.loads((O/'host-source-verified.json').read_text())['fixtures']
own(['mkdir','files/e4_fixtures'],'mkdir-fixtures')
for alias,rel,n,h in fixtures:
 target='files/e4_fixtures/'+alias
 p=subprocess.Popen([ADB,'-s',S,'exec-in','run-as','com.videokit.app','tee',target],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 with (R/'test_media'/rel).open('rb') as f:shutil.copyfileobj(f,p.stdin,1048576)
 p.stdin.close();p.stdin=None;_,err=p.communicate(timeout=120);(O/('transfer-'+alias+'.txt')).write_bytes(err);assert p.returncode==0
 assert own(['stat','-c','%s',target],'size-'+alias)==str(n)
 assert own(['sha256sum',target],'hash-'+alias,timeout=120).split()[0]==h
 print('FIXTURE_READY '+alias,flush=True)
(O/'prepared.json').write_text(json.dumps({'at':datetime.datetime.now().astimezone().isoformat(),'copyBytes':736803758,'hostHashBytes':736803758,'devicePreprovisionHashBytes':736803758,'oldCacheBackupBytes':(O/'cache-before.tar').stat().st_size,'budgetIdentity':'730a73e1-50e1-4198-a515-047104f00e31','batch':'D1-E4A-N-TABLET-20261017','ready':True},indent=2),encoding='utf-8')
