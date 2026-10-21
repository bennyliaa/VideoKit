"""G execution services: single admission point, native resource vector, durable task records.

No module import starts a process, reads media, or creates a run directory.
"""
from __future__ import annotations
import base64, ctypes, hashlib, hmac, json, os, queue, secrets, struct, subprocess, threading, time, zlib
from contextlib import contextmanager
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
PYTHON=Path(os.sys.executable)
PWSH=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
JAVA=Path('D:/Android/Android Studio/jbr/bin/java.exe')
COORDINATOR='01a107c3-2bf9-7fa0-94a0-234258ca6774'

class Stop(Exception):pass
class Refused(Exception):pass
def need(ok,reason):
    if not ok:raise Refused(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def compact(value):return json.dumps(value,separators=(',',':'),ensure_ascii=True).encode()
def uid():return secrets.token_hex(12)
def pack(fields):return '\t'.join(base64.b64encode(str(x).encode()).decode() for x in fields)
def unpack(line):
    need(len(line)<=8192,'FRAME_LIMIT')
    return [base64.b64decode(x,validate=True).decode() for x in line.split('\t')]

class Native:
    """Only G-owned guard handles. Raw values never enter task journals or protocol responses."""
    def __init__(self,ledger):
        self.ledger=ledger;self.k=ctypes.WinDLL('kernel32',use_last_error=True);self.owned={}
        self.k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint,ctypes.c_void_p];self.k.CreateFileW.restype=ctypes.c_void_p
        self.k.CloseHandle.argtypes=[ctypes.c_void_p];self.k.CloseHandle.restype=ctypes.c_int
        self.k.GetFileInformationByHandle.argtypes=[ctypes.c_void_p,ctypes.c_void_p];self.k.GetFileInformationByHandle.restype=ctypes.c_int
    def open(self,rid,path,row):
        if rid not in self.ledger.live:self.ledger.acquire(rid,'G','media',row)
        handle=self.k.CreateFileW(str(path),0x80000000,1,None,3,0x80,None)
        if handle==ctypes.c_void_p(-1).value:
            self.ledger.release(rid,'OPEN_NOT_ALLOCATED');raise Refused('GUARD_OPEN_FAILED')
        self.owned[rid]=handle
        info=(ctypes.c_uint*13)();need(self.k.GetFileInformationByHandle(handle,ctypes.byref(info)),'GUARD_IDENTITY_UNPROVEN')
        return {'identity':f'{info[7]}:{info[11]}:{info[12]}','length':(info[8]<<32)|info[9],
                'object':uid(),'ticket':uid(),'owner':'G','disposition':'OWNED_OPEN_RETRYABLE','nativeCloses':0}
    def close(self,rid):
        need(rid in self.owned,'GUARD_TICKET_UNKNOWN');handle=self.owned.pop(rid)
        if not self.k.CloseHandle(handle):raise Stop('GUARD_CLOSE_UNKNOWN_NO_RETRY')
        self.ledger.release(rid,'NATIVE_CLOSE_RETURNED');return {'disposition':'CLOSED_PROVEN','nativeCloses':1}

class Ledger:
    def __init__(self):self.lock=threading.RLock();self.live={};self.peak=0;self.media_peak=0;self.buffers=0;self.buffer_peak=0;self.audit=[];self.pending_buffers=[]
    def acquire(self,rid,owner,kind,row=None):
        with self.lock:
            need(rid not in self.live,'DUP_RESOURCE_ID');need(len(self.live)<24,'OS_HANDLE_LIMIT')
            if kind=='media':
                current=sum(x['kind']=='media' for x in self.live.values());need(current<6,'MEDIA_HANDLE_LIMIT')
                if row is not None:need(sum(x['kind']=='media' and x.get('task')==row['task'] for x in self.live.values())<row['mediaHandles'],'ROW_MEDIA_HANDLE_LIMIT')
                self.media_peak=max(self.media_peak,current+1)
            self.live[rid]={'owner':owner,'kind':kind,'task':row['task'] if row else None};self.peak=max(self.peak,len(self.live))
    def release(self,rid,proof):
        with self.lock:
            need(proof in {'NATIVE_CLOSE_RETURNED','OPEN_NOT_ALLOCATED','OWNER_EXIT_PROVEN','THREAD_JOIN_PROVEN','THREAD_NOT_STARTED_PROVEN'},'INVALID_RELEASE_PROOF')
            if proof in {'THREAD_JOIN_PROVEN','THREAD_NOT_STARTED_PROVEN'}:need(rid not in self.live or self.live[rid]['kind']=='worker','INVALID_RELEASE_PROOF')
            if rid in self.live:self.audit.append((rid,proof));del self.live[rid]
    def owner_exit(self,owner,proof,kinds=None):
        need(proof.get('exited') and proof['instance']==owner,'OWNER_EXIT_NOT_PROVEN')
        for rid,entry in list(self.live.items()):
            if entry['owner']==owner and (kinds is None or entry['kind'] in kinds):self.release(rid,'OWNER_EXIT_PROVEN')
        with self.lock:
            count=self.pending_buffers.count(owner);self.buffers-=count;self.pending_buffers=[p for p in self.pending_buffers if p!=owner]
    @contextmanager
    def buffer(self,row,owner='G'):
        with self.lock:need(self.buffers<8 and self.buffers<row['buffers'],'BUFFER_LIMIT');self.buffers+=1;self.buffer_peak=max(self.buffer_peak,self.buffers)
        retained=False
        try:yield
        except Stop:
            retained=True;self.pending_buffers.append(owner);raise
        finally:
            if not retained:
                with self.lock:self.buffers-=1

def empty_usage():return dict(n=0,qn=0,qr=0,ib=0,ic=0,v=0,targets=0,records=0,credit=0)
class Budget:
    def __init__(self,manifest):
        self.lock=threading.RLock();self.rows={r['id']:r for r in manifest['branches']};self.used={};self.taskused={};self.globalused=empty_usage();self.started=time.monotonic();self.ends={}
        self.rows['PF']={'id':'PF','task':'PF','nonquery':16,'queriesNew':0,'queriesReplay':0,'inputBytes':32,'inputCalls':2,'validationBytes':0,'newTargets':0,'newRecords':1,'outputBytes':0,'mediaHandles':3,'buffers':2,'seconds':20}
        self.rows['GC']={'id':'GC','task':'PF','nonquery':32,'queriesNew':0,'queriesReplay':0,'inputBytes':0,'inputCalls':0,'validationBytes':0,'newTargets':0,'newRecords':0,'outputBytes':0,'mediaHandles':6,'buffers':8,'seconds':38}
        self.globalcap=dict(n=351,qn=83,qr=18,ib=1573522,ic=59,v=262144,targets=10,records=32,credit=655360)
    @staticmethod
    def caps(row):return dict(n=row['nonquery'],qn=row['queriesNew'],qr=row['queriesReplay'],ib=row['inputBytes'],ic=row['inputCalls'],v=row['validationBytes'],targets=row['newTargets'],records=row['newRecords'],credit=row['outputBytes'])
    def begin(self,row):
        with self.lock:need(row not in self.ends,'ROW_RESTART_DENIED');self.ends[row]=min(self.started+180,time.monotonic()+self.rows[row]['seconds'])
    def remaining(self,row):return self.ends[row]-time.monotonic()
    def charge(self,row,**charge):
        with self.lock:
            need(self.remaining(row)>0,'ROW_DEADLINE_STOP');spec=self.rows[row];task=spec['task'];ru=self.used.setdefault(row,empty_usage());tu=self.taskused.setdefault(task,empty_usage())
            tc=empty_usage()
            for r in self.rows.values():
                if r['task']==task:
                    for k,v in self.caps(r).items():tc[k]+=v
            for current,cap in [(ru,self.caps(spec)),(tu,tc),(self.globalused,self.globalcap)]:
                for k,v in charge.items():need(k in cap and 0<=v<=cap[k]-current[k],'BUDGET_STOP:'+k)
            for current in [ru,tu,self.globalused]:
                for k,v in charge.items():current[k]+=v
    def restore(self,states):
        self.used={};self.taskused={};self.globalused=empty_usage()
        for state in states:
            for row,used in state.get('usage',{}).items():
                need(row in self.rows and (row not in self.used or row=='GC'),'DUP_OR_UNKNOWN_RECOVERED_ROW');need(set(used)==set(empty_usage()),'RECOVERED_USAGE_SCHEMA')
                cap=self.caps(self.rows[row]);need(all(isinstance(v,int) and 0<=v<=cap[k] for k,v in used.items()),'RECOVERED_ROW_OVERFLOW')
                previous=self.used.get(row,empty_usage());merged={k:max(previous[k],used[k]) for k in used};self.used[row]=merged;task=self.rows[row]['task'];tu=self.taskused.setdefault(task,empty_usage())
                for k,v in merged.items():tu[k]+=v-previous[k];self.globalused[k]+=v-previous[k]
        for k,v in self.globalused.items():need(v<=self.globalcap[k],'RECOVERED_BUDGET_OVERFLOW')

class Store:
    """Every task's admission and completion, including reservations and resource vectors.
    Two 8KiB compressed/checksummed slots; no global write outside the same command's two phases.
    """
    def __init__(self,root,ledger,writer_factory=None):
        self.root=Path(root);self.ledger=ledger;self.seq={};self.requested=0;self.written=0;self.unknown_requested_bytes=0;self.transactions=0;self.peak=0;self.files={};self.lock=threading.RLock();self.native=dict(open=0,write=0,sync=0,close=0,read=0);self.event_bytes={};self.log=None
        # Optional wrappers belong to the independent synthetic check only. Production
        # uses the original unbuffered FileIO object and the identical exact-write gate.
        self.writer_factory=writer_factory;self.commit_status='HEALTHY';self.commit_failures=[]
    def ensure_writable(self):
        if self.commit_status!='HEALTHY':raise Stop('METADATA_COMMIT_UNKNOWN_NO_NEW_EFFECT')
    def exact_write(self,writer,data,label):
        """One bounded request, no repair write. A returned count is not a durability proof."""
        with self.lock:
            self.ensure_writable();need(isinstance(data,bytes) and len(data)<=131072,'METADATA_WRITE_BOUND');requested=len(data)
            self.requested+=requested;self.native['write']+=1
            try:returned=writer.write(data)
            except BaseException as error:
                self.commit_status='UNKNOWN';self.unknown_requested_bytes+=requested
                self.commit_failures.append(dict(label=label,requested=requested,returned=None,reason='WRITE_RAISED',error=type(error).__name__))
                raise Stop('METADATA_WRITE_UNKNOWN_NO_REPAIR') from error
            valid=type(returned) is int and 0<=returned<=requested
            if valid:self.written+=returned
            else:self.unknown_requested_bytes+=requested
            if not valid or returned!=requested:
                self.commit_status='UNKNOWN';self.commit_failures.append(dict(label=label,requested=requested,returned=returned if type(returned) in (int,str,type(None),bool) else type(returned).__name__,reason='SHORT_WRITE' if valid else 'INVALID_WRITE_RETURN'))
                raise Stop('METADATA_SHORT_OR_INVALID_WRITE_NO_REPAIR')
            return returned
    def sync(self,writer):
        self.ensure_writable();self.native['sync']+=1
        try:writer.flush();os.fsync(writer.fileno())
        except BaseException as error:
            self.commit_status='UNKNOWN';raise Stop('METADATA_SYNC_UNKNOWN_NO_NEW_EFFECT') from error
    def reserve_file(self,path,cap):
        key=str(path.relative_to(self.root));old=self.files.get(key,0);need(old in (0,cap),'FILE_CAP_CONFLICT');self.files[key]=cap
        need(sum(self.files.values())<=3178496,'FILE_PEAK_CREDIT_LIMIT')
    def observe(self):
        actual=sum((self.root/p).stat().st_size for p in self.files if (self.root/p).exists());self.peak=max(self.peak,actual);need(actual<=3178496,'FILE_PEAK_LIMIT')
    @contextmanager
    def file(self,path,mode,cap):
        file,rid=self._open_file(path,mode,cap)
        try:yield file
        finally:self._close_file(file,rid)
    def _open_file(self,path,mode,cap,rid=None):
        self.ensure_writable()
        need(path.is_relative_to(self.root),'METADATA_ROOT')
        for part in [path,*path.parents]:
            if part==self.root.parent:break
            need(not part.is_symlink() and not part.is_junction(),'REPARSE_METADATA_DENIED')
        self.reserve_file(path,cap);path.parent.mkdir(parents=True,exist_ok=True);rid=rid or 'metadata/'+uid();self.ledger.acquire(rid,'G','metadata');self.native['open']+=1
        try:raw=open(path,mode,buffering=0)
        except BaseException as error:
            self.ledger.release(rid,'OPEN_NOT_ALLOCATED');self.commit_status='UNKNOWN'
            raise Stop('METADATA_OPEN_FAILED_NO_NEW_EFFECT') from error
        try:file=self.writer_factory(raw,path,mode) if self.writer_factory else raw
        except BaseException as error:
            # The real open succeeded; close that original object once even if a
            # self-owned test wrapper could not be created. Never refund as unopened.
            self.commit_status='UNKNOWN';self._close_file(raw,rid)
            raise Stop('METADATA_WRAPPER_SETUP_FAILED_NO_NEW_EFFECT') from error
        return file,rid
    def _close_file(self,file,rid):
        self.native['close']+=1
        try:file.close()
        except BaseException as error:
            self.commit_status='UNKNOWN';raise Stop('METADATA_CLOSE_UNKNOWN_NO_RETRY') from error
        self.ledger.release(rid,'NATIVE_CLOSE_RETURNED');self.observe()
    def open_log(self,banner):
        file,rid=self._open_file(self.root/'global.log','wb',131072,'global-log')
        try:self.exact_write(file,banner,'GLOBAL_SETUP')
        except BaseException:
            self._close_file(file,rid);raise
        self.log=file;return file
    def close_log(self):
        need(self.log is not None,'GLOBAL_LOG_NOT_OPEN');self.sync(self.log);self._close_file(self.log,'global-log');self.log=None
    def write_receipt(self,data):
        need(len(data)<=131072,'FINAL_RECEIPT_LIMIT')
        with self.file(self.root/'result-before-close.json','wb',131072) as file:
            self.exact_write(file,data,'FINAL_PRECLOSE_RECEIPT');self.sync(file)
    def save(self,task,state):
        with self.lock:
            encoded=compact(state);need(len(encoded)<=65536,'LOGICAL_RECORD_LIMIT');payload=zlib.compress(encoded,6);need(len(payload)<=8144,'SNAPSHOT_LIMIT')
            seq=self.seq.get(task,0)+1;header=struct.pack('<qiI',seq,len(payload),0);record=header+hashlib.sha256(header+payload).digest()+payload;record=record.ljust(8192,b'\0')
            path=self.root/task/f'state{seq%2}.slot'
            with self.file(path,'wb',8192) as f:
                self.exact_write(f,record,'SNAPSHOT:'+task);self.sync(f)
            self.seq[task]=seq;self.transactions+=1
    @staticmethod
    def decode_record(raw):
        need(len(raw)==8192,'JOURNAL_CORRUPT');seq,n,_=struct.unpack('<qiI',raw[:16]);need(seq>0 and 0<=n<=8144,'JOURNAL_CORRUPT');payload=raw[48:48+n]
        need(hmac.compare_digest(hashlib.sha256(raw[:16]+payload).digest(),raw[16:48]),'JOURNAL_CORRUPT');return seq,Store.inflate(payload)
    @staticmethod
    def inflate(payload):
        d=zlib.decompressobj();data=d.decompress(payload,65537);need(len(data)<=65536 and d.eof,'JOURNAL_LOGICAL_LIMIT');return json.loads(data)
    def load(self,task):
        found=[]
        for slot in range(2):
            path=self.root/task/f'state{slot}.slot'
            if path.exists():
                with self.file(path,'rb',8192) as f:self.native['read']+=1;found.append(self.decode_record(f.read(8193)))
        need(found,'JOURNAL_UNKNOWN');seq,state=max(found,key=lambda x:x[0]);self.seq[task]=seq;return state
    def event(self,row,event,query=False):
        data=compact(event)+b'\n';need(len(data)<=1024,'EVENT_LIMIT');path=self.root/'events'/f'{row}.{"q" if query else "ops"}'
        cap=8192 if query else 24576
        if not query and self.log is not None:
            with self.lock:
                current=self.event_bytes.get(row,0);need(current+len(data)<=cap,'ROW_LOG_LIMIT')
                need(self.log.tell()+len(data)<=131072,'GLOBAL_EVENT_LOG_LIMIT')
                self.exact_write(self.log,data,'GLOBAL_EVENT:'+row);self.event_bytes[row]=current+len(data)
            return
        need((path.stat().st_size if path.exists() else 0)+len(data)<=cap,'ROW_LOG_LIMIT')
        with self.file(path,'ab',cap) as f:
            self.exact_write(f,data,('QUERY_EVENT:' if query else 'ROW_EVENT:')+row)
            if query:self.sync(f)
    def reload_queries(self,task,rows):
        cache={}
        for row in rows:
            if row['task']!=task:continue
            p=self.root/'events'/f'{row["id"]}.q'
            if p.exists():
                with self.file(p,'rb',8192) as f:
                    self.native['read']+=1;raw=f.read(8193);need(len(raw)<=8192,'QCACHE_LIMIT')
                for line in raw.splitlines():
                    e=json.loads(line)
                    if e.get('new'):cache[e['qid']]=e['view']
        return cache

class Channel:
    def __init__(self,name,root,key,ledger):
        self.name=name;self.key=key;self.ledger=ledger;self.lock=threading.RLock();self.q=queue.Queue(maxsize=8);self.unknown=False;self.owner=None;self.proof=None;self.root=root
        env=os.environ.copy();env['E2_KEY']=base64.b64encode(key).decode()
        args=[str(JAVA),'-cp',str(BASE/'artifacts/java'),'videokit.e1.JavaHelper','--admitted-helper',str(root)] if name=='J' else [str(PWSH),'-NoProfile','-NonInteractive','-File',str(BASE/'tools/r-helper.ps1'),'-FixtureRoot',str(root)]
        for suffix in ['in-parent','in-child','out-parent','out-child','err-parent','err-child','process']:ledger.acquire(name+'/'+suffix,name if suffix.endswith('child') else 'G','pipe' if suffix!='process' else 'process')
        self.process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,creationflags=subprocess.CREATE_NO_WINDOW,bufsize=0)
        self.started=time.time_ns();self.pid=self.process.pid
        def read():
            try:
                while True:
                    line=self.process.stdout.readline(8194)
                    if not line:break
                    need(len(line)<=8193,'CHILD_FRAME_LIMIT');self.q.put(line.decode().rstrip('\r\n'),timeout=3)
            except Exception as e:self.q.put(e)
        self.reader=threading.Thread(target=read,name=name+'-response',daemon=True);self.reader.start()
        def drain():
            while self.process.stderr.read(256):pass
        self.drainer=threading.Thread(target=drain,name=name+'-stderr',daemon=True);self.drainer.start()
    def _send(self,fields):
        body=pack(fields);raw=body+'\t'+hmac.new(self.key,body.encode(),hashlib.sha256).hexdigest();need(len(raw)<=8192,'FRAME_LIMIT');self.process.stdin.write((raw+'\n').encode());self.process.stdin.flush()
    def call(self,id,verb,row,task,epoch,claim,kind,args=(),timeout=3,callback=None):
        with self.lock:
            need(not self.unknown,'TRANSPORT_UNKNOWN_NO_NEW_IO');self._send([id,verb,row,task,epoch,claim,kind,*args]);end=time.monotonic()+timeout
            while True:
                try:raw=self.q.get(timeout=max(.001,end-time.monotonic()))
                except queue.Empty:self.unknown=True;raise Stop('TRANSPORT_PENDING_RETAIN_OPERATION')
                if isinstance(raw,Exception):self.unknown=True;raise Stop('CHILD_PROTOCOL_UNKNOWN')
                fields=unpack(raw)
                if fields[0]=='CALLBACK':
                    need(callback is not None and fields[1]==id,'UNEXPECTED_CALLBACK');answer=callback(fields[2],int(fields[3]),base64.b64decode(fields[4]));self._send([id+'/callback','QUERY_RESULT',row,task,epoch,'','Q',json.dumps(answer,separators=(',',':'))]);continue
                need(fields[0]==id,'RESPONSE_IDENTITY');need(fields[1]=='OK',fields[2]);return json.loads(fields[2]) if self.name=='R' else fields[2]
    def exited(self):
        try:code=self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:raise Stop('OWNER_EXIT_PENDING')
        need(code==0 and self.owner is not None,'OWNER_EXIT_UNPROVEN');self.proof=dict(instance=self.owner,pid=self.pid,started=self.started,observed=time.time_ns(),code=code,exited=True)
        self.reader.join(1);self.drainer.join(1);need(not self.reader.is_alive() and not self.drainer.is_alive(),'TRANSPORT_THREADS_PENDING')
        for suffix in ['in-child','out-child','err-child']:self.ledger.release(self.name+'/'+suffix,'OWNER_EXIT_PROVEN')
        return self.proof
    def close_pipe(self,which):
        stream={'in':self.process.stdin,'out':self.process.stdout,'err':self.process.stderr}[which];stream.close();self.ledger.release(self.name+'/'+which+'-parent','NATIVE_CLOSE_RETURNED')
    def close_process_handle(self):
        need(self.proof and self.proof['exited'],'PROCESS_NOT_EXITED');handle=int(self.process._handle);k=ctypes.WinDLL('kernel32',use_last_error=True);k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
        need(k.CloseHandle(handle),'PROCESS_HANDLE_CLOSE_UNKNOWN');self.process._handle.Detach();self.ledger.release(self.name+'/process','NATIVE_CLOSE_RETURNED')
