from pathlib import Path
import subprocess,json,datetime,hashlib
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/input-sink02-freeze.json').exists(),'FROZEN';D=B/'evidence/production-core-001';D.mkdir(exist_ok=False)
jar=B/'artifacts/input-sink02-classes.jar';C=B/'evidence/local-003/classes';J=Path('D:/Android/Android Studio/jbr/bin')
cp=';'.join(map(str,[jar,C]+sorted((B/'deps').glob('*.jar'))));argv=[str(J/'java.exe'),'-Xmx256m','-cp',cp,'com.videokit.d1input.InputSinkCheck',str(D)]
start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(D/'run.stdout').write_bytes(r.stdout);(D/'run.stderr').write_bytes(r.stderr)
(D/'run.json').write_text(json.dumps({'argv':argv,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':r.returncode,'originalProcessReturned':True,'productionJarFirst':True,'jarSha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'sourcePins':'evidence/local-003/source-pins.json'},indent=2),encoding='utf-8')
print(r.stdout.decode('utf-8',errors='replace'));print(r.stderr.decode('utf-8',errors='replace'));assert r.returncode==0 and b'groups=20' in r.stdout
