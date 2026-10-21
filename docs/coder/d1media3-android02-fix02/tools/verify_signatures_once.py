from pathlib import Path
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parents[1];D=B/'evidence/signatures-001';D.mkdir(exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin');sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';C=B/'evidence/typed-001/classes';apks=sorted((B/'artifacts').glob('*.apk'));assert len(apks)==2
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
nodes=[c for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter() if c.tag.split('}')[-1]=='component' and c.get('group')=='com.android.tools.build' and c.get('name')=='apksig'];assert len(nodes)==1 and any(h.get('value')==sha(sig) for a in nodes[0] for h in a)
dump(D/'inputs.json',[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in apks+[sig,C/'VerifyApk.class',B/'tools/VerifyApk.java']])
argv=[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-cp',str(C)+';'+str(sig),'VerifyApk']+list(map(str,apks));owner={'argv':argv,'startUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observationSeconds':30,'originalProcessReturned':False,'purpose':'Actual apksig signature inspection only, no typed/state test replay','killInterruptRetry':0,'deviceMediaOperations':0};path=D/'owner.json';dump(path,owner)
env=os.environ.copy()
for k in ['JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','JDK_JAVA_OPTIONS','CLASSPATH']:env.pop(k,None)
with (D/'stdout.raw').open('xb') as out,(D/'stderr.raw').open('xb') as err:
 p=subprocess.Popen(argv,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False);owner['pid']=p.pid;dump(path,owner)
 try:code=p.wait(30)
 except subprocess.TimeoutExpired:owner['status']='UNKNOWN_ORIGINAL_RETURN_PENDING';dump(path,owner);raise SystemExit('UNKNOWN no kill/retry')
owner.update(exitCode=code,originalProcessReturned=True,captureHandlesClosed=True,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(path,owner);assert code==0
text=(D/'stdout.raw').read_text();assert text.count('v2=true certificateSha256=5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f')==2
dump(D/'result.json',{'status':'PASS_REAL_TWO_APK_SIGNATURES_ONLY','apks':len(apks),'certificateSha256':'5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f','allInputsUnchanged':all(sha(Path(x['path']))==x['sha256'] for x in json.loads((D/'inputs.json').read_text()))});print(text)
