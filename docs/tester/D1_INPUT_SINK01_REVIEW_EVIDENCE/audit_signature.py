from pathlib import Path
import subprocess,json,hashlib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink01';E=Path(__file__).resolve().parent
J=Path('D:/Android/Android Studio/jbr/bin');jar=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';D=E/'signature-classes';D.mkdir(exist_ok=False)
commands=[[str(J/'javac.exe'),'--release','11','-cp',str(jar),'-d',str(D),str(E/'VerifySignature.java')],[str(J/'java.exe'),'-cp',str(D)+';'+str(jar),'VerifySignature',str(B/'artifacts/input-sink01-compile-probe-debug.apk')]]
for i,args in enumerate(commands):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 (E/('signature-'+str(i)+'.stdout')).write_bytes(p.stdout);(E/('signature-'+str(i)+'.stderr')).write_bytes(p.stderr)
 (E/('signature-'+str(i)+'.json')).write_text(json.dumps(dict(argv=args,exitCode=p.returncode,originalProcessReturned=True,SDKCommand=False,apksigJarSha256=hashlib.sha256(jar.read_bytes()).hexdigest()),indent=2),encoding='utf8')
 print(p.returncode,p.stdout.decode('utf8','replace'),p.stderr.decode('utf8','replace'));assert p.returncode==0
