from pathlib import Path
import subprocess,json,datetime,sys,hashlib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink02';E=Path(__file__).resolve().parent;C=E/'independent-001/classes';J=Path('D:/Android/Android Studio/jbr/bin')
cp=';'.join([str(C)]+[str(p) for p in sorted((B/'deps').glob('*.jar'))]);prod=str(B/'artifacts/input-sink02-classes.jar')+';'+cp
def run(name,args):
 stem=name;i=1
 while (E/(stem+'.json')).exists():stem=name+'-'+str(i);i+=1
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=50)
 (E/(stem+'.stdout')).write_bytes(p.stdout);(E/(stem+'.stderr')).write_bytes(p.stderr)
 (E/(stem+'.json')).write_text(json.dumps(dict(argv=args,startUtc=start,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=p.returncode,originalProcessReturned=True,productionJarSha256=hashlib.sha256((B/'artifacts/input-sink02-classes.jar').read_bytes()).hexdigest()),indent=2),encoding='utf8')
 print(stem,'exit',p.returncode,p.stdout.decode('utf8','replace')[-3500:],p.stderr.decode('utf8','replace')[-1500:]);assert p.returncode==0
run('tester-compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(E/'IndependentFixCheck.java'),str(E/'CancellationAckCheck.java'),str(E/'AbortHistoryCheck.java')])
for mode,path in [('source',cp),('production',prod)]:
 if '--history-only' not in sys.argv:
  run('tester-independent-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',path,'com.videokit.d1input.IndependentFixCheck'])
  run('coder-boundaries-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',path,'com.videokit.d1input.ReturnBoundaryCheck'])
  for phase in ['WRITE','FLUSH','CLOSE','REOPEN','VALIDATE','COMMIT']:
   run('cancelled-'+phase.lower()+'-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',path,'com.videokit.d1input.CancellationAckCheck',phase])
 for phase in ['ABORT','QUERY','ABORT_ERROR']:
  run('history-'+phase.lower()+'-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',path,'com.videokit.d1input.AbortHistoryCheck',phase])
