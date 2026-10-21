"""Explicit narrow public-entry checks; default inspection; no device/media/native execution."""
from pathlib import Path
import argparse,json,subprocess,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def run():
 if (B/'evidence/e6b-freeze.json').exists():raise RuntimeError('FROZEN')
 dest=B/'.selfcheck/public-001';dest.mkdir(parents=True);base=R/'docs/coder/d1e6a/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';assert base.exists()
 cp=str(base)+';D:/Android/SDK/platforms/android-36/android.jar'
 files=sorted(list((B/'src').rglob('*.java'))+list((B/'upstream-c14/src').rglob('*.java'))+[B/p for p in ['android/com/videokit/spike/c14/E4CpuAdapter.java','upstream-c14/android/com/videokit/spike/c14/PipelineValidationReceipt.java','upstream-c14/android/com/videokit/spike/c14/StageLog.java','tools/E6BPublicPreflightSelfCheck.java']]+list((B/'tools/jvm-stubs').rglob('*.java')))
 commands=[['D:/Android/Android Studio/jbr/bin/javac.exe','-J-Duser.language=en','-encoding','UTF-8','-cp',cp,'-d',str(dest)]+[str(p) for p in files],['D:/Android/Android Studio/jbr/bin/java.exe','-cp',str(dest)+';'+cp,'com.videokit.spike.c14.E6BPublicPreflightSelfCheck']];records=[]
 for i,cmd in enumerate(commands):
  result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);p=B/('evidence/public-'+('compile' if i==0 else 'run')+'-001.log')
  with p.open('xb') as f:f.write(result.stdout)
  records.append(dict(argv=cmd,exitCode=result.returncode,log=row(p)))
  if result.returncode:raise RuntimeError('PUBLIC_CHECK_FAILED:'+str(p))
  if i==1:assert 'public_entry_cases=6 assertions=59' in result.stdout.decode()
 value=dict(schema=1,status='PASS',publicEntryCases=6,assertions=59,badTimelineCases=5,badTimelineCpuCreations=0,badTimelineContextCalls=0,sourceOpenCalls=0,digestCalls=0,legalPreflightCreationTripwire=1,inputs=[row(p) for p in files],commands=records,scope='Actual public E4CpuAdapter.validate(Context,...) calls; original production PipelineRules exceptions retained by identity/cause/origin, session router. Binder constructor tripwire calibrates real CPU creation site on legal input only; not Android/normal success. Context/Looper/Log/Binder are test-only platform shims.',supportClasses='Frozen E6A existing supporting classes; changed adapter and all pure rules freshly compiled above',deviceCalls=0,mediaReads=0,nativeRebuild=False,prior20BoundaryCases='INHERITED_NOT_RERUN')
 with (B/'evidence/local-check-results.json').open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
 print('PASS public6 /59 assertions; bad CPU/context/source/digest creation0; legal input reaches real constructor tripwire only')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run-once',action='store_true');a=p.parse_args()
 if a.run_once:run()
 else:print('INSPECT public entry check; explicit --run-once only, no calls made')
