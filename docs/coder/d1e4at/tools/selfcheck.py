"""One bounded local batch against the production pump/workflow. All subprocesses are owned fakes."""
from pathlib import Path
from dataclasses import asdict
import hashlib
import io
import json
import os
import shlex
import sys
import time
from exact_process import Limits,collect,transfer_file,stdout_bytes,write_all,installation_success,retained_owners
from fixture_transfer import FileProof,AdbBackend,provision_once,run_as_argv,probe_script,rename_script,receive_script,fixture_path

BASE=Path(__file__).resolve().parents[1]
CHILD=BASE/'tools/fake_child.py'
ASSERTIONS=0
COMMANDS=[]
CASES=[]
def check(ok,name):
    global ASSERTIONS
    ASSERTIONS+=1
    if not ok:raise AssertionError(name)
def rejects(error,action):
    try:action()
    except error:check(True,'expected rejection');return
    raise AssertionError('missing rejection')
def sha(data):return hashlib.sha256(data).hexdigest()

class LocalBackend:
    execution_authorized=True
    def __init__(self,root,behavior='exact',limits=None):self.root=root;self.behavior=behavior;self.logs=[];self.limits=limits or Limits(timeout=5)
    def argv(self,mode,path=None,*extra):
        result=[sys.executable,'-X','utf8','-B','-u',str(CHILD),mode,'--root',str(self.root)]
        if path is not None:result+=['--target',path]
        return result+list(extra)
    def run(self,argv):
        result=collect(argv,Limits(timeout=5));self.logs.append(result);COMMANDS.append(result);return stdout_bytes(result)
    def exists(self,path):
        result=json.loads(self.run(self.argv("probe",path,"--behavior","metadata")));return not result.get("absent",False)
    def probe(self,path,cap=1048576):
        result=json.loads(self.run(self.argv('probe',path,"--cap",str(cap))))
        return None if result.get('absent') else FileProof(result['length'],result['sha256'])
    def rename(self,source,target):self.run(self.argv('rename',source,'--destination',target))
    def receive(self,path,source,expected):
        result=transfer_file(self.argv('receive',path,'--behavior',self.behavior),source,expected.length,expected.sha256,self.limits);self.logs.append(result);COMMANDS.append(result);return result

def main():
    if len(sys.argv)!=2:raise ValueError('owned evidence output directory required')
    root=Path(sys.argv[1]).resolve()
    if not root.is_relative_to(BASE/'evidence') or root.exists():raise ValueError('new owned evidence root only')
    root.mkdir();(root/'.owned-fixture-root').write_text('E4AT_OWNED_FAKE_FILES_ONLY')
    pattern=bytes(range(256))*1363+bytes(range(174))
    check(len(pattern)==349102,'exact requested pattern length')
    source=root/'source 目录 with spaces.bin';source.write_bytes(pattern);expected=FileProof(len(pattern),sha(pattern))
    def case(name,behavior='exact',limits=None):
        path=root/name;path.mkdir();(path/'.owned-fixture-root').write_text('E4AT_OWNED_FAKE_FILES_ONLY');(path/'files/e4_fixtures').mkdir(parents=True);return path,LocalBackend(path,behavior,limits)
    def provision(name,behavior='exact',residual=False,limits=None):
        path,backend=case(name,behavior,limits);final='files/e4_fixtures/basic.bin';temp='files/e4_fixtures/.basic-'+name+'.part';archive='files/e4_fixtures/basic-residual.keep';old=None
        if residual:
            data=pattern[:81407];(path/final).write_bytes(data);old=FileProof(len(data),sha(data))
        result=provision_once(backend,source,expected,final,temp,path/'receipts',attempt_id='owned_'+name,residual=old,archive_path=archive if residual else None)
        CASES.append(dict(case=name,result=result));return path,backend,result,final,temp,archive
    path,backend,result,final,temp,archive=provision('exact_residual',residual=True)
    check(result['status']=='FIXTURE_ADMITTED','independent full data admits')
    check((path/final).read_bytes()==pattern and not (path/temp).exists(),'full binary bytes including NUL CR LF SUB FF')
    check((path/archive).read_bytes()==pattern[:81407],'original residual preserved through rename')
    check(result['transfer']['submittedBytes']==349102 and result['transfer']['originalExitCode']==0,'actual submit and original exit recorded')
    check(result['transfer']['flushReturned'] and result['transfer']['stdinCloseReturned'] and result['transfer']['sourceCloseReturned'],'explicit close/flush returned')
    check(result['events'][-1]['stage']=='SAME_DIRECTORY_PUBLISH_VERIFIED','independent post-publish proof')
    before=len(COMMANDS)
    rejects(FileExistsError,lambda:provision_once(backend,source,expected,final,temp,path/'receipts',attempt_id='owned_exact_residual'))
    check(len(COMMANDS)==before,'attempt reservation blocks a second transfer')
    for behavior in ['exit0-truncate','exit0-corrupt','text-eof-example']:
        name=behavior.replace('-','_');path,backend,result,final,temp,archive=provision(name,behavior)
        check(result['status']=='NOT_ADMITTED' and result['firstFailure']=='INDEPENDENT_LANDED_LENGTH_OR_SHA_MISMATCH','exit0 partial/corrupt independently denied')
        check(result['transfer']['originalExitCode']==0 and result['transfer']['submittedBytes']==349102,'exit0 full submission is insufficient')
        check((path/temp).exists() and not (path/final).exists(),'partial temp retained without publishing')
        check(sum('receive' in cmd['argv'] for cmd in backend.logs)==1,'one actual producer, never retry')
        if behavior=='exit0-truncate':check((path/temp).stat().st_size==81407,'requested exit0 truncation example retained')
        if behavior=='exit0-corrupt':check((path/temp).stat().st_size==349102,'correct length with wrong SHA denied')
    path,backend,result,final,temp,archive=provision('exit0_grow','exit0-grow')
    check(result['status']=='NOT_ADMITTED' and (path/temp).stat().st_size==349103,'oversize landing retained without publish')
    oversized=backend.logs[-1];check(oversized['originalExitCode']==43 and json.loads(bytes.fromhex(oversized['stdout']['prefixHex']))['readBytes']==0,'independent length gate refuses hash read before oversize bytes')
    for behavior in ['early','nonzero','hang','overcap']:
        limits=Limits(timeout=.65 if behavior=='hang' else 5,cleanup=2,stdout_cap=131072 if behavior=='overcap' else 1048576)
        start=time.monotonic();path,backend,result,final,temp,archive=provision('negative_'+behavior,behavior,limits=limits)
        check(result['status']=='NOT_ADMITTED' and result['firstFailure']=='TRANSFER_PROCESS_NOT_COMPLETE','failed original process never admitted')
        check((path/temp).exists() and not (path/final).exists(),'failed process leaves partial original')
        check(result['transfer']['ownership']=='RETURNED','owned fake child/pipes actually returned')
        check(sum('receive' in cmd['argv'] for cmd in backend.logs)==1,'no retry on process failure')
        if behavior=='nonzero':check(result['transfer']['originalExitCode']==19,'original nonzero retained')
        if behavior=='hang':check(time.monotonic()-start<4.5 and result['transfer']['terminatedOwnedChild'],'bounded stop of own hanging fake child')
        if behavior=='overcap':check('PROCESS_OUTPUT_BUDGET' in result['transfer']['errors'] and result['transfer']['stdout']['bytes']<=131072+16384,'bounded actual drain count and stored prefix')
    path,backend,result,final,temp,archive=provision('stdout_pressure','pressure')
    check(result['status']=='FIXTURE_ADMITTED','concurrent stdout and stderr pressure without deadlock')
    check(result['transfer']['stdout']['bytes']==262144 and result['transfer']['stderr']['bytes']==131072,'both drains continuously consumed')
    path,backend=case('no_overwrite');final='files/e4_fixtures/basic.bin';temp='files/e4_fixtures/.exists.part';(path/temp).write_bytes(b'keep')
    result=provision_once(backend,source,expected,final,temp,path/'receipts',attempt_id='owned_no_overwrite');CASES.append(dict(case='no_overwrite',result=result))
    check(result['status']=='NOT_ADMITTED' and result['firstFailure']=='TEMP_ALREADY_EXISTS_NO_OVERWRITE','no overwrite of old temp')
    check((path/temp).read_bytes()==b'keep' and not any('receive' in cmd['argv'] for cmd in backend.logs),'existing temp preserved without producer')
    check(json.loads(bytes.fromhex(backend.logs[-1]['stdout']['prefixHex']))['readBytes']==0,'existence check is metadata-only, never full hash of old temp')
    path,backend=case('bad_source');bad=FileProof(349102,'0'*64)
    result=transfer_file(backend.argv('receive','files/e4_fixtures/new.part'),source,bad.length,bad.sha256,Limits(timeout=5));COMMANDS.append(result)
    check(result['status']=='NOT_ADMITTED' and result['firstError']=='SOURCE_PREHASH_MISMATCH','complete source identity required before launch')
    check(not (path/'files/e4_fixtures/new.part').exists(),'prehash rejection never launches producer')
    class ShortWriter:
        def __init__(self):self.data=bytearray()
        def write(self,data):n=min(3,len(data));self.data.extend(data[:n]);return n
    short=ShortWriter();credited=bytearray();write_all(short,pattern,credited.extend)
    check(bytes(short.data)==pattern and bytes(credited)==pattern,'production write-all handles positive short writes exactly once')
    class ZeroWriter:
        def write(self,data):return 0
    rejects(IOError,lambda:write_all(ZeroWriter(),b'owned',lambda x:None))
    actual=(BASE/'reference/07-install-app-debug.apk.txt').read_bytes()
    check(installation_success(0,actual),'actual recorded banner+Success parsed without new install')
    for code,out,err,want in [(0,b'Success\r\n',b'',True),(0,b'Performing Push Install\nSuccess\n',b'',True),(1,b'Success\n',b'',False),(0,b'NotSuccess\n',b'',False),(0,b'Failure [X]\nSuccess\n',b'',False),(0,b'Success\n',b'error',False),(0,b'',b'',False)]:check(installation_success(code,out,err)==want,'finished install prompt exact lines')
    script="pwd; printf '%s\\n' 'with spaces'; test -d files/e4_fixtures"
    argv=run_as_argv('D:/SDK with spaces/adb.exe','HA1Q6WXR','shell',script)
    check(shlex.split(' '.join(argv[4:]))==['run-as','com.videokit.app','sh','-c',script],'entire remote script stays in run-as scope')
    generated=probe_script('files/e4_fixtures/basic.mp4',349102)
    check(generated.index(' -le 349102')<generated.index('sha256sum'),'actual remote hash is preceded by declared length cap')
    check('sha256sum' not in probe_script('files/e4_fixtures/basic.mp4',0,True),'metadata-only generated command contains no content hash')
    check(shlex.split(' '.join(run_as_argv('D:/SDK/adb.exe','HA1Q6WXR','shell',generated)[4:]))[-1]==generated,'generated nested quote script remains single original argument')
    for value in ['files/e4_fixtures/../escape','files/e4_fixtures/a;touch_bad','files/e4_fixtures/a\'b','/data/escape']:
        rejects(ValueError,lambda value=value:fixture_path(value))
    path,backend=case('argv');sent=['C:\\a folder\\尾部\\','quote"inside','SUB\x1aNUL-is-not-argv','plain space']
    raw=backend.run(backend.argv('argv',None,'--',*sent));check(json.loads(raw)==sent,'Windows process argv spaces unicode quotes trailing slash exact')
    denied=AdbBackend('D:/NotExecuted/adb.exe','HA1Q6WXR')
    rejects(PermissionError,lambda:denied.probe('files/e4_fixtures/basic.mp4'))
    check(retained_owners()==0,'all local fake jobs returned; no pending child/thread owner')
    result=dict(schema=1,scope='E4AT_OWNED_BINARY_FAKE_PROCESSES_ONLY',status='PASS',assertions=ASSERTIONS,commands=len(COMMANDS),cases=CASES,
                realMediaStat=0,realMediaBytesRead=0,adbCalls=0,deviceRuns=0,gradleRuns=0,downloads=0,retainedProcessOwners=retained_owners(),sourcePattern=dict(bytes=len(pattern),sha256=expected.sha256),processes=COMMANDS)
    (root/'selfcheck-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:result[key] for key in ['scope','status','assertions','commands','adbCalls','deviceRuns','gradleRuns','realMediaBytesRead','retainedProcessOwners']},sort_keys=True))

if __name__=='__main__':main()
