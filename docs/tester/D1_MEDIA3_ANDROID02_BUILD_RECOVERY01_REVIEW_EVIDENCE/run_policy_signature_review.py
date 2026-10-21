from pathlib import Path
import datetime,hashlib,json,os,subprocess,time,xml.etree.ElementTree as ET
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-android02-recovery01';E=Path(__file__).resolve().parent;D=E/'policy-signatures-001'
assert not D.exists();D.mkdir();C=D/'classes';C.mkdir();J=Path('D:/Android/Android Studio/jbr/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';prod=B/'artifacts/media3-android02-recovery01-classes.jar'
nodes=[c for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter() if c.tag.split('}')[-1]=='component' and c.get('group')=='com.android.tools.build' and c.get('name')=='apksig'];assert len(nodes)==1 and any(h.get('value')==sha(sig) for a in nodes[0] for h in a)
sources=[B/'tools/RecoveryPolicyCheck.java',B/'tools/VerifyApk.java'];apks=[B/'artifacts/media3-android02-recovery01-app-debug.apk',B/'artifacts/media3-android02-recovery01-test-debug.apk',B/'evidence/build-001/before-stage-a/app.apk',B/'evidence/build-001/before-stage-a/test.apk'];deps=sorted((B/'deps').glob('*.jar'));inputs=sources+[prod,sig]+apks+deps
pins=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs];save('input-pins.json',pins)
cp=';'.join(map(str,[prod,sig]+deps));env=os.environ.copy()
for k in ['JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','JDK_JAVA_OPTIONS','JAVA_OPTS','GRADLE_OPTS','CLASSPATH']:env.pop(k,None)
start=time.monotonic();deadline=start+30
def run(name,argv):
 owner={'argv':argv,'startUtc':now(),'heapMiB':256,'wholeWindowSeconds':30,'originalProcessReturned':False,'captureHandlesClosed':False,'killInterruptRetry':0,'AndroidMediaGradleDeviceOperations':0};save(name+'-owner.json',owner)
 with (D/(name+'.stdout')).open('xb') as out,(D/(name+'.stderr')).open('xb') as err:
  p=subprocess.Popen(argv,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False);owner['pid']=p.pid;save(name+'-owner.json',owner)
  try:code=p.wait(max(.001,deadline-time.monotonic()))
  except subprocess.TimeoutExpired:
   owner.update(status='UNKNOWN_ORIGINAL_RETURN_PENDING',observationEndUtc=now());save(name+'-owner.json',owner)
   # Retain the exact original process and files. Never kill, relaunch, or dispatch another tool.
   p.wait();owner.update(lateOriginalReturn=True,exitCode=p.returncode);save(name+'-owner.json',owner);raise SystemExit('Late return; no later task')
 owner.update(exitCode=code,originalProcessReturned=True,captureHandlesClosed=True,endUtc=now(),elapsedWholeSeconds=time.monotonic()-start,stdoutBytes=(D/(name+'.stdout')).stat().st_size,stderrBytes=(D/(name+'.stderr')).stat().st_size);save(name+'-owner.json',owner)
 assert code==0 and owner['elapsedWholeSeconds']<30 and owner['stdoutBytes']<=65536 and owner['stderrBytes']<=65536,owner
run('compile',[str(J/'javac.exe'),'-J-Xmx256m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C)]+list(map(str,sources)))
run('verify',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-cp',str(C)+';'+cp,'RecoveryPolicyCheck']+list(map(str,apks)))
out=(D/'verify.stdout').read_text();assert out.count('PASS ')==17 and 'DONE recoveryPolicyCases=17' in out and out.count('v2=true certificateSha256=5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f')==4
assert str(prod.as_uri()) in out or 'media3-android02-recovery01-classes.jar' in out
assert all(sha(Path(x['path']))==x['sha256'] for x in pins)
result={'status':'PASS_LIMITED_17_PUBLIC_POLICY_AND_FOUR_REAL_APK_SIGNATURES','policyCases':17,'signatureApks':4,'heapMiB':256,'totalElapsedSeconds':time.monotonic()-start,'productionJarFirst':str(prod),'productionJarSha256':sha(prod),'sameInputsAfter':True,'AndroidExperimentJobMediaRuntime':'NOT_RUN','newTesterPolicyHelperRuns':0,'workerOrFinalizerNativeReturnProof':'NOT_PROVEN_BY_THIS_JVM'};save('result.json',result);print(json.dumps(result))
