"""One targeted local batch: original argv replay, actual Git sh, and the production diagnostic."""
from pathlib import Path
import hashlib
import json
import os
import shlex
import sys
from dataclasses import replace
import exact_process as ep
from remote_command import *
from diagnose_once import run_diagnostic,PAYLOAD_SHA,LIMITS

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2];SH='C:/Program Files/Git/usr/bin/sh.exe'
ASSERTIONS=0;CALLS=[]
def check(value,why):
    global ASSERTIONS
    ASSERTIONS+=1
    if not value:raise AssertionError(why)
def row(p):
    data=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
class LocalTransport:
    adb='MODEL_NOT_ADB'
    def __init__(self,root,variant='normal'):self.root=root;self.variant=variant;self.records=[];self.sequence=0
    def mapped(self,argv):
        trace=self.root/f'trace-{self.sequence:02d}.json';self.sequence+=1
        return [sys.executable,'-X','utf8','-B',str(BASE/'tools/fake_aosp_client.py'),'--root',str(self.root),'--trace',str(trace),'--variant',self.variant,'--',*argv[1:]]
    def command(self,argv):
        result=ep.collect(self.mapped(argv),LIMITS);self.records.append(result);CALLS.append(result);return result
    def receive(self,argv,payload):
        result=ep.transfer_file(self.mapped(argv),payload,256,PAYLOAD_SHA,LIMITS);self.records.append(result);CALLS.append(result);return result
def new_root(base,name):
    root=base/name;root.mkdir();(root/'.local-model-only').write_bytes(b'E4T2_OWNED_SYNTHETIC_ONLY');(root/'files/e4_fixtures').mkdir(parents=True);return root
def local_context(root):
    script='set -e; cd '+shlex.quote(root.as_posix())+'; /usr/bin/id -u; pwd'
    result=ep.collect([SH,'-c',script],ep.Limits(timeout=5));CALLS.append(result);lines=ep.stdout_bytes(result).decode().splitlines()
    return Context(uid=int(lines[0]),pwd=lines[1])
def main():
    if len(sys.argv)!=2:raise ValueError('NEW_OWNED_BATCH_ROOT_REQUIRED')
    base=Path(sys.argv[1]).resolve()
    if not base.is_relative_to(BASE/'evidence') or base.exists() or (BASE/'evidence/remote-freeze.json').exists():raise ValueError('OWNED_NEW_UNFROZEN_SCOPE')
    base.mkdir();inputs=[row(BASE/'tools'/n) for n in ['exact_process.py','remote_command.py','diagnose_once.py','fake_aosp_client.py','run_local_checks.py']]
    source=BASE/'payload256.bin';check(source.read_bytes()==bytes(range(256)),'fixed own all-byte payload')
    original=json.loads((BASE/'reference/02-basic.mp4-backend-logs.json').read_text('utf-8'));producer=next(r for r in original if r['argv'][3]=='exec-in');original_argv=producer['argv']
    root=new_root(base,'original-argv');transport=LocalTransport(root)
    result=transport.receive(original_argv,source);trace=json.loads((root/'trace-00.json').read_text('utf-8'))
    target=root/'files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part'
    check(result['originalExitCode']==0 and result['submittedBytes']==256,'original adapter model client returns0 after own256 submission')
    check(trace['remoteShellExit']==127 and not target.exists(),'real Git sh executes quoted command-name failure and target absent')
    check(result['stdout']['bytes']==0 and result['stderr']['bytes']==0,'legacy exec-in hides remote error/result')
    raw_script=shlex.split(original_argv[-1])[0];root=new_root(base,'fixed-legacy-argv');transport=LocalTransport(root)
    fixed=run_as_argv('MODEL_NOT_ADB','HA1Q6WXR','exec-in',raw_script);result=transport.receive(fixed,source);trace=json.loads((root/'trace-00.json').read_text('utf-8'))
    check(trace['remoteShellExit']==0 and (root/'files/e4_fixtures/.basic.E4AT1P_TABLET_20261017_once.part').read_bytes()==bytes(range(256)),'mode-specific raw argument actually runs exact receiver')
    check(result['stdout']['bytes']==0,'fixed legacy direction still has no remote execution marker')
    root=new_root(base,'exec-out-direction');transport=LocalTransport(root)
    args=run_as_argv('MODEL_NOT_ADB','HA1Q6WXR','exec-out','n=$(cat | wc -c); printf "COUNT=%s\\n" "$n"')
    result=transport.receive(args,source);trace=json.loads((root/'trace-00.json').read_text('utf-8'))
    check(trace['forwardedInputBytes']==0 and ep.stdout_bytes(result).strip()==b'COUNT=0','exec-out is not an upload direction despite host submitted bytes')
    diagnostics=[]
    for name,variant in [('success','normal'),('missing-end','drop-end'),('no-shell-v2','no-v2'),('prior-receiver','prior-cat'),('wrong-independent-sha','bad-proof')]:
        root=new_root(base,name);context=local_context(root);transport=LocalTransport(root,variant)
        old=root/'files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep';old.write_bytes(b'OWN_ONLY')
        before=old.read_bytes();result=run_diagnostic(transport,root/'receipts',context,authorized=True);diagnostics.append(dict(case=name,result=result))
        check(old.read_bytes()==before,'lstat-only history did not alter owned historical dummy')
        check(result['metadataCommands']<=20 and result['producerAttempts']<=1,'finite commands and one producer')
        check(result['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED','no snapshot is not complete resource return')
        if name=='success':
            check(result['status']=='SYNTHETIC_DIAGNOSTIC_VERIFIED_NOT_A_MEDIA_FIXTURE','production diagnostic passes actual local shell markers plus independent file proof')
            check(result['metadataCommands']==6 and result['producerAttempts']==1,'exact six metadata and one own256 producer')
            check(result['hostSubmittedBytesSnapshot']==256 and result['syntheticPayloadBudgetBytes']==256,'host submit snapshot separate from synthetic budget and remote count')
            check((root/context.target).read_bytes()==bytes(range(256)),'full all-byte data survives actual local cat')
            check(result['originalReceiver']['begin']['uid']==str(context.uid) and result['originalReceiver']['begin']['pwd']==context.pwd,'real local uid/pwd reported, not Android claim')
            check(result['independentFile']['sha']==PAYLOAD_SHA,'independent real local sha equals source')
            check(sum(p.stat().st_size for p in (root/'receipts').iterdir())<1048576,'actual diagnostic logs under1MiB')
            try:run_diagnostic(transport,root/'receipts',context,authorized=True)
            except FileExistsError:check(True,'same attempt evidence directory refuses second run')
            else:raise AssertionError('attempt reused')
        elif name=='no-shell-v2':check(result['producerAttempts']==0 and 'SHELL_V2_REQUIRED' in result['firstFailure'],'no protocol fallback')
        elif name=='prior-receiver':check(result['producerAttempts']==0 and 'POSSIBLE_PRIOR_RECEIVER' in result['firstFailure'],'available prior receiver evidence stops without kill')
        else:
            check(result['status']=='NOT_ADMITTED' and result['producerAttempts']==1,'missing marker/hash refuses after only one producer')
            check((root/context.target).exists(),'failed diagnostic artifact retained')
    context=Context();valid=(f'E4T2_BEGIN|{context.nonce}|uid=10221|pid=1|pwd={context.pwd}|path={context.target}\n'+f'E4T2_END|{context.nonce}|uid=10221|pid=1|pwd={context.pwd}|path={context.target}|bytes=256\n').encode()
    h=history_script(context)
    pre=preflight_script(context)
    check(pre.index('printf')<pre.index('test "$u"') and 'pwd -P' not in pre,'actual context printed before rejection and same pwd interface as original admitted evidence')
    check('test -e' not in h and '[ -e' not in h and 'sha256sum' not in h and 'cat ' not in h,'historical paths use exact no-follow lstat only, no content operation')
    check(h.count('/system/bin/toybox stat -c')==3 and 'stat -L' not in h,'exact three historical leaves, no recursive or following-stat scan')
    for bad in [valid.replace(b'uid=10221',b'uid=2000'),valid.replace(b'bytes=256',b'bytes=255'),valid.splitlines()[0]+b'\n']:
        try:parse_receiver(bad,context)
        except ValueError:check(True,'original uid/count/end marker strictly checked')
        else:raise AssertionError('bad remote proof admitted')
    check(ep.retained_owners()==0,'all targeted local process owners returned; T1 strong gate retained')
    result=dict(schema=1,scope='T2_SOURCE_BACKED_ARGV_AND_LOCAL_REAL_GIT_SH_ONLY',status='PASS',assertions=ASSERTIONS,inputs=inputs,callRecords=len(CALLS),records=CALLS,diagnostics=diagnostics,
                modelSourceVersion='AOSP pinned commandline source; installed37.0.1 mapping UNKNOWN',adbCalls=0,deviceRuns=0,realMediaBytesRead=0,gradleRuns=0,legacy72Repeated=False,legacy63Repeated=False,retainedLocalOwners=0)
    out=base/'local-results.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['scope','status','assertions','callRecords','adbCalls','realMediaBytesRead','retainedLocalOwners']},sort_keys=True))
if __name__=='__main__':main()
