"""One serial pinned JDK build/test, with at most the explicitly authorized repair.
Review output is external; never runs Gradle, Android, or a frozen old launcher.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,os,json,hashlib,time,subprocess,zipfile,threading,argparse
H=Path(__file__).resolve().parent;P=Path('D:/CodexProjects/VideoKit');J=Path('D:/Android/Android Studio/jbr/bin')
ap=argparse.ArgumentParser();ap.add_argument('--attempt',choices=['01','02']);ap.add_argument('--output');a=ap.parse_args();review=a.output is not None
if review:
 if a.attempt is not None:raise SystemExit('EXACT_MODE_REQUIRED')
 D=Path(a.output);base=P/'docs/tester/D1_HOST_TRANSACTION02_SOURCE_BINDING_FIX_REVIEW_EVIDENCE'
 if not D.is_absolute() or str(D)!=str(D.resolve()) or not D.is_relative_to(base) or len(D.relative_to(base).parts)!=1:raise SystemExit('EXACT_NEW_INDEPENDENT_REVIEW_ROOT_REQUIRED')
 deadline=time.monotonic()+600
else:
 if a.attempt is None or (H/'manifest.json').exists():raise SystemExit('UNFROZEN_CODER_ATTEMPT_REQUIRED')
 D=H/'evidence'/('attempt'+a.attempt);prep=json.loads((H/'evidence/preparation.json').read_bytes());deadline=prep['monotonicDeadline']
 if a.attempt=='02':
  previous=json.loads((H/'evidence/attempt01/result.json').read_bytes())
  if previous['status']=='PASS':raise SystemExit('REPAIR_NOT_NEEDED_NO_SECOND_RUN')
if D.exists():raise SystemExit('NO_ATTEMPT_OR_REVIEW_REUSE')
for p in [D,*D.parents]:
 if p.exists() and p.stat().st_file_attributes&1024:raise SystemExit('NO_REPARSE_OUTPUT')
D.mkdir(parents=True);read_reserved=0;saved_reserved=0;events=[];processes=[];held=[]
FROZEN_ENV=dict(os.environ)
ENV_SHA=hashlib.sha256((json.dumps(FROZEN_ENV,sort_keys=True,ensure_ascii=True,separators=(',',':'))+'\n').encode()).hexdigest()
process_specs={}
def guard():
 if time.monotonic()>=deadline:raise RuntimeError('BATCH_DEADLINE_STOP_NEW')
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p,cap=16777216,expected=None):
 global read_reserved
 guard();n=p.stat().st_size
 if n>cap or read_reserved+n+1>536870912:raise ValueError('READ_CAP_BEFORE_OPEN')
 read_reserved+=n+1
 with p.open('rb') as f:b=f.read(n+1)
 if len(b)!=n or expected is not None and sha(b)!=expected:raise ValueError('PIN_MISMATCH:'+str(p))
 return b
def write(p,b):
 global saved_reserved
 if saved_reserved+len(b)>33554432:raise ValueError('SAVED_CAP_BEFORE_OPEN')
 saved_reserved+=len(b);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
def save(p,d):write(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def retain(reason,*objects):
 held.extend(objects);save(D/('unknown-'+str(len(held))+'.json'),dict(reason=reason,stopNew=True,secondClose=False,kill=False));
 while True:time.sleep(.1)
def run(name,argv):
 global saved_reserved
 guard();saved_reserved+=2097152
 if saved_reserved>33554432:raise ValueError('STREAM_RESERVATION')
 out=(D/(name+'.stdout')).open('xb');err=(D/(name+'.stderr')).open('xb');start=time.monotonic()
 spec=process_specs[name]
 if argv!=spec['argv'] or ENV_SHA!=spec['envSha256']:raise RuntimeError('FROZEN_ACTUAL_CALL_SPEC')
 try:p=subprocess.Popen(argv,executable=argv[0],cwd=str(P),env=FROZEN_ENV,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False,close_fds=True)
 except BaseException:retain('ORIGINAL_CONSTRUCTOR_UNKNOWN',out,err)
 row=dict(name=name,argv=argv,envSha256=ENV_SHA,exactSpec=spec,pid=p.pid,constructorReturned=True,startedMonotonic=start,waitReturned=False,handleCloseReturned=False,stdoutCloseReturned=False,stderrCloseReturned=False);processes.append(row)
 try:code=p.wait(timeout=min(300,max(.01,deadline-time.monotonic())))
 except subprocess.TimeoutExpired:
  row['observationExpired']=True;row['stopNew']=True
  # No kill, replacement wait object, or close to manufacture return.
  code=p.wait()
 row.update(exitCode=code,waitReturned=True,endedMonotonic=time.monotonic())
 try:
  if os.name=='nt':p._handle.Close()
  row['handleCloseReturned']=True;out.close();row['stdoutCloseReturned']=True;err.close();row['stderrCloseReturned']=True
 except BaseException:retain('ORIGINAL_CLOSE_UNKNOWN',p,out,err)
 row.update(stdoutBytes=(D/(name+'.stdout')).stat().st_size,stderrBytes=(D/(name+'.stderr')).stat().st_size)
 save(D/(name+'-return.json'),row)
 if row['stdoutBytes']>1048576 or row['stderrBytes']>1048576 or row.get('observationExpired'):raise RuntimeError('OBSERVATION_OR_STREAM_CAP_FAILURE')
 return code
status='FAIL';error=None
try:
 if review:
  manifest=json.loads(read(H/'manifest.json'))
  for r in manifest['files']:read(H/r['path'],33554432,r['sha256'])
 prep=json.loads(read(H/'evidence/preparation.json'));read(H/'case-plan.json')
 for r in prep['copyInputs']:read(Path(r['path']),16777216,r['sha256'])
 for r in prep['sourceReads']:
  if r['path'] in (str(J/'java.exe'),str(J/'javac.exe')):read(Path(r['path']),1048576,r['sha256'])
 sources=sorted((H/'src').rglob('*.java'))+sorted((H/'checks').rglob('*.java'))+sorted((H/'reference/regression-sources').rglob('*.java'))+sorted((H/'reference/platform-fixtures').rglob('*.java'))
 inputs=[]
 for p in [*sources,*sorted((H/'lib').glob('*.jar')),H/'run_batch.py']:
  b=read(p);inputs.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 save(D/'source-input-pins.json',inputs)
 with zipfile.ZipFile(D/'exact-new-and-regression-sources.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sources:z.writestr(p.relative_to(H).as_posix(),read(p))
 saved_reserved+=(D/'exact-new-and-regression-sources.zip').stat().st_size
 classes=D/'classes';classes.mkdir();args=D/'javac.args';write(args,('\n'.join('"'+p.as_posix()+'"' for p in sources)+'\n').encode())
 cp=';'.join(str(p) for p in sorted((H/'lib').glob('*.jar')))
 production=D/'host-transaction02.jar';tests=D/'host-transaction02-tests.jar'
 compile_argv=[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(classes),'@'+str(args)]
 runtime=';'.join([str(production),str(tests),cp]);test_argv=[str(J/'java.exe'),'-Xmx256m','-cp',runtime,'com.videokit.d1hosttx.HostTransactionCheck',str(D/'work')]
 process_specs={name:dict(argv=argv,executable=argv[0],cwd=str(P),envSha256=ENV_SHA,envMode='EXACT_EXPLICIT_FROZEN_COPY_NO_PLAINTEXT_ARCHIVE',stdin='DEVNULL',stdout=str(D/(name+'.stdout')),stderr=str(D/(name+'.stderr')),shell=False,close_fds=True) for name,argv in [('compile',compile_argv),('checks',test_argv)]}
 save(D/'order.json',dict(sourcePins=inputs,casePlanSha256=sha(read(H/'case-plan.json')),specs=process_specs,beforeAnyPopen=True,deadlineMonotonic=deadline,readCap=536870912,savedCap=33554432,productSDK=False,admin=False,ACLModification=False))
 code=run('compile',compile_argv)
 if code!=0:raise RuntimeError('COMPILE_FAILED')
 for path,is_product in ((production,True),(tests,False)):
  with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as z:
   for p in sorted(classes.rglob('*.class')):
    rel=p.relative_to(classes).as_posix();prod=rel.startswith('com/videokit/d1hosttx/') and not Path(rel).name.startswith('HostTransactionCheck')
    if prod==is_product:z.writestr(rel,read(p))
  saved_reserved+=path.stat().st_size
 code=run('checks',test_argv)
 if code!=0:raise RuntimeError('TEST_FAILED')
 summary=json.loads(read(D/'work/summary.json'));assert summary['passed']==12 and summary['originalRealFileCases']==8 and summary['sourceBindingMatrixGroups']==4 and summary['affectedFrozenAuthorityScenarios']==3 and summary['hostOwners']==summary['SDKOwners']==summary['sourceOwners']==0
 for r in inputs:read(Path(r['path']),16777216,r['sha256'])
 status='PASS'
except Exception as e:error=repr(e)
finally:
 actual=sum(p.stat().st_size for p in D.rglob('*') if p.is_file())
 save(D/'result.json',dict(status=status,error=error,review=review,readReserved=read_reserved,permanentSavedReservation=saved_reserved,actualOutputBytesBeforeResult=actual,processes=processes,remainingBatchSeconds=max(0,deadline-time.monotonic()),D1='NOT_PASSED',M0='NOT_STARTED',Android='NOT_RUN',Gradle=0,SDK=0,device=0))
 print(json.dumps(dict(status=status,error=error,output=str(D),readReserved=read_reserved,permanentSavedReservation=saved_reserved,actualOutputBytes=actual)))
if status!='PASS':raise SystemExit(2)
