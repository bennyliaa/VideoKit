from pathlib import Path
import subprocess,json,datetime,hashlib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink05';E=Path(__file__).resolve().parent;C=E/'independent-001/source/classes';J=Path('D:/Android/Android Studio/jbr/bin');jar=B/'artifacts/input-sink05-classes.jar';cp=';'.join([str(C)]+[str(p) for p in sorted((B/'deps').glob('*.jar'))])
def run(name,args):
 stem=name;i=1
 while (E/(stem+'.json')).exists():stem=name+'-'+str(i);i+=1
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40);(E/(stem+'.stdout')).write_bytes(p.stdout);(E/(stem+'.stderr')).write_bytes(p.stderr);(E/(stem+'.json')).write_text(json.dumps(dict(argv=args,startUtc=start,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=p.returncode,originalProcessReturned=True,productionJarSha256=hashlib.sha256(jar.read_bytes()).hexdigest()),indent=2),encoding='utf8');print(stem,p.returncode,p.stdout.decode('utf8','replace')[-2300:],p.stderr.decode('utf8','replace'));assert p.returncode==0
run('independent-compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(E/'IndependentResponseOrderCheck.java')])
for mode in ['source','production']:run('independent-orders-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',(str(jar)+';' if mode=='production' else '')+cp,'com.videokit.d1input.IndependentResponseOrderCheck'])
