from pathlib import Path
import subprocess,json,datetime,hashlib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink04';E=Path(__file__).resolve().parent;C=E/'independent-001/source/classes';J=Path('D:/Android/Android Studio/jbr/bin');cp=';'.join([str(C)]+[str(p) for p in sorted((B/'deps').glob('*.jar'))]);jar=B/'artifacts/input-sink04-classes.jar'
def run(name,args):
 stem=name;i=1
 while (E/(stem+'.json')).exists():stem=name+'-'+str(i);i+=1
 name=stem
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45);(E/(name+'.stdout')).write_bytes(p.stdout);(E/(name+'.stderr')).write_bytes(p.stderr);(E/(name+'.json')).write_text(json.dumps(dict(argv=args,startUtc=start,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=p.returncode,originalProcessReturned=True,productionJarSha256=hashlib.sha256(jar.read_bytes()).hexdigest()),indent=2),encoding='utf8');print(name,p.returncode,p.stdout.decode('utf8','replace')[-2200:],p.stderr.decode('utf8','replace'));assert p.returncode==0
run('independent-compile-final',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(E/'IndependentLateReadyCheck.java')])
for mode in ['source','production']:
 for case in ['CONTRADICTORY_ABORTED','NORMAL_QUERY_READY']:run('late-ready-'+case.lower()+'-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',(str(jar)+';' if mode=='production' else '')+cp,'com.videokit.d1input.IndependentLateReadyCheck',case])
