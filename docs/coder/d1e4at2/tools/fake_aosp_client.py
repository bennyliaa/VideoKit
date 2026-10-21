"""Bounded LOCAL model of documented AOSP argv construction, with real existing Git sh parsing."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
from remote_command import model_service

BASE=Path(__file__).resolve().parents[1]
SH='C:/Program Files/Git/usr/bin/sh.exe'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--trace',type=Path,required=True);parser.add_argument('--variant',default='normal');parser.add_argument('args',nargs=argparse.REMAINDER);a=parser.parse_args()
    root=a.root.resolve()
    if not root.is_relative_to(BASE/'evidence') or (root/'.local-model-only').read_bytes()!=b'E4T2_OWNED_SYNTHETIC_ONLY':raise ValueError('LOCAL_MODEL_ROOT_REQUIRED')
    args=a.args[1:] if a.args[:1]==['--'] else a.args;argv=['MODEL_NOT_ADB',*args]
    if argv[1:3]!=['-s','HA1Q6WXR']:raise ValueError('ONE_MODEL_TARGET')
    if argv[3]=='features':
        print('cmd,shell_v2' if a.variant!='no-v2' else 'cmd');a.trace.write_text(json.dumps(dict(localModel=True,featuresOnly=True)),encoding='utf-8');return 0
    service=model_service(argv);actual=service
    if not service.startswith('run-as '):raise ValueError('MODEL_RUN_AS_EXPECTED')
    actual='e4_run_as'+actual[len('run-as'):]
    snapshot='E4T2_PS|' in actual
    if snapshot:
        cut=actual.index('/system/bin/toybox ps ');tail=actual[cut:]
        # Everything after this command is the final outer-quoted argument. Preserve its closing quote.
        import shlex
        inner=shlex.split(service)[-1];uid=inner.split('ps -u ',1)[1].split()[0]
        substitute="printf 'PID PPID UID ARGS\\n'"
        if a.variant=='prior-cat':substitute+=f"; printf '999999 1 {uid} cat\\n'"
        inner=inner[:inner.index('/system/bin/toybox ps ')]+substitute
        rebuilt=['MODEL_NOT_ADB','-s','HA1Q6WXR','shell','-T','-e','none','run-as','com.videokit.app','sh','-c',shlex.quote(inner)]
        actual='e4_run_as'+model_service(rebuilt)[len('run-as'):]
    actual=actual.replace('/system/bin/toybox ','')
    if a.variant=='bad-proof' and 'E4T2_PROOF|' in actual:
        targets=list((root/'files').glob('e4_diag_*/payload256.bin'))
        if len(targets)!=1:raise ValueError('OWNED_DIAGNOSTIC_TARGET')
        data=targets[0].read_bytes();targets[0].write_bytes(bytes([data[0]^1])+data[1:])
    if os.name=='nt':
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(),os.O_BINARY)
    data=sys.stdin.buffer.read(257)
    if len(data)>256:raise ValueError('MODEL_PAYLOAD_BOUND')
    mode=argv[3];forwarded=data if mode in {'shell','exec-in'} else b''
    env=os.environ.copy();env['PATH']='C:/Program Files/Git/usr/bin;'+env.get('PATH','')
    prefix='e4_run_as() { test "$1" = com.videokit.app || return 41; shift; "$@"; }; '
    child=subprocess.run([SH,'-c',prefix+actual],input=forwarded,capture_output=True,cwd=root,env=env,timeout=5,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    out=child.stdout;err=child.stderr
    if a.variant=='drop-end' and 'E4T2_BEGIN|' in actual:out=b'\n'.join(line for line in out.splitlines() if not line.startswith(b'E4T2_END|'))+b'\n'
    a.trace.write_text(json.dumps(dict(localModel=True,installedAdbExecuted=False,serviceCommand=service,executedCommand=actual,
        shims=['run-as command name only; no UID switch','Android toybox prefix uses existing local test binaries','UID snapshot is synthetic header/fixture' if snapshot else 'no snapshot shim'],
        forwardedInputBytes=len(forwarded),remoteShellExit=child.returncode,remoteStdoutHex=out[:8192].hex(),remoteStderrHex=err[:8192].hex(),legacyClientExitIsNotRemoteExit=mode!='shell'),indent=2)+'\n',encoding='utf-8')
    if mode=='shell':sys.stdout.buffer.write(out);sys.stderr.buffer.write(err);return child.returncode
    if mode=='exec-out':sys.stdout.buffer.write(out+err)
    # Legacy exec-in does not return remote stdout/stderr; both legacy branches return0 here.
    return 0
if __name__=='__main__':sys.exit(main())
