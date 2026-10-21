from pathlib import Path
import subprocess,json,hashlib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1render02';S=R/'docs/coder/d1render01';D=B/'evidence/review-baseline';D.mkdir(exist_ok=False)
files=sorted((S/'src').rglob('*.java'))+[S/'android/com/videokit/d1present/PlatformRenderer.java']+sorted((B/'review-regression').rglob('*.java'))
for n in ['AsyncReadBridge','LeaseRegistry','HostFixtures','SourceAdmission']:files.append(S/'upstream/com/videokit/spike/c14'/f'{n}.java')
for n in ['E13SourceGroup','E13FinishOwner','E13ReturnEvents','E13Stages']:files.append(S/'upstream/com/videokit/spike/e4'/f'{n}.java')
(D/'source-pins.json').write_text(json.dumps([{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],indent=2),encoding='utf-8')
args=D/'javac.args';args.write_text('\n'.join('"'+str(p).replace('\\','/')+'"' for p in files),encoding='utf-8');C=D/'classes';C.mkdir();J=Path('D:/Android/Android Studio/jbr/bin')
for name,argv in [('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-d',str(C),'@'+str(args)]),('run',[str(J/'java.exe'),'-cp',str(C),'com.videokit.d1present.IndependentReviewCheck'])]:
 r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(D/(name+'.stdout')).write_bytes(r.stdout);(D/(name+'.stderr')).write_bytes(r.stderr);(D/(name+'.json')).write_text(json.dumps({'argv':argv,'exitCode':r.returncode,'originalProcessReturned':True},indent=2),encoding='utf-8');print(r.stdout.decode('utf-8',errors='replace'));print(r.stderr.decode('utf-8',errors='replace'));assert r.returncode==0
