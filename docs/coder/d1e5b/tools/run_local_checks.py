"""Targeted E5B own-file checks. No historical-suite rerun, Android/device/media/download."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def main():
 a=argparse.ArgumentParser();a.add_argument('--run',action='store_true');a.add_argument('--attempt',default='main-001');a.add_argument('--repair-reason');o=a.parse_args()
 sources=sorted((B/'src').rglob('*.java'))+[B/'tools/E5BGuardSelfCheck.java'];inputs=[row(p) for p in sources]
 if not o.run:print(json.dumps(dict(mode='INSPECT',inputs=inputs)));return
 if (B/'evidence/e5b-freeze.json').exists():raise ValueError('FROZEN')
 final=B/'evidence/local-check-results.json'
 if final.exists():
  old=json.loads(final.read_text());
  if not o.repair_reason or old['inputs']==inputs:raise ValueError('NO_DUPLICATE_PASSING_CHECK')
  final.rename(B/('evidence/local-check-results-before-'+o.attempt+'.json'))
 out=B/'evidence/jvm-attempts'/o.attempt;out.mkdir(parents=True,exist_ok=False);classes=B/'selfcheck'/o.attempt;classes.mkdir(parents=True,exist_ok=False);records=[]
 def call(n,args,t):
  log=out/(n+'.log')
  with log.open('xb') as f:r=subprocess.run([str(x) for x in args],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,timeout=t,check=False)
  records.append(dict(argv=[str(x) for x in args],exitCode=r.returncode,log=row(log)))
  if r.returncode or log.stat().st_size>1048576:raise ValueError('FAILED_'+n)
  return log.read_text(encoding='utf-8-sig')
 j=Path('D:/Android/Android Studio/jbr/bin');status='FAIL';error='';summary=None
 try:
  call('javac',[j/'javac.exe','--release','11','-encoding','UTF-8','-d',classes,*sources],120)
  flags=['-Dsun.nio.fs.ensureAccurateMetadata=true','--add-opens=java.base/sun.nio.fs=ALL-UNNAMED','--add-opens=java.base/sun.nio.ch=ALL-UNNAMED','--add-opens=java.base/java.io=ALL-UNNAMED']
  text=call('java',[j/'java.exe',*flags,'-cp',classes,'com.videokit.spike.e4.E5BGuardSelfCheck','all',out/'owned'],120);summary=json.loads(text.strip());assert summary['status']=='PASS_SUPPORTED_CASES';status='PASS'
 except Exception as e:error=str(e)
 d=dict(schema=1,status=status,scope='E5B_DIRECT_PRODUCTION_SUPPORTED_LOCAL_CASES',inputs=inputs,summary=summary,commands=records,error=error,repairReason=o.repair_reason,trueFileSymlink='NOT_RUN_OS_PRIVILEGE_1314',androidFstatFlock='NOT_RUN',realMediaReads=0,deviceCalls=0)
 (out/'attempt-result.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
 if status=='PASS':final.write_text(json.dumps(d,indent=2),encoding='utf-8')
 print(json.dumps(dict(status=status,summary=summary,error=error)))
 if status!='PASS':sys.exit(1)
if __name__=='__main__':main()
