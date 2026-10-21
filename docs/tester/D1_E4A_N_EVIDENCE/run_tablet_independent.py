import pathlib,subprocess,json,datetime,hashlib
E=pathlib.Path(__file__).resolve().parent;O=E/'tablet';ADB=r'D:\Android\SDK\platform-tools\adb.exe';S='HA1Q6WXR'
def run(args,name):
 p=subprocess.run([ADB,'-s',S]+args,capture_output=True,timeout=60);(O/(name+'.txt')).write_bytes(p.stdout+p.stderr);return p
method='binderRefusesBeforeBeginAndOversizeParcel'
assert not (O/'binder-result.json').exists()
identities=[]
for pkg,h in [('com.videokit.app','e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f'),('com.videokit.app.test','1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be')]:
 p=run(['shell','pm','path',pkg],pkg+'-final-path');assert p.returncode==0
 path=p.stdout.decode().strip().removeprefix('package:');p=run(['shell','sha256sum',path],pkg+'-final-hash');assert p.returncode==0 and p.stdout.decode().split()[0]==h;identities.append({'package':pkg,'sha256':h})
run(['shell','run-as','com.videokit.app','ls','-lan','files'],'before-independent-files')
before=datetime.datetime.now().astimezone().isoformat()
p=run(['shell','am','instrument','-w','-r','-e','class','com.videokit.spike.e4.E4DeviceTests#'+method,'-e','e4Case',method,'-e','e4Batch','D1-E4A-N-TABLET-20261017','-e','e4BudgetIdentity','730a73e1-50e1-4198-a515-047104f00e31','com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner'],'binder-instrumentation')
t=p.stdout.decode(errors='replace');passed=p.returncode==0 and 'OK (1 test)' in t and 'INSTRUMENTATION_CODE: -1' in t and 'FAILURES!!!' not in t
run(['shell','ps','-A','-o','PID,UID,NAME'],'post-processes')
run(['shell','run-as','com.videokit.app','ls','-lan','files','files/e4_fixtures'],'post-files')
run(['shell','dumpsys','activity','instrumentation'],'post-instrumentation')
(O/'binder-result.json').write_text(json.dumps({'method':method,'start':before,'end':datetime.datetime.now().astimezone().isoformat(),'exitCode':p.returncode,'result':'PASS' if passed else 'FAIL','installedIdentities':identities,'reasonIndependent':'Metadata-only RawEndpoint; no fixture, BEGIN, Source/Sink or encoder; fixture preparation failed before any E4Session execution','attempts':1},indent=2),encoding='utf-8')
print(t);print('RESULT',passed)
