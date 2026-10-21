"""Final actual Gradle classes, SDK-stub public-entry and failed runtime-grant revocation checks only."""
import hashlib,json,pathlib,subprocess
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];jdk=pathlib.Path('D:/Android/Android Studio/jbr/bin');sdk=pathlib.Path('D:/Android/SDK/platforms/android-36.1/android.jar');app=B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';support=B/'.selfcheck/final-pc-007/classes';work=B/'.selfcheck/android-entry-001';work.mkdir(parents=True,exist_ok=False);out=B/'evidence/android-entry';out.mkdir(parents=True,exist_ok=False)
source=[B/'tools/E9PublicAndroidEntryCheck.java',B/'tools/E9ARuntimeGrantCheck.java'];cp=str(app)+';'+str(support)+';'+str(sdk);commands=[]
def run(name,args):
 argv=[str(x) for x in args];result=subprocess.run(argv,capture_output=True,timeout=30);(out/(name+'.stdout.txt')).write_bytes(result.stdout);(out/(name+'.stderr.txt')).write_bytes(result.stderr);commands.append(dict(name=name,argv=argv,exitCode=result.returncode));print(name,result.returncode)
 if result.returncode:print(result.stderr.decode('utf-8',errors='replace'));raise SystemExit(result.returncode)
run('compile',[jdk/'javac.exe','-encoding','UTF-8','-cp',cp,'-d',work,*source]);run('public-six',[jdk/'java.exe','-cp',str(work)+';'+cp,'com.videokit.spike.e4.E9PublicAndroidEntryCheck']);run('runtime-invalidation',[jdk/'java.exe','-cp',str(work)+';'+cp,'com.videokit.spike.e4.E9ARuntimeGrantCheck',work/'runtime',B/'reference'])
inputs=[]
for p in source+[sdk]+sorted(app.rglob('*.class')):
 raw=p.read_bytes();inputs.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/public-android-entry-check.json').write_text(json.dumps(dict(schema=1,status='PASS',publicEntries=6,runtimeGrantInvalidationSequence=1,commands=commands,inputs=inputs,scope='actual new Gradle classes; SDK stubs and synthetic shared metadata only, no Android runtime',deviceCalls=0),indent=2)+'\n',encoding='utf-8')
