"""One-attempt provisioning library. Importing or --plan never invokes ADB or opens a source."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import os
from exact_process import Limits, collect, stdout_bytes, transfer_file

PACKAGE='com.videokit.app'

@dataclass(frozen=True)
class FileProof:
    length:int
    sha256:str
    def __post_init__(self):
        if type(self.length) is not int or not 0<=self.length<=1073741824 or not re.fullmatch('[0-9a-f]{64}',self.sha256):raise ValueError('EXACT_FILE_PROOF_REQUIRED')

def fixture_path(value):
    if not isinstance(value,str) or not re.fullmatch(r'files/e4_fixtures/[A-Za-z0-9._-]{1,120}',value):raise ValueError('FIXED_FIXTURE_DIRECTORY_AND_BASENAME_REQUIRED')
    if PurePosixPath(value).name in {'.','..'}:raise ValueError('DOT_ROLE_REJECTED')
    return value

def run_as_argv(adb,serial,mode,script):
    if not re.fullmatch('[A-Za-z0-9._:-]{1,80}',serial) or mode not in {'shell','exec-in'}:raise ValueError('FIXED_TARGET_REQUIRED')
    # ADB joins remote arguments. Literal POSIX quoting keeps the ENTIRE script inside run-as sh -c.
    return [str(adb),'-s',serial,mode,'run-as',PACKAGE,'sh','-c',shlex.quote(script)]

def probe_script(path,cap=1048576,metadata_only=False):
    if type(cap) is not int or not 0<=cap<=1073741824:raise ValueError('FINITE_REMOTE_HASH_CAP_REQUIRED')
    p=shlex.quote(fixture_path(path))
    tail="printf 'E4AT_META\\n%s\\n' \"$n\"" if metadata_only else f"test \"$n\" -le {cap} || exit 43; printf 'E4AT_FILE\\n%s\\n' \"$n\"; /system/bin/toybox sha256sum -- {p}"
    return f"if [ ! -e {p} ] && [ ! -L {p} ]; then printf 'E4AT_ABSENT\\n'; elif [ -f {p} ] && [ ! -L {p} ]; then n=$(/system/bin/toybox stat -c %s -- {p}) || exit 44; {tail}; else exit 42; fi"

def rename_script(source,target):
    s=shlex.quote(fixture_path(source));t=shlex.quote(fixture_path(target))
    if source==target or PurePosixPath(source).parent!=PurePosixPath(target).parent:raise ValueError('SAME_DIRECTORY_DISTINCT_NAMES_REQUIRED')
    return f'set -e; test -f {s}; test ! -L {s}; test ! -e {t}; test ! -L {t}; /system/bin/toybox mv -n -- {s} {t}; test ! -e {s}; test -f {t}; test ! -L {t}'

def receive_script(path):
    p=shlex.quote(fixture_path(path))
    return f'umask 077; set -e; set -C; test ! -e {p}; test ! -L {p}; exec cat > {p}'

class AdbBackend:
    """Only a separately dispatched tester may construct with execution_authorized=True."""
    def __init__(self,adb,serial,*,execution_authorized=False,timeout=120):
        self.adb=str(adb);self.serial=serial;self.execution_authorized=execution_authorized;self.timeout=timeout;self.logs=[]
    def _allowed(self):
        if not self.execution_authorized:raise PermissionError('PLAN_ONLY_NO_DEVICE_EXECUTION')
    def _command(self,script):
        self._allowed();result=collect(run_as_argv(self.adb,self.serial,'shell',script),Limits(timeout=min(self.timeout,120),stdout_cap=65536,stderr_cap=65536));self.logs.append(result)
        raw=stdout_bytes(result)
        if result['stderr']['bytes']:raise IOError('REMOTE_STDERR_NOT_CLEAN')
        return raw
    def exists(self,path):
        raw=self._command(probe_script(path,0,True)).decode("ascii","strict").splitlines()
        if raw==["E4AT_ABSENT"]:return False
        if len(raw)==2 and raw[0]=="E4AT_META" and raw[1].isdigit():return True
        raise IOError("REMOTE_METADATA_FORMAT")
    def probe(self,path,cap=1048576):
        raw=self._command(probe_script(path,cap)).decode('ascii','strict').splitlines()
        if raw==['E4AT_ABSENT']:return None
        if len(raw)!=3 or raw[0]!='E4AT_FILE' or not raw[1].isdigit():raise IOError('REMOTE_PROBE_FORMAT')
        fields=raw[2].split(maxsplit=1)
        if len(fields)!=2 or fields[1].strip()!=path:raise IOError('REMOTE_PROBE_PATH_MISMATCH')
        return FileProof(int(raw[1]),fields[0])
    def rename(self,source,target):self._command(rename_script(source,target))
    def receive(self,path,source,expected):
        self._allowed();result=transfer_file(run_as_argv(self.adb,self.serial,'exec-in',receive_script(path)),source,expected.length,expected.sha256,Limits(timeout=self.timeout));self.logs.append(result);return result

def _new(path,value):
    data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(data)>1048576:raise ValueError('RECEIPT_BUDGET')
    with Path(path).open('xb') as file:file.write(data);file.flush();os.fsync(file.fileno())

def provision_once(backend,source,expected,final_path,temp_path,receipt_dir,*,attempt_id,residual=None,archive_path=None):
    """All target proofs are separate actual file probes. No retries, cleanup, resume or overwrite."""
    final_path=fixture_path(final_path);temp_path=fixture_path(temp_path)
    if final_path==temp_path or PurePosixPath(final_path).parent!=PurePosixPath(temp_path).parent:raise ValueError('NEW_SAME_DIRECTORY_TEMP_REQUIRED')
    if not re.fullmatch('[A-Za-z0-9_-]{8,80}',attempt_id):raise ValueError('ONE_REVIEWED_ATTEMPT_ID_REQUIRED')
    if not backend.execution_authorized:raise PermissionError('PLAN_ONLY_NO_DEVICE_EXECUTION')
    if residual is not None:
        archive_path=fixture_path(archive_path)
        if archive_path in {final_path,temp_path}:raise ValueError('DISTINCT_RESIDUAL_ARCHIVE_REQUIRED')
    receipt_dir=Path(receipt_dir);receipt_dir.mkdir(parents=True,exist_ok=True)
    marker=receipt_dir/(attempt_id+'.attempt.json');result_path=receipt_dir/(attempt_id+'.result.json')
    _new(marker,dict(attempt=attempt_id,source=str(source),expected=asdict(expected),final=final_path,temp=temp_path,residual=asdict(residual) if residual else None,archive=archive_path,state='CONSUMED_BEFORE_ANY_MUTATION'))
    events=[];result=dict(attempt=attempt_id,status='NOT_ADMITTED',temp=temp_path,final=final_path,archive=archive_path,expected=asdict(expected),events=events,automaticRetry=False,automaticCleanup=False)
    def event(name,proof=None):
        if len(events)>=24:raise IOError('EVENT_BUDGET')
        item=dict(stage=name,proof=asdict(proof) if proof else None);events.append(item)
        # Finite durable stage history. Failure never erases an earlier event or the attempt marker.
        with (receipt_dir/(attempt_id+'.events.jsonl')).open('ab') as file:
            file.write((json.dumps(item,sort_keys=True)+'\n').encode());file.flush();os.fsync(file.fileno())
    def probe(path,cap):return backend.probe(path,cap)
    try:
        if residual is not None:
            before=probe(final_path,residual.length)
            if before!=residual:raise IOError('ORIGINAL_RESIDUAL_IDENTITY_MISMATCH')
            event('ORIGINAL_RESIDUAL_VERIFIED',before)
            if backend.exists(archive_path):raise IOError('RESIDUAL_ARCHIVE_ALREADY_EXISTS')
            backend.rename(final_path,archive_path)
            after=probe(archive_path,residual.length)
            if after!=residual or backend.exists(final_path):raise IOError('RESIDUAL_RENAME_NOT_PROVEN')
            event('RESIDUAL_ARCHIVED_SAME_BYTES',after)
        elif backend.exists(final_path):raise IOError('FIXTURE_ALREADY_EXISTS_NO_OVERWRITE')
        if backend.exists(temp_path):raise IOError('TEMP_ALREADY_EXISTS_NO_OVERWRITE')
        event('NEW_TEMP_ABSENCE_VERIFIED')
        transfer=backend.receive(temp_path,source,expected);result['transfer']=transfer
        if transfer['status']!='PROCESS_IO_COMPLETE_ONLY':raise IOError('TRANSFER_PROCESS_NOT_COMPLETE')
        event('HOST_BINARY_SUBMISSION_COMPLETE_ONLY')
        landed=probe(temp_path,expected.length)
        if landed!=expected:raise IOError('INDEPENDENT_LANDED_LENGTH_OR_SHA_MISMATCH')
        event('INDEPENDENT_TEMP_BYTES_VERIFIED',landed)
        if backend.exists(final_path):raise IOError('PUBLISH_TARGET_NOT_ABSENT')
        backend.rename(temp_path,final_path)
        published=probe(final_path,expected.length)
        if published!=expected or backend.exists(temp_path):raise IOError('PUBLISH_NOT_PROVEN')
        event('SAME_DIRECTORY_PUBLISH_VERIFIED',published);result['status']='FIXTURE_ADMITTED';result['independentFinal']=asdict(published)
    except Exception as failure:result['firstFailure']=str(failure)[:300]
    result['backendCommands']=len(backend.logs);_new(result_path,result);return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan',type=Path,required=True);args=parser.parse_args();spec=json.loads(args.plan.read_text(encoding='utf-8'))
    commands=[]
    for item in spec['files']:
        commands.append(dict(alias=item['alias'],receive=run_as_argv(spec['adb'],spec['serial'],'exec-in',receive_script(item['temp'])),verify=run_as_argv(spec['adb'],spec['serial'],'shell',probe_script(item['temp'],item['bytes'])),publish=run_as_argv(spec['adb'],spec['serial'],'shell',rename_script(item['temp'],item['final']))))
    print(json.dumps(dict(mode='PLAN_ONLY',sourceOpened=False,adbCalls=0,executionAuthorized=False,commands=commands),ensure_ascii=False,indent=2))
