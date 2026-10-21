"""Finite own-file JVM evidence. No device or media access."""
from pathlib import Path
import hashlib,json,subprocess,sys,os
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--run',action='store_true');a.add_argument('--attempt',default='main-001');a.add_argument('--repair-reason');o=a.parse_args()
 sources=sorted((B/'src').rglob('*.java'))+[B/'android/com/videokit/spike/e4/E4EncoderNegotiation.java',B/'tools/E4CoreSelfCheck.java',B/'tools/E5SelfCheck.java']
 inputs=[row(p) for p in sources]
 if not o.run:print(json.dumps(dict(mode='INSPECT',inputs=inputs)));return
 if (B/'evidence/e5-freeze.json').exists():raise ValueError('FROZEN')
 final=B/'evidence/local-check-results.json'
 if final.exists():
  if not o.repair_reason or json.loads(final.read_text())['inputs']==inputs:raise ValueError('PASSING_CHECK_NO_DUPLICATE')
  final.rename(B/('evidence/local-check-results-before-'+o.attempt+'.json'))
 out=B/'evidence/jvm-attempts'/o.attempt;out.mkdir(parents=True,exist_ok=False)
 classes=B/'selfcheck'/o.attempt;classes.mkdir(parents=True,exist_ok=False)
 j=Path('D:/Android/Android Studio/jbr/bin');records=[];summaries=[]
 def call(name,argv,seconds=30):
  p=out/(name+'.log')
  with p.open('xb') as f:r=subprocess.run([str(x) for x in argv],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,timeout=seconds,check=False)
  record=dict(argv=[str(x) for x in argv],exitCode=r.returncode,log=row(p));records.append(record)
  if r.returncode:raise ValueError('FAILED_'+name)
  if p.stat().st_size>1048576:raise ValueError('OUTPUT_BOUND')
  return p.read_text(encoding='utf-8-sig')
 status='FAIL';error=''
 try:
  call('javac',[j/'javac.exe','-encoding','UTF-8','--release','11','-d',classes,*sources],120)
  call('core',[j/'java.exe','-cp',classes,'com.videokit.spike.e4.E4CoreSelfCheck'])
  for mode in ['main','close-unknown','durability-unknown']:
   text=call(mode,[j/'java.exe','-cp',classes,'com.videokit.spike.e4.E5SelfCheck',out/('owned-'+mode),mode]);summaries.append(json.loads(text.strip()))
  status='PASS'
 except Exception as e:error=str(e)
 evidence=dict(schema=1,status=status,scope='E5_LOCAL_SYNTHETIC_JVM',inputs=inputs,commands=records,summaries=summaries,error=error,repairReason=o.repair_reason,androidExecution='NOT_RUN',deviceCalls=0,oldMediaReads=0)
 (out/'attempt-result.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 if status=='PASS':final.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 print(json.dumps(dict(status=status,summaries=summaries,error=error)))
 if status!='PASS':sys.exit(1)
if __name__=='__main__':main()
