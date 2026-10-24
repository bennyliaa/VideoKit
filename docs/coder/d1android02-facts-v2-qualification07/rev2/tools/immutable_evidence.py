"""Fixed facts/qualification evidence files, original file handle identity only."""
from pathlib import Path
import ctypes,msvcrt,os,json,time
from contextlib import contextmanager
from ctypes import wintypes as W
from facts_contract import exact,integer,hash_string,sha,enc,dec,EVIDENCE_BYTES,fail
B=Path(__file__).resolve().parents[1]
REF_FIELDS={'path','bytes','sha256','volumeId','fileId'}
ORIGINAL_FILE_EVENTS=[]
FILE_PENDING=[]
@contextmanager
def original_file(path,mode):
 f=Path(path).open(mode);r=dict(path=str(path),mode=mode,original=f,closeEntered=False,closeReturned=False,readOrWriteAmountUnknown=False);ORIGINAL_FILE_EVENTS.append(r)
 try:yield f
 finally:
  r['closeEntered']=True
  try:f.close();r['closeReturned']=True
  except BaseException as e:
   r['error']=type(e).__name__;FILE_PENDING.append(r)
   while True:time.sleep(.1)
class INFO(ctypes.Structure):
 _fields_=[('attributes',W.DWORD),('created',W.FILETIME),('accessed',W.FILETIME),('written',W.FILETIME),('volume',W.DWORD),('sizeHigh',W.DWORD),('sizeLow',W.DWORD),('links',W.DWORD),('indexHigh',W.DWORD),('indexLow',W.DWORD)]
def no_links(path):
 p=Path(path).absolute()
 for q in [p,*p.parents]:
  if q.exists() and q.stat().st_file_attributes&1024:fail('EVIDENCE_REPARSE')
def fixed(path,root,name):
 if type(path) is not str or type(root) is not str:fail('EVIDENCE_PATH_TYPE')
 p=Path(path);r=Path(root)
 if not p.is_absolute() or not r.is_absolute() or str(p)!=str(p.absolute()) or p!=r/name or any(x in ('.','..') for x in path.replace('\\','/').split('/')):fail('EVIDENCE_FIXED_PATH')
 no_links(p)
 if p.absolute()!=p.resolve() or r.absolute()!=r.resolve():fail('EVIDENCE_FIXED_PATH')
 from entry_gates import fixture_root_allowed
 live=Path('D:/CodexProjects/VideoKit/docs/tester/D1_ANDROID02_CAPTURE_EXECUTION')
 if not fixture_root_allowed(str(r)) and not (r.is_relative_to(live) and r.name in ('v2-authority','v2-original-return')):fail('EVIDENCE_ROOT')
 return p
def identity(f,path):
 k=ctypes.WinDLL('kernel32',use_last_error=True);h=W.HANDLE(msvcrt.get_osfhandle(f.fileno()));info=INFO()
 k.GetFileInformationByHandle.argtypes=[W.HANDLE,ctypes.POINTER(INFO)];k.GetFileInformationByHandle.restype=W.BOOL
 k.GetFinalPathNameByHandleW.argtypes=[W.HANDLE,W.LPWSTR,W.DWORD,W.DWORD];k.GetFinalPathNameByHandleW.restype=W.DWORD
 if not k.GetFileInformationByHandle(h,ctypes.byref(info)):raise ctypes.WinError(ctypes.get_last_error())
 buf=ctypes.create_unicode_buffer(32768);n=k.GetFinalPathNameByHandleW(h,buf,32768,0)
 if not 0<n<32768:raise ctypes.WinError(ctypes.get_last_error())
 final=buf.value
 if final.startswith('\\\\?\\'):final=final[4:]
 if Path(final)!=Path(path).absolute() or info.attributes&1024 or info.links!=1:fail('EVIDENCE_HANDLE_PATH_OR_LINKS')
 return dict(volumeId=str(info.volume),fileId=str((info.indexHigh<<32)|info.indexLow),bytes=(info.sizeHigh<<32)|info.sizeLow)
def create(raw,root,name):
 if type(raw) is not bytes or not 1<=len(raw)<=EVIDENCE_BYTES:fail('EVIDENCE_BYTES')
 p=fixed(str(Path(root)/name),str(root),name);p.parent.mkdir(parents=True,exist_ok=True)
 with original_file(p,'xb') as f:
  try:n=f.write(raw)
  except OSError:
   ORIGINAL_FILE_EVENTS[-1]['readOrWriteAmountUnknown']=True;FILE_PENDING.append(ORIGINAL_FILE_EVENTS[-1])
   while True:time.sleep(.1)
  if n!=len(raw):raise IOError('EVIDENCE_SHORT_WRITE')
  try:f.flush()
  except OSError:
   ORIGINAL_FILE_EVENTS[-1]['readOrWriteAmountUnknown']=True;FILE_PENDING.append(ORIGINAL_FILE_EVENTS[-1])
   while True:time.sleep(.1)
  i=identity(f,p)
 if i['bytes']!=len(raw):fail('EVIDENCE_CREATED_SIZE')
 return dict(path=str(p),bytes=len(raw),sha256=sha(raw),volumeId=i['volumeId'],fileId=i['fileId'])
def read(ref,root,name,ledger,cap=EVIDENCE_BYTES):
 exact(ref,REF_FIELDS,'EVIDENCE_REFERENCE_SCHEMA')
 if not integer(ref['bytes'],1,cap) or not hash_string(ref['sha256']) or any(type(ref[k]) is not str or not ref[k].isdigit() for k in ('volumeId','fileId')):fail('EVIDENCE_REFERENCE_TYPE')
 p=fixed(ref['path'],root,name)
 if ledger.get('reads',0)>=64 or ledger.get('reservedBytes',ledger.get('bytes',0))+ref['bytes']+1>268435456:fail('EVIDENCE_SOURCE_READ_BUDGET')
 ledger['reads']=ledger.get('reads',0)+1;ledger['reservedBytes']=ledger.get('reservedBytes',0)+ref['bytes']+1
 with original_file(p,'rb') as f:
  before=identity(f,p)
  if any(before[k]!=ref[k] for k in ('bytes','volumeId','fileId')):fail('EVIDENCE_FILE_IDENTITY')
  try:raw=f.read(ref['bytes']+1)
  except OSError:
   ORIGINAL_FILE_EVENTS[-1]['readOrWriteAmountUnknown']=True;FILE_PENDING.append(ORIGINAL_FILE_EVENTS[-1])
   while True:time.sleep(.1)
  after=identity(f,p)
 ledger['bytes']=ledger.get('bytes',0)+len(raw)
 if before!=after or len(raw)!=ref['bytes'] or sha(raw)!=ref['sha256']:fail('EVIDENCE_ORIGINAL_BYTES')
 return raw
