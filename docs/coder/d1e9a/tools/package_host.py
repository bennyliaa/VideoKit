"""Freeze only the production host classes already compiled/tested in frame-validation-008; no recompile."""
import hashlib,json,pathlib,re,subprocess,zipfile
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];classes=B/'.selfcheck/frame-validation-008/classes';production=[]
for folder in ['src','upstream-c14/src']:production+=list((B/folder).rglob('*.java'))
production += [B/'tools'/n for n in ['E9PcSupervisor.java','E9PcClient.java','E9HostDeployment.java','E9HostManager.java','E9HostActivationSession.java','E9ActivationPolicyExport.java']]
allowed={}
for source in production:
 text=source.read_text(encoding='utf-8-sig');package=re.search(r'package\s+([\w.]+);',text).group(1);allowed[package.replace('.','/')+'/'+source.stem]=source
artifact=B/'artifacts/D1-20261018-E9A/final/e9a-host-tools.jar';artifact.parent.mkdir(parents=True,exist_ok=True);rows=[]
with zipfile.ZipFile(artifact,'x',compression=zipfile.ZIP_DEFLATED) as jar:
 for p in sorted(classes.rglob('*.class')):
  name=p.relative_to(classes).as_posix();top=name[:-6].split('$')[0]
  if top not in allowed:continue
  raw=p.read_bytes();jar.writestr(name,raw);source=allowed[top];rows.append(dict(entry=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),classMajor=int.from_bytes(raw[6:8],'big'),source=str(source.relative_to(R)).replace('\\','/'),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest()))
unchanged=[]
for x in rows:
 if x['entry'].split('$')[0].removesuffix('.class') not in ['com/videokit/spike/e4/E9HostManager','com/videokit/spike/e4/E9HostDeployment']:
  previous=B/'.selfcheck/final-pc-007/classes'/x['entry'];assert previous.read_bytes()==(classes/x['entry']).read_bytes(),x['entry'];unchanged.append(x['entry'])
assert rows and not any('ProductionCheck' in r['entry'] or 'TestFiles' in r['entry'] or 'SelfCheck' in r['entry'] for r in rows)
logs=B/'evidence/host-binary';logs.mkdir(exist_ok=False);commands=[]
for name in ['E9HostManager','E9HostActivationSession','E9PcClient']:
 args=['D:/Android/Android Studio/jbr/bin/java.exe','-cp',str(artifact),'com.videokit.spike.e4.'+name];p=subprocess.run(args,capture_output=True,timeout=10);(logs/(name+'.stdout.txt')).write_bytes(p.stdout);(logs/(name+'.stderr.txt')).write_bytes(p.stderr);commands.append(dict(argv=args,exitCode=p.returncode));assert p.returncode==0 and b'INSPECT_ONLY' in p.stdout
raw=artifact.read_bytes();(B/'evidence/host-binary-provenance.json').write_text(json.dumps(dict(schema=1,status='PASS',artifact=dict(path=str(artifact.relative_to(R)).replace('\\','/'),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),productionClasses=rows,compiledBy='frame-validation-008 targeted javac current production inputs; no package recompile',testClassesIncluded=False,unchangedLifetimeAndSharedClassBytes=unchanged,defaultModeCommands=commands,deviceCalls=0),indent=2)+'\n',encoding='utf-8');print('PASS production host JAR classes',len(rows),'no test classes/no device calls')
