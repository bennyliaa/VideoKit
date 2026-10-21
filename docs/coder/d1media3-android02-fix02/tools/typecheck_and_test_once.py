from pathlib import Path
import datetime,hashlib,json,os,subprocess,time
B=Path(__file__).resolve().parents[1];D=B/'evidence/typed-001';D.mkdir(exist_ok=False);C=D/'classes';C.mkdir();J=Path('D:/Android/Android Studio/jbr/bin');SDK=Path('D:/Android/SDK/platforms/android-36.1/android.jar');deadline=time.monotonic()+30
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources=sorted(p for n in ['src','android','upstream','instrumentation'] for p in (B/n).rglob('*.java'))+[B/'tools/TypedFix02Check.java',B/'tools/VerifyApk.java']
deps=sorted((B/'deps').glob('*.jar'))+[B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar'];cp=';'.join(map(str,[SDK]+deps));args=D/'source.args';args.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources),encoding='utf-8')
dump(D/'source-pins.json',[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources]);dump(D/'dependency-pins.json',[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [SDK]+deps])
env=os.environ.copy()
for k in ['JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','JDK_JAVA_OPTIONS','CLASSPATH']:env.pop(k,None)
def run(name,argv):
 owner={'argv':argv,'startUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wholeWindowSeconds':30,'originalProcessReturned':False,'killInterruptRetry':0,'actualAndroidOrMediaRuntime':0};path=D/(name+'-owner.json');dump(path,owner)
 with (D/(name+'.stdout')).open('xb') as out,(D/(name+'.stderr')).open('xb') as err:
  p=subprocess.Popen(argv,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False);owner['pid']=p.pid;dump(path,owner)
  try:code=p.wait(max(1,deadline-time.monotonic()))
  except subprocess.TimeoutExpired:owner['status']='UNKNOWN_ORIGINAL_RETURN_PENDING';dump(path,owner);raise SystemExit('UNKNOWN no kill/retry; original retained')
 owner.update(exitCode=code,originalProcessReturned=True,captureHandlesClosed=True,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(path,owner);print(name,'exit',code);assert code==0,(D/(name+'.stderr')).read_text()
run('compile',[str(J/'javac.exe'),'-J-Xmx256m','-J-XX:-UsePerfData','--release','11','-g','-encoding','UTF-8','-proc:none','-cp',cp,'-d',str(C),'@'+str(args)])
run('typed',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-cp',str(C),'TypedFix02Check'])
text=(D/'typed.stdout').read_text();assert 'DONE typedFix02Cases=' in text;print(text[-1800:]);dump(D/'result.json',{'status':'PASS_TYPED_FIVE_FIX_STATE_AND_ORDER_ONLY','typedCases':int(text.split('DONE typedFix02Cases=')[1].split()[0]),'AndroidFullSourceTypecheck':True,'payloadBytesUnder':65536,'actualAndroidOsOrMatureMuxer':False,'wholeWindowReturnedWithin30s':time.monotonic()<deadline,'sameOriginalThreadsJoined':'sameOriginalThreadsJoined=true' in text})
