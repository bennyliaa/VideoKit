"""One finite, offline production-parser regression. No child process, ADB, media or dependency access."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
from datetime import datetime,timezone
import exact_process as ep
from command_response import complete_stdout,parse_features
from diagnose_once import run_diagnostic,BASE,PAYLOAD_SHA
from remote_command import Context,HISTORY

ROOT=BASE.parents[2]
rows=[]
def check(value,name):
    rows.append(dict(name=name,passed=bool(value)))
    if not value:raise AssertionError(name)

def reject(function,name):
    try:function()
    except (ValueError,UnicodeError,KeyError,IOError):check(True,name)
    else:check(False,name)

def identity(path):
    raw=path.read_bytes();return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

def synthetic(raw):
    r=deepcopy(ORIGINAL)
    r['argv']=['OFFLINE_SYNTHETIC_RESPONSE_ONLY']
    r['stdout'].update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),prefixHex=raw.hex(),prefixTruncated=False)
    return r

ORIGINAL=json.loads((BASE/'reference/features-record.json').read_text('utf-8'))

class OfflineTransport:
    adb='OFFLINE_NO_PROCESS'
    def __init__(self,feature_record,full=False):self.feature_record=feature_record;self.full=full;self.stages=[]
    def command(self,argv):
        n=len(self.stages);self.stages.append(argv)
        if n==0:return deepcopy(self.feature_record)
        if not self.full:raise RuntimeError('OFFLINE_STOP_AFTER_FEATURE_ADMISSION')
        c=Context()
        bodies={
            1:f'E4T2_CONTEXT|{c.nonce}|uid={c.uid}|pwd={c.pwd}\r\n',
            2:f'E4T2_PS|{c.nonce}|self=123\r\n  PID PPID UID ARGS\r\n  123 1 {c.uid} sh -c synthetic\r\n',
            3:'\r\n'.join('E4T2_LSTAT|'+p+'|rc=1|SYNTHETIC_UNINTERPRETED_ERROR' for p in HISTORY)+'\r\n',
            4:f'E4T2_DIRECTORY|{c.nonce}|path={c.directory}\r\n',
            6:f'E4T2_PROOF|{c.nonce}|uid={c.uid}|pwd={c.pwd}|path={c.target}|bytes=256|sha={PAYLOAD_SHA}\r\n',
        }
        return synthetic(bodies[n].encode('ascii'))
    def receive(self,argv,payload):
        if not self.full:raise AssertionError('NO_PAYLOAD_ALLOWED_IN_FEATURE_CASE')
        self.stages.append(argv);c=Context()
        begin=f'E4T2_BEGIN|{c.nonce}|uid={c.uid}|pid=123|pwd={c.pwd}|path={c.target}\r\n'
        end=f'E4T2_END|{c.nonce}|uid={c.uid}|pid=123|pwd={c.pwd}|path={c.target}|bytes=256\r\n'
        r=synthetic((begin+end).encode('ascii'));r['submittedBytes']=256
        return r # Deliberately no payload open or remote filesystem; parser contract only.

def main():
    destination=BASE/'evidence/local-check-results.json'
    if destination.exists() or (BASE/'evidence/features-freeze.json').exists():raise ValueError('ONE_NEW_LOCAL_CHECK_ONLY')
    began=datetime.now(timezone.utc).isoformat();inputs=[identity(BASE/'tools'/n) for n in ['exact_process.py','remote_command.py','diagnose_once.py','command_response.py','check_features.py']]
    original=(BASE/'reference/features-original-stdout.txt').read_bytes()
    check(len(original)==220 and hashlib.sha256(original).hexdigest()=='05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce','tester exact original220B identity')
    check(complete_stdout(ORIGINAL)==original,'original receipt length SHA and return gate')
    check('shell_v2' in parse_features(complete_stdout(ORIGINAL)),'real220B CRLF original admitted')
    check('shell_v2' not in original.decode('ascii').strip().split(','),'old comma-only parser false rejection reproduced offline')
    positives=[('LF',original.replace(b'\r\n',b'\n')),('comma',b'cmd,shell_v2,stat_v2'),('mixed',b'cmd,\r\nshell_v2\nstat_v2,abb\r\n'),('single',b'shell_v2'),('duplicate',b'shell_v2,shell_v2\n')]
    for name,raw in positives:check('shell_v2' in parse_features(complete_stdout(synthetic(raw))),name+' exact feature admitted')
    for raw in [b'cmd,stat_v2',b'shell_v20',b'noshell_v2',b'shell_v2_extra',b'SHELL_V2',b'xshell_v2,shell_v20']:
        check('shell_v2' not in parse_features(complete_stdout(synthetic(raw))),'similar or absent token refused: '+repr(raw))
    for raw in [b'',b'\xffshell_v2',b'shell_v2\x00',b'shell_v2\rcmd',b'shell_v2 cmd',b' shell_v2\n',b'shell_v2\tcmd',b'\xef\xbb\xbfshell_v2']:
        reject(lambda raw=raw:parse_features(complete_stdout(synthetic(raw))),'invalid feature bytes refuse: '+repr(raw))
    def changed(key,value):
        r=deepcopy(ORIGINAL);r[key]=value;return r
    bads=[changed('status','NOT_ADMITTED'),changed('ownership','UNKNOWN_RETAINED'),changed('originalExitCode',1),changed('originalExitObserved',False),changed('firstError','PROCESS_TIMEOUT'),changed('errors',['PROCESS_TIMEOUT']),changed('creationUnknown',True)]
    for field in ['flushReturned','stdinCloseReturned','sourceCloseReturned','writerReturned']:bads.append(changed(field,False))
    bads.append(changed('stdinCloseError','close threw'))
    for side in ['stdout','stderr']:
        for key,value in [('prefixTruncated',True),('closeReturned',False),('error','unknown'),('bytes',999),('sha256','0'*64),('prefixHex','zz')]:
            r=deepcopy(ORIGINAL);r[side][key]=value;bads.append(r)
    r=deepcopy(ORIGINAL);r['stdout']['prefixHex']=original[:-1].hex();bads.append(r)
    r=deepcopy(ORIGINAL);r['stderr'].update(bytes=1,prefixHex='78',sha256=hashlib.sha256(b'x').hexdigest());bads.append(r)
    for i,r in enumerate(bads):reject(lambda r=r:parse_features(complete_stdout(r)),f'bad original receipt gate {i:02d}')
    integrations=[]
    cases=[('original220',deepcopy(ORIGINAL),True),('LF',synthetic(positives[0][1]),True),('comma',synthetic(positives[1][1]),True),('mixed',synthetic(positives[2][1]),True),('similar',synthetic(b'shell_v20,noshell_v2'),False),('truncated',bads[-2],False),('stderr',bads[-1],False)]
    for name,r,admitted in cases:
        t=OfflineTransport(r);result=run_diagnostic(t,BASE/'evidence'/('offline-'+name),authorized=True)
        check(len(t.stages)==(2 if admitted else 1) and result['producerAttempts']==0,'production flow feature admission '+name)
        check(result['status']=='NOT_ADMITTED' and result['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED','offline stop and old ownership '+name)
        integrations.append(dict(case=name,syntheticCalls=len(t.stages),result=result))
    t=OfflineTransport(ORIGINAL,full=True);result=run_diagnostic(t,BASE/'evidence/offline-other-command-formats',authorized=True)
    check(result['status']=='SYNTHETIC_DIAGNOSTIC_VERIFIED_NOT_A_MEDIA_FIXTURE','own CRLF context directory receiver proof formats parse in production')
    check(result['metadataCommands']==6 and result['producerAttempts']==1,'production command plan remains6 plus1 synthetic calls')
    check('SYNTHETIC_UNINTERPRETED_ERROR' in result['historicalExactLstat'] and result['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED','lstat errors and process snapshot do not clear old unknown')
    integrations.append(dict(case='synthetic-other-formats-not-device',syntheticCalls=len(t.stages),result=result))
    check(ep.retained_owners()==0,'no retained real local process owner')
    out=dict(schema=1,status='PASS',scope='OFFLINE_T3_PRODUCTION_PARSER_ONLY',attempt='main-001',beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),assertions=len(rows),checks=rows,inputs=inputs,original=identity(BASE/'reference/features-original-stdout.txt'),integrations=integrations,adbCalls=0,processStarts=0,deviceRuns=0,realMediaBytesRead=0,gradleRuns=0,legacy43Repeated=False,legacy63Repeated=False,legacy72Repeated=False,retainedLocalOwners=0,sourcePayloadBytesRead=0)
    with destination.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(status=out['status'],assertions=out['assertions'],processStarts=0,adbCalls=0,deviceRuns=0)))
if __name__=='__main__':main()
