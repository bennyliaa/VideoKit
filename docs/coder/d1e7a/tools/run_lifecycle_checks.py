"""One finite execution of the actual managed job/finish boundary. No device or media."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
def run():
 if (B/'evidence/e7a-freeze.json').exists():raise RuntimeError('FROZEN')
 dest=B/'.selfcheck/lifecycle-002';dest.mkdir(parents=True)
 support=R/'docs/coder/d1e7/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
 files=[B/'src/com/videokit/spike/e4'/n for n in ['E4Owned.java','E5AOwner.java','E7WriterDeathGate.java']]+[B/'app/src/androidTest/java/com/videokit/spike/e4/E7ADiagnosticRun.java',B/'tools/E7ALifecycleSelfCheck.java']
 java=Path('D:/Android/Android Studio/jbr/bin');commands=[]
 for tag,argv in [('compile',[str(java/'javac.exe'),'-encoding','UTF-8','-cp',str(support),'-d',str(dest)]+[str(p) for p in files]),('run',[str(java/'java.exe'),'-cp',str(dest)+';'+str(support),'com.videokit.spike.e4.E7ALifecycleSelfCheck'])]:
  result=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);p=B/('evidence/lifecycle-'+tag+'-002.log')
  with p.open('xb') as f:f.write(result.stdout)
  commands.append(dict(argv=argv,exitCode=result.returncode,log=row(p)))
  if result.returncode:raise RuntimeError(result.stdout.decode(errors='replace'))
  if tag=='run':match=re.search(r'actual_job_finish_cases=(\d+) assertions=(\d+)',result.stdout.decode());assert match
 write(B/'evidence/local-check-results.json',dict(schema=1,status='PASS',actualJobFinishCases=int(match[1]),assertions=int(match[2]),inputs=[row(p) for p in files],commands=commands,scope='Actual E7ADiagnosticRun.run/deadline/acknowledgeFinish plus original E4Owned and E7WriterDeathGate executed. Virtual monotonic clock; latch-controlled platform open/read/close and history/proc ports; finish callback is a counter. No copied lifecycle model. Thread barriers max2s/join1s; no Android process-liveness guarantee claimed.',qualificationDeadlineNs=10000000000,earlyPlatformFinishes=0,reopens=0,oldGate27Cases='INHERITED_E7_NOT_RERUN',androidExecution='NOT_RUN',deviceCalls=0,mediaReads=0))
 old=R/'docs/coder/d1e7';kept=[]
 for directory in ['src','android','native','upstream-c14']:
  for p in sorted((B/directory).rglob('*')):
   if not p.is_file():continue
   prior=old/p.relative_to(B);assert p.read_bytes()==prior.read_bytes();kept.append(dict(current=row(p),baseline=row(prior)))
 entry=(B/'app/src/androidTest/java/com/videokit/spike/e4/E7AReadOnlyInstrumentation.java').read_text()
 assert 'extends Instrumentation' in entry and 'super.finish(' in entry and entry.count('super.finish(')==1
 assert 'original.acknowledgeFinish' in entry and 'android.permission.DUMP' in entry
 assert 'original.run()' in entry and 'original.deadline()' in entry
 assert 'new E7ADiagnosticRun<>' in entry
 for forbidden in ['.observe(','.fsync(','.force(','.cancel(','.interrupt(','.join(','.await(','setDaemon(','.startService(','.bindService(']:assert forbidden not in entry
 legacy=(B/'app/src/androidTest/java/com/videokit/spike/e4/E7WriterDeathDiagnosticTests.java').read_text();assert 'NO_JOB_STARTED' in legacy and 'new Thread' not in legacy
 write(B/'evidence/integration-static-check.json',dict(schema=1,status='PASS',sourceDirectoriesEntirelyByteIdentical=kept,runner=row(B/'app/src/androidTest/java/com/videokit/spike/e4/E7AReadOnlyInstrumentation.java'),actualBoundary=row(B/'app/src/androidTest/java/com/videokit/spike/e4/E7ADiagnosticRun.java'),legacyJUnitEntry='DISABLED_BEFORE_JOB',productionGate='BYTE_IDENTICAL_E7',permissions='NO_NEW_REQUESTED_PERMISSION; control sender must hold existing DUMP',androidRuntime='NOT_RUN',managedLifecycle='NO_JUNIT; async onStart return; external exact-handle/sequence archive ACK and actual operations+owner returns before platform finish'))
 write(B/'evidence/native-and-strict-logic-inheritance.json',dict(schema=1,status='PASS',nativeRebuild=False,allProductionDirectoriesByteIdentical=True,baseline='D1-20261017-E7',strictGate='E6B inherited6frames1000us/fullEOF/content/thumb unchanged',deviceCalls=0,mediaReads=0))
 print(json.dumps(dict(status='PASS',cases=int(match[1]),assertions=int(match[2]),unchangedProductionFiles=len(kept))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run-once',action='store_true');a=p.parse_args()
 if a.run_once:run()
 else:print('INSPECT_ONLY')
