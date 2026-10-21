"""Local fixed-response model with real Base64 decode/file writes, never an ADB implementation."""
from pathlib import Path
import base64
import hashlib
import json
import shlex
import sys
from private_commands import *
BASE=Path(__file__).resolve().parents[1]
def main():
    root=Path(sys.argv[1]).resolve();variant=sys.argv[2];args=sys.argv[3:]
    if not root.is_relative_to(BASE/'evidence/local-main-001') or (root/'.owned').read_bytes()!=b'T6_LOCAL_ONLY':raise ValueError('OWNED_LOCAL_ROOT')
    if args==['decode-only']:
        raw=sys.stdin.buffer.read(100000)
        data=base64.b64decode(raw,validate=True);print(json.dumps(dict(encodedBytes=len(raw),encodedSha256=hashlib.sha256(raw).hexdigest(),rawBytes=len(data),rawSha256=hashlib.sha256(data).hexdigest())));return
    def emit(kind,fields):print('T6_'+kind+'|'+NONCE+'|'+fields)
    if args==['-s',SERIAL,'features']:
        if sys.stdin.buffer.read(1):raise ValueError('METADATA_STDIN')
        r=json.loads((BASE/'reference/features.json').read_text('utf-8'));sys.stdout.buffer.write(bytes.fromhex(r['stdout']['prefixHex']));return
    prefix=['-s',SERIAL,'shell'];rest=args[len(prefix):];stdin=not rest[:1]==['-n']
    if not stdin:rest=rest[1:]
    if args[:len(prefix)]!=prefix or rest[:7]!=['-T','-e','none','run-as',PACKAGE,'sh','-c'] or len(rest)!=8:raise ValueError('FIXED_ROUTE')
    words=shlex.split(rest[-1]);script=words[0] if len(words)==1 else ''
    directory=root/'private';target=directory/'payload256.bin'
    if stdin:
        if script!=receiver_script():raise ValueError('FIXED_RECEIVER')
        wire=sys.stdin.buffer.read(345)
        if len(wire)!=344 or b'\x1a' in wire or b'\0' in wire:raise ValueError('ASCII_WIRE_LENGTH')
        data=base64.b64decode(wire,validate=True)
        emit('BEGIN',f'uid={UID}|pwd={PWD}|pid=123|path={TARGET}')
        with target.open('xb') as f:f.write(b'' if variant=='decoder-nonzero' else data[:26] if variant=='short-exit0' else bytes([data[0]^1])+data[1:] if variant=='wrong-sha' else data)
        d=7 if variant=='decoder-nonzero' else 0;emit('DECODE',f'rc={d}')
        if d:raise SystemExit(d)
        emit('END',f'uid={UID}|pwd={PWD}|pid=123|path={TARGET}|decoderRc=0|statRc=0|bytes={target.stat().st_size}');return
    if sys.stdin.buffer.read(1):raise ValueError('METADATA_STDIN')
    if script==context_script():
        if directory.exists():raise FileExistsError('CONFLICT')
        emit('CONTEXT',f'uid={UID}|pwd={PWD}');return
    if script==decoder_probe_script():
        (directory/'probe.ascii').write_bytes(b'AA==');(directory/'probe.raw').write_bytes(b'\0')
        for stage in ['printf','decoder','od']:emit('PROBE_RC',f'stage={stage}|rc=0')
        emit('PROBE',f'uid={UID}|pwd={PWD}|parentPid=123|mode=SEQUENTIAL_FILES|asciiStatRc=0|rawStatRc=0|asciiBytes=4|rawBytes=1|hex= 00');return
    if script==processes_script():emit('PS','self=123');print(f' PID PPID UID ARGS\n 123 1 {UID} sh -c synthetic\n 124 123 {UID} toybox ps');return
    if script==mkdir_script():directory.mkdir();emit('DIRECTORY',f'path={DIRECTORY}');return
    if script==proof_script():
        s=target.stat();stamp=f'{s.st_dev},{s.st_ino},{s.st_size},{UID},8180,{int(s.st_mtime)}'
        with target.open('rb') as f:data=f.read(256)
        emit('PROOF',f'uid={UID}|pwd={PWD}|path={TARGET}|bytes={s.st_size}|sha={hashlib.sha256(data).hexdigest()}|before={stamp}|after={stamp}');return
    raise ValueError('UNKNOWN_FIXED_SCRIPT')
if __name__=='__main__':
    try:main()
    except Exception as error:print(str(error),file=sys.stderr);raise SystemExit(1)
