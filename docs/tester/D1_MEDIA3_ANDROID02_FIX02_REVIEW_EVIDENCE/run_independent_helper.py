from pathlib import Path
import datetime,hashlib,json,os,re,subprocess,time,xml.etree.ElementTree as ET
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-android02-fix02';E=Path(__file__).resolve().parent;D=E/'typed-signatures-001';assert not D.exists();D.mkdir();C=D/'classes';C.mkdir();J=Path('D:/Android/Android Studio/jbr/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';prod=B/'artifacts/media3-android02-fix02-classes.jar';src=E/'IndependentFix02Check.java'
assert prod.stat().st_size==150394 and sha(prod)=='f246fff1e4faebbc05279283f47ca264523b4bf87ff1491c198c814352b1719c'
nodes=[c for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter() if c.tag.split('}')[-1]=='component' and c.get('group')=='com.android.tools.build' and c.get('name')=='apksig'];assert len(nodes)==1 and any(h.get('value')==sha(sig) for a in nodes[0] for h in a)
old=R/'docs/coder/d1media3-android02-recovery01';apks=[B/f'artifacts/media3-android02-fix02-{k}-debug.apk' for k in ['app','test']]+[old/f'artifacts/media3-android02-recovery01-{k}-debug.apk' for k in ['app','test']];deps=sorted((B/'deps').glob('*.jar'));inputs=[src,prod,sig]+apks+deps;rows=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs];save('input-pins.json',rows)
cp=';'.join(map(str,[prod,sig]+deps));env=os.environ.copy()
for k in ['JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','JDK_JAVA_OPTIONS','JAVA_OPTS','GRADLE_OPTS','CLASSPATH']:env.pop(k,None)
start=time.monotonic();deadline=start+30
def run(name,argv):
 owner={'argv':argv,'startUtc':now(),'heapMiB':256,'wholeWindowSeconds':30,'originalProcessReturned':False,'captureHandlesClosed':False,'killInterruptRetry':0,'AndroidMediaGradleDeviceOperations':0};save(name+'-owner.json',owner)
 with (D/(name+'.stdout')).open('xb') as out,(D/(name+'.stderr')).open('xb') as err:
  p=subprocess.Popen(argv,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False);owner['pid']=p.pid;save(name+'-owner.json',owner)
  try:code=p.wait(max(.001,deadline-time.monotonic()))
  except subprocess.TimeoutExpired:
   owner.update(status='UNKNOWN_ORIGINAL_RETURN_PENDING',observationEndUtc=now());save(name+'-owner.json',owner);p.wait();owner.update(lateOriginalReturn=True,exitCode=p.returncode);save(name+'-owner.json',owner);raise SystemExit('Late original retained; no subsequent task')
 owner.update(exitCode=code,originalProcessReturned=True,captureHandlesClosed=True,endUtc=now(),elapsedWholeSeconds=time.monotonic()-start,stdoutBytes=(D/(name+'.stdout')).stat().st_size,stderrBytes=(D/(name+'.stderr')).stat().st_size);save(name+'-owner.json',owner)
 assert code==0 and owner['elapsedWholeSeconds']<30 and owner['stdoutBytes']<=65536 and owner['stderrBytes']<=65536,owner
run('compile',[str(J/'javac.exe'),'-J-Xmx256m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(src)])
run('typed',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-cp',str(C)+';'+cp,'IndependentFix02Check']+list(map(str,apks)))
out=(D/'typed.stdout').read_text();m=re.search(r'DONE independentGroups=(\d+) typedPayloadUtf8Bytes=(\d+)',out);assert m and int(m[1])==46 and int(m[2])<=65536 and out.count('PASS ')==46 and out.count('v2=true certificateSha256=5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f')==4
assert all(sha(Path(x['path']))==x['sha256'] for x in rows)
result={'status':'PASS_46_INDEPENDENT_FINITE_GROUPS_FINAL_PRODUCTION_JAR','totalGroups':46,'typedAndPolicyGroups':45,'signatureGroup':1,'realApkSignatures':4,'payloadUtf8Bytes':int(m[2]),'heapMiB':256,'wholeSeconds':time.monotonic()-start,'sameOriginalThreadsJoined':True,'allInputsUnchanged':True,'finalProductionJarSha256':sha(prod),'actualAndroidOsExperimentJobMedia3Muxer':'NOT_RUN'};save('result.json',result);print(json.dumps(result))
