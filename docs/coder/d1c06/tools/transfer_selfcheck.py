"""Exercises production framing against an in-memory protocol peer, never connects sockets or invokes ADB."""
import io,hashlib,struct,threading,json,sys
from pathlib import Path
from transfer_fixtures import transfer,CHUNK
class Peer:
 def __init__(self,exit_code=0,oversized=False):self.sha=hashlib.sha256();self.total=0;self.max_frame=0;self.finished=threading.Event();self.reply=struct.pack('<BI',3,1)+bytes([exit_code]);self.closed=False;self.oversized=oversized
 def sendall(self,data):
  channel,n=struct.unpack('<BI',data[:5]);assert len(data)==5+n
  if channel==0:self.sha.update(data[5:]);self.total+=n;self.max_frame=max(self.max_frame,n)
  else:assert channel==4 and n==0;self.finished.set()
 def recv(self,n):
  self.finished.wait(30)
  if self.closed:return b''
  if self.oversized:self.reply=struct.pack('<BI',1,CHUNK+1);self.oversized=False
  take=min(n,3,len(self.reply));v=self.reply[:take];self.reply=self.reply[take:];return v
 def close(self):self.closed=True;self.finished.set()
class GeneratedBinary:
 def __init__(self,size):self.left=size;self.read_bound=0
 def read(self,n):
  assert 0<n<=CHUNK;self.read_bound=max(self.read_bound,n);size=min(n,self.left);self.left-=size;return (bytes(range(256))*(size//256+1))[:size]
passed=[]
def check(value,label):assert value,label;passed.append(label);print('PASS',label)
peer=Peer();control=bytes(range(256))*257;row=transfer(peer,io.BytesIO(control),len(control),30)
check(row['sha256']==hashlib.sha256(control).hexdigest()==peer.sha.hexdigest() and peer.total==len(control),'all 256 binary byte values and fragmented frame response preserved')
size=2**31+12345;peer=Peer();stream=GeneratedBinary(size);row=transfer(peer,stream,size,120)
check(peer.total==row['bytes']==size and row['sha256']==peer.sha.hexdigest(),'actual generated 2GiB+12345 binary bytes streamed and hashed, 64-bit totals')
check(peer.max_frame<=CHUNK and stream.read_bound==CHUNK,'bounded 32KiB reads and payloads, no file-sized buffering')
for peer,data,expected,label,code in [(Peer(9),b'abc',3,'nonzero remote exit rejected','REMOTE_WRITE_FAILED'),(Peer(oversized=True),b'abc',3,'oversized remote frame rejected','ADB_FRAME_BUDGET_OR_CHANNEL'),(Peer(),b'abc',4,'truncated source rejected','SOURCE_LENGTH_CHANGED')]:
 try:transfer(peer,io.BytesIO(data),expected,30);raise AssertionError(label)
 except IOError as e:check(str(e)==code,label)
result={'status':'PASS','assertions':len(passed),'checks':passed,'streamed_large_bytes':size,'max_read_and_payload':CHUNK,'transport':'in-memory production framing peer; no device/socket execution','device_execution':'NOT_RUN'}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
