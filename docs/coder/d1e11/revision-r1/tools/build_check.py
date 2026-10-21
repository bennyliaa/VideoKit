"""Host-only R1 compile, actual cross-process CREATE_NEW tests, then merged production JAR. No APK build/device."""
import hashlib,json,pathlib,subprocess,sys,time,zipfile
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[3];BASE=B.parent;J=pathlib.Path('D:/Android/Android Studio/jbr/bin');OLD=BASE/'artifacts/D1-20261018-E11/final/e11-host-tools.jar';out=B/'evidence/checks';out.mkdir(exist_ok=False);classes=B/'.classes';classes.mkdir(exist_ok=False);commands=[]
def row(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
sources=[B/'tools'/n for n in ['E11DeploymentOnce.java','E9HostActivationSession.java','OnceCheck.java']];save(out/'inputs.json',dict(baseJar=row(OLD),sources=[row(p) for p in sources]))
args=[str(J/'javac.exe'),'-encoding','UTF-8','-cp',str(OLD),'-d',str(classes),*[str(p) for p in sources]];save(out/'compile.command.json',dict(argv=args))
with (out/'compile.stdout.txt').open('xb') as stdout,(out/'compile.stderr.txt').open('xb') as stderr:code=subprocess.run(args,stdout=stdout,stderr=stderr,timeout=60).returncode
assert code==0,'HOST_ONLY_COMPILE_FAILED'
def launch(label,mode,path):
 result=out/(label+'.result.json');argv=[str(J/'java.exe'),'-cp',str(classes)+';'+str(OLD),'com.videokit.spike.e4.OnceCheck',mode,str(path),str(result)];save(out/(label+'.command.json'),dict(argv=argv));commands.append(dict(label=label,argv=argv));stdout=(out/(label+'.stdout.txt')).open('xb');stderr=(out/(label+'.stderr.txt')).open('xb');p=subprocess.Popen(argv,stdout=stdout,stderr=stderr);stdout.close();stderr.close();return p,result
def finish(job):
 p,result=job;code=p.wait(timeout=12);assert code==0;return json.loads(result.read_bytes())
def folder(name):p=out/name;p.mkdir();return p/'activation-deployment.once'
serial=folder('serial');first=finish(launch('serial-first','NORMAL',serial));second=finish(launch('serial-replay-new-jvm','NORMAL',serial));assert first['simulatedDispatches']==1 and second['simulatedDispatches']==0
race=folder('race');jobs=[launch('race-'+str(i),'NORMAL',race) for i in range(2)];races=[finish(j) for j in jobs];assert sum(x['simulatedDispatches'] for x in races)==1
force=folder('force-failed');failure=finish(launch('force-failed','FORCE_FAIL',force));again=finish(launch('force-replay','NORMAL',force));assert failure['simulatedDispatches']==again['simulatedDispatches']==0
unknown=folder('close-unknown');job=launch('close-unknown','CLOSE_UNKNOWN',unknown);p,result=job;end=time.monotonic()+10
while not result.exists() and p.poll() is None and time.monotonic()<end:time.sleep(.02)
assert result.exists();held=json.loads(result.read_bytes());assert held['productionExitAllowed'] is False and held['originalReturned'] is False and p.poll() is None
replay=finish(launch('unknown-replay-new-jvm','NORMAL',unknown));assert replay['simulatedDispatches']==0 and p.poll() is None
save(out/'unknown-fixture-teardown.json',dict(pid=p.pid,scope='ONLY synthetic local test JVM; no installer/child process',originalCloseAck=False,productionExitAllowed=False));p.terminate();p.wait(timeout=5)
artifact=B/'e11-host-tools-final.jar';entries=[]
with zipfile.ZipFile(OLD) as prior,zipfile.ZipFile(artifact,'x',zipfile.ZIP_DEFLATED) as z:
 for n in prior.namelist():
  if n.startswith('com/videokit/spike/e4/E9HostActivationSession'):continue
  raw=prior.read(n);z.writestr(n,raw);entries.append(dict(entry=n,sha256=hashlib.sha256(raw).hexdigest(),source='BYTE_IDENTICAL_BASE_E11_JAR'))
 for p in classes.rglob('*.class'):
  if p.name.startswith('OnceCheck'):continue
  name=p.relative_to(classes).as_posix();raw=p.read_bytes();z.writestr(name,raw);entries.append(dict(entry=name,sha256=hashlib.sha256(raw).hexdigest(),source='R1_HOST_ONLY_JAVAC',classMajor=int.from_bytes(raw[6:8],'big')))
assert not any('OnceCheck' in x['entry'] for x in entries)
save(B/'evidence/host-revision-results.json',dict(schema=1,status='PASS',baseJar=row(OLD),artifact=row(artifact),entries=entries,productionClasses=len(entries),tests=dict(serial=[first,second],concurrent=races,forceFailure=[failure,again],unknown=[held,replay]),javaFixtureInvocations=8,commands=commands,apkBuilds=0,deviceCalls=0,unknownTestTeardownNotCloseAck=True))
print('PASS host-only R1 persistent once barrier:8 synthetic JVM invocations; no APK rebuild/device')
