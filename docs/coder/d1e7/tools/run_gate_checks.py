"""Finite checks of the exact production gate; no Android/device/media or file-protocol simulation."""
from pathlib import Path
import hashlib,json,re,subprocess,argparse
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
def run():
 if (B/'evidence/e7-freeze.json').exists():raise RuntimeError('FROZEN')
 out=B/'.selfcheck/gate-001';out.mkdir(parents=True)
 support=R/'docs/coder/d1e6b/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
 assert support.is_dir()
 files=[B/'src/com/videokit/spike/e4'/n for n in ['E5AOwner.java','E7WriterDeathGate.java']]+[B/'tools/E7WriterDeathGateSelfCheck.java']
 java=Path('D:/Android/Android Studio/jbr/bin');commands=[]
 for tag,argv in [('compile',[str(java/'javac.exe'),'-encoding','UTF-8','-cp',str(support),'-d',str(out)]+[str(p) for p in files]),('run',[str(java/'java.exe'),'-cp',str(out)+';'+str(support),'com.videokit.spike.e4.E7WriterDeathGateSelfCheck'])]:
  result=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
  p=B/('evidence/gate-'+tag+'-001.log')
  with p.open('xb') as f:f.write(result.stdout)
  commands.append(dict(argv=argv,exitCode=result.returncode,log=row(p)))
  if result.returncode:raise RuntimeError(result.stdout.decode(errors='replace'))
  if tag=='run':
   match=re.search(r'production_gate_cases=(\d+) assertions=(\d+)',result.stdout.decode());assert match
 old=R/'docs/coder/d1e6b';kept=[]
 for root,names in [('src/com/videokit/spike/e4',['E5AOwner.java','E5AFinalObservation.java','E5AAdmission.java','E5ALifecycle.java','E5N2Recovery.java','E5BGuard.java','E5BFileId.java','E4OutputBudget.java']),('android/com/videokit/spike/c14',['E4CpuAdapter.java']),('app/src/androidTest/java/com/videokit/spike/e4',['E4DeviceTests.java'])]:
  for name in names:
   p=B/root/name;q=old/root/name;assert p.read_bytes()==q.read_bytes();kept.append(dict(current=row(p),baseline=row(q)))
 adapter=(B/'android/com/videokit/spike/e4/E5N2RecoveryAndroid.java').read_text()
 assert 'E7WriterDeathGate.inspect(owner,System.currentTimeMillis()' in adapter
 assert 'getHistoricalProcessExitReasons(context.getPackageName(),pid,max)' in adapter
 assert 'Os.lstat("/proc/"+pid)' in adapter
 entry=(B/'app/src/androidTest/java/com/videokit/spike/e4/E7WriterDeathDiagnosticTests.java').read_text()
 for forbidden in ['.observe(','.fsync(','.force(','.startService(','.bindService(','.createFile(','.write(','ABORT','E5AAdmission']:
  assert forbidden not in entry,forbidden
 assert 'OsConstants.O_RDONLY|OsConstants.O_NOFOLLOW|OsConstants.O_NONBLOCK' in entry
 assert 'new byte[257]' in entry and 'done.await(10,TimeUnit.SECONDS)' in entry
 tests=dict(schema=1,status='PASS',productionGateCases=int(match[1]),assertions=int(match[2]),inputs=[row(p) for p in files],commands=commands,scope='Exact production E7WriterDeathGate called with substituted Android history/proc ports. Android adapter compiled by separate APK build; no Android API behavior claimed. No model copy. No persistent fact parser exists or is tested.',historyCallsPerCaseMax=1,historyLimit=8,admissionGrants=0,deviceCalls=0,mediaReads=0,persistentProtocol='DISABLED_DESIGN_ONLY',priorE6BBoundaries='INHERITED_BYTE_IDENTICAL_NOT_RERUN')
 write(B/'evidence/local-check-results.json',tests)
 write(B/'evidence/integration-static-check.json',dict(schema=1,status='PASS',unchanged=kept,productionAdapter=row(B/'android/com/videokit/spike/e4/E5N2RecoveryAndroid.java'),readOnlyEntry=row(B/'app/src/androidTest/java/com/videokit/spike/e4/E7WriterDeathDiagnosticTests.java'),dynamicScope='Pure gate only; Android adapter and readonly entry NOT_RUN',writerPredicate='one query max8; identity/time matches counted before reason; only unique positive reason then procENOENT',persistentProtocol='DISABLED',admissionUnchanged=True,resourcesUnchanged=True))
 native=[]
 for p in sorted((B/'native').rglob('*')):
  if p.is_file():
   q=old/p.relative_to(B);assert p.read_bytes()==q.read_bytes();native.append(row(p))
 write(B/'evidence/native-and-strict-logic-inheritance.json',dict(schema=1,status='PASS',nativeRebuild=False,files=native,strictGate='E6B inherited6frames1000us/fullEOF/content/thumb unchanged; no dynamic rerun',deviceCalls=0,mediaReads=0))
 print(json.dumps(dict(status='PASS',cases=tests['productionGateCases'],assertions=tests['assertions'],unchangedBoundaries=len(kept))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run-once',action='store_true');a=p.parse_args()
 if a.run_once:run()
 else:print('INSPECT_ONLY')
