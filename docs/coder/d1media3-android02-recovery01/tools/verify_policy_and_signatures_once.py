from pathlib import Path
import datetime,hashlib,json,subprocess,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parents[1];D=B/'evidence/policy-signatures-001';D.mkdir(exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin');C=D/'classes';C.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';nodes=[c for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter() if c.tag.split('}')[-1]=='component' and c.get('group')=='com.android.tools.build' and c.get('name')=='apksig'];assert len(nodes)==1 and any(h.get('value')==sha(sig) for a in nodes[0] for h in a)
sources=[B/'tools/VerifyApk.java',B/'tools/RecoveryPolicyCheck.java'];prod=B/'artifacts/media3-android02-recovery01-classes.jar';apks=[B/'artifacts/media3-android02-recovery01-app-debug.apk',B/'artifacts/media3-android02-recovery01-test-debug.apk',B/'evidence/build-001/before-stage-a/app.apk',B/'evidence/build-001/before-stage-a/test.apk'];cp=';'.join(map(str,[prod,sig]+sorted((B/'deps').glob('*.jar'))))
dump(D/'inputs.json',[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources+[prod,sig]+apks])
def run(name,argv,seconds):
 owner={'argv':argv,'startUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observationSeconds':seconds,'originalProcessReturned':False,'killInterruptRetry':0,'mediaDeviceOperations':0};out=D/(name+'-owner.json');dump(out,owner)
 with (D/(name+'.stdout')).open('xb') as stdout,(D/(name+'.stderr')).open('xb') as stderr:
  p=subprocess.Popen(argv,cwd=D,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,shell=False);owner['pid']=p.pid;dump(out,owner)
  try:code=p.wait(seconds)
  except subprocess.TimeoutExpired:owner['status']='UNKNOWN_ORIGINAL_RETURN_PENDING';dump(out,owner);raise SystemExit('UNKNOWN, no kill or retry')
 owner.update(exitCode=code,originalProcessReturned=True,captureHandlesClosed=True,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out,owner);assert code==0,(D/(name+'.stderr')).read_text();print(name,'exit',code)
run('compile',[str(J/'javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C)]+list(map(str,sources)),60)
run('verify',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-cp',str(C)+';'+cp,'RecoveryPolicyCheck']+list(map(str,apks)),30)
text=(D/'verify.stdout').read_text();assert text.count('certificateSha256=5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f')==4 and 'DONE recoveryPolicyCases=17' in text
dump(D/'result.json',{'status':'PASS_LIMITED_CHANGED_PUBLIC_POLICY_AND_REAL_APK_SIGNATURES_NOT_ANDROID_RUNTIME','policyCases':17,'apkSignaturesVerified':4,'certificateSha256':'5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f','finalProductionJarFirst':True,'finalProductionJarSha256':sha(prod),'sourceAndBinaryPinsUnchangedAfterRun':all(sha(Path(x['path']))==x['sha256'] for x in json.loads((D/'inputs.json').read_text())),'AndroidScopeRuntime':'NOT_RUN'})
print(text[-1300:])
