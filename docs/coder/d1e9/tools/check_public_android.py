"""SDK-stub phase-before-platform checks against final Gradle classes."""
import hashlib,json,pathlib,subprocess
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];jdk=pathlib.Path('D:/Android/Android Studio/jbr/bin');sdk=pathlib.Path('D:/Android/SDK/platforms/android-36.1/android.jar')
if not sdk.exists():sdk=pathlib.Path('D:/Android/SDK/platforms/android-36/android.jar')
classes=B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';work=B/'.selfcheck/public-android-001';work.mkdir(parents=True,exist_ok=False);e=B/'evidence/public-android-entry';e.mkdir(parents=True,exist_ok=False)
source=B/'tools/E9PublicAndroidEntryCheck.java';cp=str(classes)+';'+str(sdk)
for name,args in [('compile',[jdk/'javac.exe','-encoding','UTF-8','-cp',cp,'-d',work,source]),('run',[jdk/'java.exe','-cp',str(work)+';'+cp,'com.videokit.spike.e4.E9PublicAndroidEntryCheck'])]:
 r=subprocess.run([str(x) for x in args],capture_output=True,timeout=30);(e/(name+'.stdout.txt')).write_bytes(r.stdout);(e/(name+'.stderr.txt')).write_bytes(r.stderr);print(name,r.returncode)
 if r.returncode:print(r.stderr.decode(errors='replace'));raise SystemExit(r.returncode)
inputs=[]
for p in [source,sdk]+sorted(classes.rglob('*.class')):
 raw=p.read_bytes();inputs.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/public-android-entry-check.json').write_text(json.dumps(dict(schema=1,status='PASS',actualPublicEntries=6,inputs=inputs,scope='New final Gradle Android classes with SDK stubs; direct prepare phase rejection before platform calls',androidExecution='NOT_RUN',deviceCalls=0),indent=2)+'\n',encoding='utf-8')
