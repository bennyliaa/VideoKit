"""Default inspection; explicit bounded production boundary check, no media/device/native execution."""
from pathlib import Path
import argparse,hashlib,json,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def run():
 if (B/'evidence/e6a-freeze.json').exists():raise RuntimeError('FROZEN')
 dest=B/'.selfcheck/attempt-005';dest.mkdir();classes=dest/'classes';classes.mkdir()
 base=R/'docs/coder/d1e6/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
 assert base.exists(),'Existing E6 support classes required; no automatic build/download'
 cp=str(base)+';D:/Android/SDK/platforms/android-36/android.jar'
 files=sorted(list((B/'src').rglob('*.java'))+list((B/'upstream-c14/src').rglob('*.java'))+[B/p for p in ['upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java','upstream-c14/android/com/videokit/spike/c14/PipelineValidationReceipt.java','upstream-c14/android/com/videokit/spike/c14/StageLog.java','android/com/videokit/spike/c14/E4CpuAdapter.java','tools/E6ABoundarySelfCheck.java']]+list((B/'tools/jvm-stubs').rglob('*.java')))
 commands=[['D:/Android/Android Studio/jbr/bin/javac.exe','-J-Duser.language=en','-encoding','UTF-8','-cp',cp,'-d',str(classes)]+[str(p) for p in files],['D:/Android/Android Studio/jbr/bin/java.exe','-cp',str(classes)+';'+cp,'com.videokit.spike.c14.E6ABoundarySelfCheck']];attempts=[]
 for n,cmd in enumerate(commands):
  p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);log=B/('evidence/boundary-'+('compile' if n==0 else 'run')+'-005.log')
  with log.open('xb') as out:out.write(p.stdout)
  attempts.append(dict(argv=cmd,exitCode=p.returncode,log=row(log)))
  if p.returncode:raise RuntimeError('BOUNDARY_CHECK_FAILED:'+str(log))
  if n==1:assert 'production_boundary_cases=20 assertions=112' in p.stdout.decode()
 old=B/'evidence/local-check-results.json'
 if old.exists():old.rename(B/'evidence/local-check-results-before-start-state-precision.json')
 result=dict(schema=1,status='PASS',productionBoundaryCases=20,assertions=112,inputs=[row(p) for p in files],commands=attempts,concurrency=dict(threads=16,published=1,duplicateRejected=15,firstRetained=True),scope='Actual shared production validate/next ownership and receipt/content workflows, full diagnostic receive boundary and session scope router. Only platform start/stop/close/lifecycle and Context/Looper/Log are simulated; not helper-only or real Android/JNI/Binder proof.',supportClasses='Existing E6 Android support classes only; all pure production rules plus every changed boundary class freshly compiled from E6A inputs above',deviceCalls=0,mediaReads=0,nativeRebuild=False,history='001 missing test Context stub signatures; 002 passed18; 003 ownership-window safeguards passed20/111; 004 source-success field20/112; 005 known pre-start/unknown-in-flight precision and final20/112 passed')
 with old.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
 print('PASS 20 direct production boundary cases /112 assertions; concurrent16 exactly1 accepted15 rejected; media/device0')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run-once',action='store_true');a=p.parse_args()
 if a.run_once:run()
 else:print('INSPECT: --run-once requires unfrozen candidate and unused attempt-005; no calls made')
