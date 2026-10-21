"""Affected actual new Gradle public methods with SDK stubs only, plus source-level runner hook audit."""
import hashlib,json,pathlib,subprocess
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];J=pathlib.Path('D:/Android/Android Studio/jbr/bin');SDK=pathlib.Path('D:/Android/SDK/platforms/android-36.1/android.jar');app=B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';support=B/'.selfcheck/activation-002/classes';work=B/'.selfcheck/sdk-public-001';work.mkdir(parents=True,exist_ok=False);out=B/'evidence/sdk-public';out.mkdir(exist_ok=False);cp=str(app)+';'+str(support)+';'+str(SDK);commands=[]
def run(label,args):
 argv=[str(x) for x in args];commands.append(dict(label=label,argv=argv))
 with (out/(label+'.stdout.txt')).open('xb') as stdout,(out/(label+'.stderr.txt')).open('xb') as stderr:p=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=30)
 print(label,p.returncode,flush=True)
 if p.returncode:print((out/(label+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));raise SystemExit(p.returncode)
run('compile',[J/'javac.exe','-encoding','UTF-8','-cp',cp,'-d',work,B/'tools/E11PublicEntryCheck.java']);run('actual-public',[J/'java.exe','-cp',str(work)+';'+cp,'com.videokit.spike.e4.E11PublicEntryCheck',work/'fixture',B/'reference'])
source=B/'app/src/androidTest/java/com/videokit/spike/e4/E11ActivationInstrumentation.java';text=source.read_text();assert 'E11Selection.require(selected);super.onCreate(args);' in text and 'if(!E11ActivationLifetime.canFinish())' in text
finish=text.split('@Override public void finish',1)[1].split('@Override public boolean onException',1)[0];assert finish.index('E5AAdmission.invalidateCurrent()')<finish.index('E11ActivationLifetime.canFinish()')<finish.index('super.finish(')
rows=[]
for p in [B/'tools/E11PublicEntryCheck.java',source,SDK]+sorted(app.rglob('*.class')):
 raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/public-android-entry-check.json').write_text(json.dumps(dict(schema=1,status='PASS',commands=commands,inputs=rows,scope='Actual new Gradle app public guard methods under SDK stubs plus current metadata platform substitute; runner finish hook static/compile+used lifetime gate only; Android runner execution NOT_RUN',legacyPreparePairRejected=True,liveProofRequired=True,runtimeFailureRevokes=True,runnerHookStaticAudit=True,deviceCalls=0),indent=2)+'\n',encoding='utf-8')
