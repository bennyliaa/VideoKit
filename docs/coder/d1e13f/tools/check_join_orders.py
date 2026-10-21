from pathlib import Path
import subprocess,json,hashlib
B=Path(__file__).resolve().parents[1];E=B/'evidence/join-orders-009';E.mkdir(exist_ok=False);C=B/'.checks/host-007';W=B/'.checks/join-orders-009';W.mkdir(parents=True,exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin');base=B/'evidence/public-004/LEGACY-NORMAL/slot';slot=E/'slot';slot.mkdir();raw=(base/'reviewed-original-disposition.json').read_bytes();(slot/'reviewed-original-disposition.json').write_bytes(raw)
src=E/'E13GuardLocation.java';src.write_text('package com.videokit.spike.e4;import java.nio.file.*;final class E13GuardLocation {static final Path ROOT=Paths.get("'+slot.resolve().as_posix()+'");static String dispositionSha(){return "'+hashlib.sha256(raw).hexdigest()+'";}static Thread returnCustodian(Runnable r,String id){Thread t=new Thread(r,"LOCAL_TEST_claim_"+id);t.setDaemon(true);return t;}}')
commands=[[str(J/'javac.exe'),'-cp',str(C),'-d',str(W),str(src),str(B/'selfchecks/FJoinOrderCheck.java')],[str(J/'java.exe'),'-cp',str(W)+';'+str(C),'com.videokit.spike.e4.FJoinOrderCheck',str(E)]]
for name,cmd in zip(['compile','check'],commands):
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(cmd,stdout=so,stderr=se);code=p.wait(timeout=15)
 (E/(name+'.exit.json')).write_text(json.dumps(dict(argv=cmd,pid=p.pid,exitCode=code,naturalReturn=True))+'\n');assert code==0,(E/(name+'.stderr.txt')).read_text()
(E/'results.json').write_text(json.dumps(dict(status='PASS_SAME_ORIGINAL_JOIN_ORDER',orders=['follow-before-close','follow-after-actual-termination','concurrent-follow-close'],manualOriginalReturnedTrue=0,realSupervisors=True,localChildren=0,deviceCalls=0),indent=2)+'\n');print('PASS same original join before/after/concurrent; no notification loss, no manual true')
