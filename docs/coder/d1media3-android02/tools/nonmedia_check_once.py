from pathlib import Path
import json,hashlib,subprocess,datetime
B=Path(__file__).resolve().parents[1];D=B/'evidence/nonmedia-001';D.mkdir(exist_ok=False)
J=Path('D:/Android/Android Studio/jbr/bin');sources=sorted(p for name in ['src','upstream','checks','platform-fixtures'] for p in (B/name).rglob('*.java'))+[B/'android/com/videokit/d1input/PlatformOutputErrors.java']
pins=[{'path':p.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]
(D/'source-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8');C=D/'classes';C.mkdir();cp=';'.join(str(p) for p in sorted((B/'deps').glob('*.jar')));a=D/'javac.args';a.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources),encoding='utf-8')
def run(name,argv,seconds):
 owner={'argv':argv,'startUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observationSeconds':seconds,'originalProcessReturned':False,'killInterruptRetry':0,'deviceOrMediaOperations':0}
 path=D/(name+'-owner.json');path.write_text(json.dumps(owner,indent=2),encoding='utf-8')
 with (D/(name+'.stdout')).open('xb') as out,(D/(name+'.stderr')).open('xb') as err:
  p=subprocess.Popen(argv,stdout=out,stderr=err,stdin=subprocess.DEVNULL,cwd=D,shell=False);owner['pid']=p.pid;path.write_text(json.dumps(owner,indent=2),encoding='utf-8')
  try:code=p.wait(seconds)
  except subprocess.TimeoutExpired:
   owner.update(status='UNKNOWN_ORIGINAL_RETURN_PENDING',endObservationUtc=datetime.datetime.now(datetime.timezone.utc).isoformat());path.write_text(json.dumps(owner,indent=2),encoding='utf-8');raise SystemExit('UNKNOWN: original kept; no kill or replay')
 owner.update(exitCode=code,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalProcessReturned=True,captureHandlesClosed=True);path.write_text(json.dumps(owner,indent=2),encoding='utf-8');print(name,'exit',code);assert code==0,(D/(name+'.stderr')).read_text()
run('javac',[str(J/'javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),'@'+str(a)],60)
run('metadata',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-cp',str(C)+';'+cp,'com.videokit.d1input.Android02NonMediaCheck'],30)
print((D/'metadata.stdout').read_text()[-1300:])
