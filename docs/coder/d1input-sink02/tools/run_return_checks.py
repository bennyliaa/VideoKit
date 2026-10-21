from pathlib import Path
import subprocess,json,sys,datetime,hashlib
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/input-sink02-freeze.json').exists(),'FROZEN';attempt=sys.argv[1];local=sys.argv[2];D=B/'evidence'/('return-'+attempt);D.mkdir(exist_ok=False)
C=B/'evidence'/('local-'+local)/'classes';J=Path('D:/Android/Android Studio/jbr/bin');jarFirst='--production-jar-first' in sys.argv
parts=([B/'artifacts/input-sink02-classes.jar'] if jarFirst else [])+[C]+sorted((B/'deps').glob('*.jar'));cp=';'.join(map(str,parts))
argv=[str(J/'java.exe'),'-Xmx256m','-cp',cp,'com.videokit.d1input.ReturnBoundaryCheck'];start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(D/'run.stdout').write_bytes(r.stdout);(D/'run.stderr').write_bytes(r.stderr)
(D/'run.json').write_text(json.dumps({'argv':argv,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':r.returncode,'originalProcessReturned':True,'productionJarFirst':jarFirst,'jarSha256':hashlib.sha256(parts[0].read_bytes()).hexdigest() if jarFirst else None,'sourcePins':f'evidence/local-{local}/source-pins.json'},indent=2),encoding='utf-8')
print(r.stdout.decode('utf-8',errors='replace'));print(r.stderr.decode('utf-8',errors='replace'));assert r.returncode==0
