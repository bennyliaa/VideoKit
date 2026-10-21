from pathlib import Path
import subprocess,json,hashlib,datetime,sys
B=Path(__file__).resolve().parents[1]
J=Path('D:/Android/Android Studio/jbr/bin')
E=B/'evidence'; E.mkdir(exist_ok=True)
run=E/('local-'+(sys.argv[1] if len(sys.argv)>1 else '001'));run.mkdir(exist_ok=False)
sources=sorted((B/'src').rglob('*.java'))+sorted((B/'checks').rglob('*.java'))
for name in ['AsyncReadBridge','LeaseRegistry','HostFixtures','SourceAdmission']:
    sources.append(B/'upstream/com/videokit/spike/c14'/f'{name}.java')
for name in ['E13SourceGroup','E13FinishOwner','E13ReturnEvents','E13Stages']:
    sources.append(B/'upstream/com/videokit/spike/e4'/f'{name}.java')
pins=[{'path':p.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]
(run/'source-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
classes=run/'classes';classes.mkdir()
args=run/'javac.args';args.write_text('\n'.join('"'+str(p).replace('\\','/')+'"' for p in sources),encoding='utf-8')
def call(name,argv):
    at=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (run/(name+'.stdout')).write_bytes(r.stdout);(run/(name+'.stderr')).write_bytes(r.stderr)
    (run/(name+'.receipt.json')).write_text(json.dumps({'argv':list(map(str,argv)),'start_utc':at,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'stdout_bytes':len(r.stdout),'stderr_bytes':len(r.stderr),'original_process_returned':True},indent=2),encoding='utf-8')
    print(r.stdout.decode('utf-8',errors='replace'));print(r.stderr.decode('utf-8',errors='replace'))
    if r.returncode:raise SystemExit(r.returncode)
call('compile',[str(J/'javac.exe'),'-encoding','UTF-8','--release','11','-d',str(classes),'@'+str(args)])
call('core',[str(J/'java.exe'),'-Xmx256m','-cp',str(classes),'com.videokit.d1present.LocalSelfCheck',str(run/'generated-pcm16.raw')])
print('LOCAL_CORE_COMPLETE; Android device operations=0')
