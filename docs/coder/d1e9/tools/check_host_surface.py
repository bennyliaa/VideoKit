"""Compile future host entry tools and verify default/no-device and synthetic-release rejection paths."""
import hashlib,json,pathlib,subprocess
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];jdk=pathlib.Path('D:/Android/Android Studio/jbr/bin');classes=B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';work=B/'.selfcheck/host-final-002';work.mkdir(parents=True,exist_ok=False);out=B/'evidence/host-surface-002';out.mkdir(parents=True,exist_ok=False)
source=[B/'tools'/n for n in ['E9HostDeployment.java','E9HostManager.java','E9ActivationPolicyExport.java','E9HostActivationSession.java']];commands=[]
def run(name,args,expected):
 argv=[str(x) for x in args];r=subprocess.run(argv,capture_output=True,timeout=30);(out/(name+'.stdout.txt')).write_bytes(r.stdout);(out/(name+'.stderr.txt')).write_bytes(r.stderr);commands.append(dict(name=name,argv=argv,exitCode=r.returncode,expected=expected));assert (r.returncode==0)==(expected==0),r.stderr
run('compile',[jdk/'javac.exe','-encoding','UTF-8','-cp',classes,'-d',work,*source],0)
cp=str(work)+';'+str(classes)
for name in ['E9HostManager','E9HostActivationSession']:run(name+'-default',[jdk/'java.exe','-cp',cp,'com.videokit.spike.e4.'+name],0)
fixture=B/'.selfcheck/final-production-009/cases/A20/synthetic-external-registry';plan=(fixture/'prepare-deployment.json').read_bytes();fields=json.loads(plan)['fields']
config=dict(kind='activationTrust',plan=__import__('base64').urlsafe_b64encode(plan).decode().rstrip('='),planSha=hashlib.sha256(plan).hexdigest(),authorization=fields['authorization'],review='1'*64,registryPath=str(fixture).replace('\\','/'),head='2'*64)
raw=(json.dumps(dict(e9=1,fields=dict(sorted(config.items()))),separators=(',',':'))+'\n').encode('ascii');configpath=out/'SYNTHETIC-rejection-only-config.json';configpath.write_bytes(raw);pin=hashlib.sha256(raw).hexdigest();forbidden=work/'must-not-export'
run('synthetic-export-rejected',[jdk/'java.exe','-cp',cp,'com.videokit.spike.e4.E9HostActivationSession','--approved-export',configpath,pin,forbidden],1)
assert not forbidden.exists();assert b'E9_SYNTHETIC_RELEASE_FORBIDDEN' in (out/'synthetic-export-rejected.stderr.txt').read_bytes()
run('synthetic-deploy-rejected',[jdk/'java.exe','-cp',cp,'com.videokit.spike.e4.E9HostActivationSession','--approved-deploy',configpath,pin,'NO_ACTUAL_RELEASE','3'*64,'NO_ACTUAL_APP','NO_ACTUAL_TEST'],1)
inputs=[]
for p in source+list(classes.rglob('*.class')):
 raw=p.read_bytes();inputs.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/host-surface-check.json').write_text(json.dumps(dict(schema=1,status='PASS',commands=commands,inputs=inputs,scope='actual host classes compile/default/synthetic-denial only; actual process dispatch and all device facts NOT_RUN',deviceCalls=0,activationPolicyExported=False,actualHActor='NOT_CREATED'),indent=2)+'\n',encoding='utf-8')
print('PASS host tool compile/default/synthetic-release-denial; deviceCalls=0')
