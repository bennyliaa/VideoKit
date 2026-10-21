from pathlib import Path
import hashlib,json,subprocess
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink02';S=R/'docs/coder/d1input-sink01';D=B/'evidence/old-five-scenarios';D.mkdir(exist_ok=False);C=D/'classes';C.mkdir();J=Path('D:/Android/Android Studio/jbr/bin')
sources=[S/'checks/com/videokit/d1input/InputSinkCheck.java',B/'reference/IndependentBoundaryCheck.java']+list((S/'platform-fixtures').rglob('*.java'))
cp=str(S/'artifacts/input-sink01-classes.jar')+';'+str(C)+';'+';'.join(str(p) for p in sorted((S/'deps').glob('*.jar')))
(D/'source-pins.json').write_text(json.dumps([{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],indent=2),encoding='utf-8')
for name,argv in [('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),*map(str,sources)]),('reproduce',[str(J/'java.exe'),'-Xmx256m','-cp',cp,'com.videokit.d1input.IndependentBoundaryCheck'])]:
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(D/(name+'.stdout')).write_bytes(p.stdout);(D/(name+'.stderr')).write_bytes(p.stderr);(D/(name+'.json')).write_text(json.dumps({'argv':argv,'exitCode':p.returncode,'originalProcessReturned':True,'deliveredOldJarFirst':True},indent=2),encoding='utf-8');print(p.stdout.decode('utf-8',errors='replace'));print(p.stderr.decode('utf-8',errors='replace'));assert p.returncode==0
