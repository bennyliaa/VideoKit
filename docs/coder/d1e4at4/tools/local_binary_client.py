"""LOCAL ONLY: fixed-script response model plus real Python binary file copies; never ADB."""
from pathlib import Path
import hashlib
import json
import os
import shlex
import sys
from binary_commands import *

BASE=Path(__file__).resolve().parents[1]

def main():
    root=Path(sys.argv[1]).resolve();variant=sys.argv[2];args=sys.argv[3:]
    if not root.is_relative_to(BASE/'evidence/local-main-001') or (root/'.owned').read_bytes()!=b'T4_LOCAL_ONLY':raise ValueError('LOCAL_ROOT_REQUIRED')
    if sys.stdin.buffer.read(1):raise ValueError('PAYLOAD_ON_STDIN_FORBIDDEN')
    stage=root/'stage';internal=root/'internal';leaf=stage/'payload256.bin';target=internal/'payload256.bin'
    def emit(kind,fields):print('T4_'+kind+'|'+NONCE+'|'+fields)
    def file_stamp(p,uid):
        s=p.stat();return f'{s.st_dev},{s.st_ino},{s.st_size},{uid},8180,{int(s.st_mtime)}'
    directory_stamp='1,1,0,2000,41c0,0' # Synthetic Android mode/UID, not Windows or device permission proof.
    if args==['-s',SERIAL,'features']:
        r=json.loads((BASE/'reference/features-record.json').read_text('utf-8'));sys.stdout.buffer.write(bytes.fromhex(r['stdout']['prefixHex']));return
    if args[:5]==['-s',SERIAL,'push','-q','-Z']:
        if len(args)!=7 or Path(args[5]).resolve()!=BASE/'payload256.bin' or args[6]!=SOURCE:raise ValueError('ONLY_FIXED_PUSH_SOURCE_AND_DESTINATION')
        with Path(args[5]).open('rb') as src:raw=src.read(257)
        if len(raw)!=256 or hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('LOCAL_SOURCE_IDENTITY')
        with leaf.open('xb') as dst:dst.write(raw[:26] if variant=='short-stage' else raw)
        print('LOCAL_MODEL_PUSH_EXIT0_NOT_DEVICE_PROOF');return
    prefix=['-s',SERIAL,'shell','-n','-T','-e','none'];rest=args[len(prefix):]
    if args[:len(prefix)]!=prefix:raise ValueError('ONLY_EMPTY_STDIN_METADATA_ROUTE')
    app=rest[:2]==['run-as',PACKAGE]
    if app:rest=rest[2:]
    if len(rest)!=3 or rest[:2]!=['sh','-c']:raise ValueError('FIXED_SH_ARGV')
    words=shlex.split(rest[2]);script=words[0] if len(words)==1 else ''
    if script==base_script(app):
        if variant=='denied' and not app:raise PermissionError('SYNTHETIC_EXTERNAL_BASE_DENIED')
        if stage.exists():raise FileExistsError('SYNTHETIC_STAGE_CONFLICT')
        emit('APP_BASE' if app else 'SHELL_BASE',f'uid={UID if app else 2000}|base={EXT}|stamp={directory_stamp}'+(f'|pwd={PWD}' if app else ''));return
    if app and script==processes_script():
        emit('PS','self=123');print(f' PID PPID UID ARGS\n 123 1 {UID} sh -c synthetic\n 124 123 {UID} toybox ps');return
    if not app and script==create_stage_script():
        stage.mkdir();emit('STAGE_CREATED',f'uid=2000|path={STAGE}|stamp={directory_stamp}');return
    if script==stage_access_script(app):
        if not stage.is_dir() or leaf.exists():raise FileExistsError('SYNTHETIC_STAGE_LEAF_CONFLICT')
        emit('APP_STAGE' if app else 'SHELL_STAGE',f'uid={UID if app else 2000}|path={STAGE}');return
    if app and script in [proof_script(True),proof_script(False)]:
        is_stage=script==proof_script(True);path=leaf if is_stage else target;st=file_stamp(path,2000 if is_stage else UID)
        with path.open('rb') as f:data=f.read(256)
        emit('STAGE_PROOF' if is_stage else 'INTERNAL_PROOF',f'uid={UID}|pwd={PWD}|path={SOURCE if is_stage else TARGET}|before={st}|after={file_stamp(path,2000 if is_stage else UID)}|sha={hashlib.sha256(data).hexdigest()}');return
    if app and leaf.exists() and script==copy_script(file_stamp(leaf,2000)):
        internal.mkdir();emit('COPY_BEGIN',f'uid={UID}|pwd={PWD}|pid=123|source={SOURCE}|target={TARGET}')
        with leaf.open('rb') as src,target.open('xb') as dst:dst.write(src.read(256))
        emit('COPY_END',f'uid={UID}|pwd={PWD}|pid=123|source={SOURCE}|target={TARGET}|bytes={target.stat().st_size}');return
    raise ValueError('UNRECOGNIZED_FIXED_SCRIPT')
if __name__=='__main__':
    try:main()
    except Exception as error:print(str(error),file=sys.stderr);raise SystemExit(1)
