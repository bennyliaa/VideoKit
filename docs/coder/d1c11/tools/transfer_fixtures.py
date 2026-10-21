"""Windows binary-safe shell-v2 raw transfer. Default PLAN ONLY; no installs or server/device management.
Future tester execution requires explicit serial, candidate/data review and fixed C11-only aliases.
Independently authored protocol implementation; tester workaround used as evidence, not copied executable.
"""
from pathlib import Path
import argparse,hashlib,json,re,socket,struct,subprocess,threading,time
ROOT=Path(__file__).resolve().parents[4];PACKAGE='com.videokit.app';DIRECTORY='files/d1_c11_fixtures';CHUNK=32768;MAX_LOG=65536
FIXTURES={
 'basic.mp4':('imgs_and_videos/videos/sample.mp4','720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9'),
 'subtitle.avi':('02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi','3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f'),
 'subtitle.srt':('02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.chs.srt','d3a44be0636d9ec4d5a2782d1a5d6ceb7141d7bf4f8df2f693d9850f867144bd'),
 'large.mkv':('03_large_files/large_video_over_2GiB.mkv','28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26')}
def receive(sock,n,stop):
 data=bytearray()
 while len(data)<n:
  if time.monotonic()>stop:raise TimeoutError('TRANSFER_DEADLINE')
  try:part=sock.recv(n-len(data))
  except socket.timeout:continue
  if not part:raise IOError('ADB_STREAM_CLOSED')
  data.extend(part)
 return bytes(data)
def service(sock,command):
 data=command.encode('ascii');assert len(data)<=4096;sock.sendall(f'{len(data):04x}'.encode()+data);stop=time.monotonic()+30
 if receive(sock,4,stop)!=b'OKAY':
  length=int(receive(sock,4,stop),16)
  if length>4096:raise IOError('ADB_SERVICE_RESPONSE_BUDGET')
  receive(sock,length,stop);raise IOError('ADB_SERVICE_REJECTED')
def transfer(sock,stream,expected_bytes,seconds=600):
 stop=time.monotonic()+seconds;result={};done=threading.Event();eof=threading.Event()
 def drain():
  try:
   logs=0
   while True:
    channel,length=struct.unpack('<BI',receive(sock,5,stop))
    if length>CHUNK or channel not in (1,2,3):raise IOError('ADB_FRAME_BUDGET_OR_CHANNEL')
    payload=receive(sock,length,stop)
    if channel==3:
     if not eof.is_set():raise IOError('ADB_PREMATURE_EXIT')
     if length not in (1,4) or int.from_bytes(payload,'little')!=0:raise IOError('REMOTE_WRITE_FAILED')
     result['exit']=0;return
    logs+=length
    if logs>MAX_LOG:raise IOError('ADB_OUTPUT_BUDGET')
  except BaseException as error:result['error']=error
  finally:done.set()
 reader=threading.Thread(target=drain,daemon=True);reader.start();digest=hashlib.sha256();total=0
 try:
  while True:
   if time.monotonic()>stop:raise TimeoutError('TRANSFER_DEADLINE')
   if done.is_set():raise result.get('error',IOError('ADB_PREMATURE_EXIT'))
   data=stream.read(CHUNK)
   if not data:break
   if len(data)>CHUNK or total+len(data)>expected_bytes:raise IOError('SOURCE_LENGTH_CHANGED')
   sock.sendall(struct.pack('<BI',0,len(data))+data);digest.update(data);total+=len(data)
  if total!=expected_bytes:raise IOError('SOURCE_LENGTH_CHANGED')
  eof.set();sock.sendall(struct.pack('<BI',4,0));reader.join(max(0,stop-time.monotonic()))
  if not done.is_set():raise TimeoutError('TRANSFER_DEADLINE')
  if 'error' in result:raise result['error']
  return {'bytes':total,'sha256':digest.hexdigest(),'chunk_bound':CHUNK,'exit':result['exit']}
 except BaseException:
  sock.close();reader.join(1);raise
def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(CHUNK),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--serial');p.add_argument('--execute',action='store_true');p.add_argument('--device-and-installed-c11-reviewed',action='store_true');p.add_argument('--overwrite-c11-fixtures-reviewed',action='store_true');p.add_argument('--aliases',nargs='+',choices=FIXTURES,default=['basic.mp4']);p.add_argument('--result-file');args=p.parse_args()
 paths={name:(ROOT/'test_media'/FIXTURES[name][0]).resolve() for name in args.aliases}
 for path in paths.values():assert path.is_relative_to((ROOT/'test_media').resolve())
 if not args.execute:
  print(json.dumps({'state':'PLAN_ONLY_NO_DEVICE_COMMANDS','candidate':'D1-20261016-C11','fixture_directory':DIRECTORY,'aliases':{n:{'bytes':v.stat().st_size,'sha256':FIXTURES[n][1]} for n,v in paths.items()}},indent=2));return
 if not (args.serial and re.fullmatch(r'[A-Za-z0-9_.:-]{1,80}',args.serial) and args.device_and_installed_c11_reviewed and args.overwrite_c11_fixtures_reviewed and args.result_file):p.error('Explicit serial, installed candidate/data review, C11 overwrite review and tester result-file required')
 result_path=Path(args.result_file).resolve()
 if not result_path.is_relative_to((ROOT/'docs/tester').resolve()):p.error('Result file must be under docs/tester; frozen coder evidence is immutable')
 if result_path.exists():p.error('Existing result file must not be overwritten; choose a new attempt')
 for n,path in paths.items():
  if hashfile(path)!=FIXTURES[n][1]:raise IOError('SOURCE_HASH_MISMATCH')
 # Small text only through adb CLI; binary file data exclusively uses framed local socket.
 def command(*items):
  proc=subprocess.Popen(['D:/Android/SDK/platform-tools/adb.exe','-s',args.serial,*items],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  data=bytearray();errors=[]
  def drain():
   try:
    while True:
     part=proc.stdout.read(min(4096,16385-len(data)))
     if not part:break
     data.extend(part)
     if len(data)>16384:raise IOError('PREFLIGHT_OUTPUT_BUDGET')
   except Exception as error:errors.append(error);proc.kill()
  reader=threading.Thread(target=drain,daemon=True);reader.start();reader.join(30)
  if reader.is_alive():proc.kill();reader.join(2);raise TimeoutError('PREFLIGHT_DEADLINE')
  try:code=proc.wait(timeout=2)
  except subprocess.TimeoutExpired:proc.kill();raise TimeoutError('PREFLIGHT_EXIT_DEADLINE')
  finally:proc.stdout.close()
  if errors:raise errors[0]
  if code!=0:raise IOError('PREFLIGHT_COMMAND_FAILED')
  return bytes(data).decode('utf-8',errors='strict').strip()
 import device_guard
 device_guard.require_ready(args.serial,lambda items:command(*items))
 command('shell','run-as',PACKAGE,'pwd')
 listing=command('shell','run-as',PACKAGE,'sh','-c',f"'if test -d {DIRECTORY}; then ls -1 {DIRECTORY}; fi'")
 allowed=set(FIXTURES)|{n+'.c11-part' for n in FIXTURES}
 if any(n not in allowed for n in listing.splitlines()):raise IOError('UNKNOWN_C11_DIRECTORY_CONTENTS')
 free=int(command('shell','df','-k','/data').splitlines()[-1].split()[3])*1024
 required=sum(v.stat().st_size for v in paths.values())+max(v.stat().st_size for v in paths.values())+268435456
 if free<required:raise IOError('INSUFFICIENT_DEVICE_SPACE')
 command('shell','run-as',PACKAGE,'mkdir','-p',DIRECTORY);records=[]
 for name,path in paths.items():
  stage=DIRECTORY+'/'+name+'.c11-part';target=DIRECTORY+'/'+name
  with socket.create_connection(('127.0.0.1',5037),timeout=5) as sock,path.open('rb') as src:
   service(sock,'host:transport:'+args.serial);service(sock,f"shell,v2,raw:run-as {PACKAGE} sh -c 'cat > {stage}'")
   row=transfer(sock,src,path.stat().st_size)
  device_bytes=int(command('shell','run-as',PACKAGE,'stat','-c','%s',stage));device_hash=command('shell','run-as',PACKAGE,'sha256sum',stage).split()[0]
  if device_bytes!=row['bytes'] or device_hash!=row['sha256'] or device_hash!=FIXTURES[name][1]:raise IOError('TRANSFER_IDENTITY_MISMATCH_NO_COMMIT')
  command('shell','run-as',PACKAGE,'mv',stage,target)
  if int(command('shell','run-as',PACKAGE,'stat','-c','%s',target))!=device_bytes or command('shell','run-as',PACKAGE,'sha256sum',target).split()[0]!=device_hash:raise IOError('FINAL_IDENTITY_MISMATCH')
  row.update(alias=name,device_bytes=device_bytes,device_sha256=device_hash,serial=args.serial,candidate='D1-20261016-C11',status='PASS_COPY_IDENTITY_ONLY');records.append(row)
  result_path.parent.mkdir(parents=True,exist_ok=True);result_path.write_text(json.dumps(records,indent=2),encoding='utf-8');print(name,row['status'])
if __name__=='__main__':main()
