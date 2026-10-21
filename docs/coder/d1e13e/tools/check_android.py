from pathlib import Path
import subprocess,json,hashlib,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];J=Path('D:/Android/Android Studio/jbr/bin');attempt=sys.argv[1];E=B/'evidence'/attempt;W=B/'.checks'/attempt;E.mkdir(exist_ok=False);W.mkdir(parents=True,exist_ok=False)
sources=[p for p in sorted((B/'checks/platform-substitutes').rglob('*.java')) if p.name!='E4CodecWire.java']+sorted((B/'binding').rglob('*.java'))+[B/'src/com/videokit/spike/e4/E4Protocol.java',B/'android/com/videokit/spike/e4/E4CodecWire.java',B/'android/com/videokit/spike/e4/E13PermissionProbe.java',B/'fixture/src/main/java/com/videokit/e13/sender/SenderService.java',B/'app/src/androidTest/java/com/videokit/spike/e4/E13Instrumentation.java',B/'checks/E13EAndroidCheck.java',B/'checks/E13EProtocolCheck.java']
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
write(E/'inputs.json',[pin(p) for p in sources]);arg=E/'compile.args';arg.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources));cmds=[]
def run(name,args):
 argv=[str(x) for x in args];cmds.append(dict(name=name,argv=argv));write(E/'commands.json',cmds)
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(argv,stdout=so,stderr=se);code=p.wait(timeout=45)
 write(E/(name+'.exit.json'),dict(pid=p.pid,exitCode=code,naturalReturn=True));assert code==0,(name,(E/(name+'.stderr.txt')).read_text());print(name,'PASS',flush=True)
run('compile',[J/'javac.exe','-encoding','UTF-8','-d',W,'@'+str(arg)])
modes=['CALLBACK_PASS','CALLBACK_FAILED','PROBE_FULL','FIXTURE_UNKNOWN','FIXTURE_IDENTITY','RUNNER_EXCEPTION','RUNNER_RESULT_UNKNOWN','WAKE_BEFORE','WAKE_DURING','WAKE_AFTER_CHECK','WAKE_EXIT_WINDOW','WAKE_UNKNOWN']
if len(sys.argv)<3:
 for mode in modes:run(mode,[J/'java.exe','-cp',W,'com.videokit.spike.e4.E13EAndroidCheck',mode])
protocols=['LATE_SNAPSHOT','STAGE_BOUND','BIND_PENDING','HELLO_PENDING','FIXTURE_PENDING','UNBIND_PENDING']
for mode in protocols:run(mode,[J/'java.exe','-cp',W,'com.videokit.spike.e4.E13EProtocolCheck',mode])
write(E/'results.json',dict(status='PASS_E13E_ACTUAL_ANDROID_ADAPTER_JVM_CHECKS',modes=(modes if len(sys.argv)<3 else [])+protocols,actualProbeSenderRunnerAndOwner=True,platformAndBaseRunner='FINITE_JVM_SUBSTITUTES_ONLY',monitorConstraint='matches cached monitor1.8.0 source; actual Android monitor execution NOT_RUN',deviceCalls=0))
