from pathlib import Path
import hashlib,json,subprocess,sys,datetime
B=Path(__file__).resolve().parents[1]
if sys.argv[1]=='--review-output':
 assert (B/'evidence/input-sink03-freeze.json').exists(),'FROZEN_REVIEW_ONLY';D=Path(sys.argv[2]).resolve();assert str(D).lower().startswith('d:\\codexprojects\\videokit\\docs\\tester\\d1_input_sink02_review_evidence\\'),'INDEPENDENT_TESTER_ROOT_ONLY'
else:
 assert not (B/'evidence/input-sink03-freeze.json').exists(),'FROZEN_USE_INDEPENDENT_REVIEW_OUTPUT';D=B/'evidence'/('local-'+sys.argv[1])
D.mkdir(parents=True,exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin')
sources=sorted(p for folder in ['src','upstream','checks','platform-fixtures'] for p in (B/folder).rglob('*.java'))
sources.append(B/'android/com/videokit/d1input/PlatformOutputErrors.java')
pins=[{'path':p.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources];(D/'source-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
classes=D/'classes';classes.mkdir();args=D/'javac.args';args.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources),encoding='utf-8')
cp=';'.join(p.as_posix() for p in (B/'deps').glob('*.jar'))
def run(name,argv):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(D/(name+'.stdout')).write_bytes(p.stdout);(D/(name+'.stderr')).write_bytes(p.stderr);(D/(name+'.json')).write_text(json.dumps({'argv':argv,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':p.returncode,'originalProcessReturned':True},indent=2),encoding='utf-8');print(p.stdout.decode('utf-8',errors='replace'));print(p.stderr.decode('utf-8',errors='replace'));assert p.returncode==0
run('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(classes),'@'+str(args)])
run('checks',[str(J/'java.exe'),'-Xmx256m','-cp',str(classes)+';'+cp,'com.videokit.d1input.InputSinkCheck',str(D)])
