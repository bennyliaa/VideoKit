from pathlib import Path
import subprocess,json,datetime,hashlib,sys
R=Path('D:/CodexProjects/VideoKit'); E=R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE'; B=R/'docs/coder/d1input-sink01'
J=Path('D:/Android/Android Studio/jbr/bin'); C=E/'independent-001/classes'
cp=';'.join([str(C)]+[str(p) for p in sorted((B/'deps').glob('*.jar'))])
if '--delivered-jar-first' in sys.argv:cp=str(B/'artifacts/input-sink01-classes.jar')+';'+cp
for name,args in [('independent-compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(E/'IndependentBoundaryCheck.java')]),('independent-boundaries',[str(J/'java.exe'),'-Xmx256m','-cp',cp,'com.videokit.d1input.IndependentBoundaryCheck'])]:
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 stem=name;i=1
 while (E/(stem+'.json')).exists():stem=name+'-'+str(i);i+=1
 (E/(stem+'.stdout')).write_bytes(p.stdout);(E/(stem+'.stderr')).write_bytes(p.stderr)
 (E/(stem+'.json')).write_text(json.dumps(dict(argv=args,startedUtc=start,exitCode=p.returncode,originalProcessReturned=True),indent=2),encoding='utf8')
 print(name,p.returncode,p.stdout.decode('utf8','replace'),p.stderr.decode('utf8','replace'))
 if p.returncode:raise SystemExit(p.returncode)
