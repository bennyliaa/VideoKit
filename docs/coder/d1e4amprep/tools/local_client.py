"""Own small-file backend model; real Base64 decode and rename, no ADB/device execution."""
from pathlib import Path
import base64
import hashlib
import json
import os
import shlex
import sys
import t6_protocol as p
from media_commands import *
BASE=Path(__file__).resolve().parents[1]
def main():
    root=Path(sys.argv[1]).resolve();variant=sys.argv[2];args=sys.argv[3:]
    if not root.is_relative_to(BASE/'evidence/local-main-001') or (root/'.owned').read_bytes()!=b'MPREP_OWN':raise ValueError('OWNED_SMALL_MODEL')
    specs=tuple(Spec(**s) for s in json.loads((root/'specs.json').read_text('utf-8')))
    def emit(kind,fields):print('T6_'+kind+'|'+p.NONCE+'|'+fields)
    def df():print('Filesystem 1K-blocks Used Available Use% Mounted on\nlocal-only 2000000000 100 1999999900 1% /data')
    def stat(path):
        s=path.stat();return f'{s.st_dev},{s.st_ino},{s.st_size},{p.UID},8180,{int(s.st_mtime)}'
    if args==['-s',p.SERIAL,'features']:
        if sys.stdin.buffer.read(1):raise ValueError('METADATA_STDIN')
        r=json.loads((BASE/'reference/features.json').read_text('utf-8'));sys.stdout.buffer.write(bytes.fromhex(r['stdout']['prefixHex']));return
    prefix=['-s',p.SERIAL,'shell'];rest=args[len(prefix):];stdin=rest[:1]!=['-n']
    if not stdin:rest=rest[1:]
    if args[:len(prefix)]!=prefix or rest[:7]!=['-T','-e','none','run-as',p.PACKAGE,'sh','-c'] or len(rest)!=8:raise ValueError('MODEL_FIXED_ROUTE')
    words=shlex.split(rest[-1]);script=words[0] if len(words)==1 else ''
    if stdin:
        s=next(s for s in specs if script==receiver_script(s));wire=sys.stdin.buffer.read(s.encodedBytes+1)
        if len(wire)!=s.encodedBytes:raise ValueError('ENCODED_COUNT')
        raw=base64.b64decode(wire,validate=True);out=root/s.temp
        if (root/s.final).exists():raise FileExistsError('FINAL_CONFLICT')
        emit('BEGIN',f'uid={p.UID}|pwd={p.PWD}|pid=123|path={s.temp}')
        if variant=='short' and s.alias=='basic.mp4':raw=raw[:26]
        if variant=='wrong-sha' and s.alias=='basic.mp4':raw=bytes([raw[0]^1])+raw[1:]
        with out.open('xb') as f:f.write(raw)
        emit('DECODE','rc=0');emit('END',f'uid={p.UID}|pwd={p.PWD}|pid=123|path={s.temp}|decoderRc=0|statRc=0|bytes={len(raw)}');return
    if sys.stdin.buffer.read(1):raise ValueError('METADATA_STDIN')
    if script==admission_script(specs):
        if (root/TEMP_DIR).exists() or any((root/s.final).exists() for s in specs):raise FileExistsError('ORIGINAL_CONFLICT')
        emit('ADMISSION',f'uid={p.UID}|pwd={p.PWD}|parent={FIXTURES}');df();return
    if script==p.processes_script():emit('PS','self=123');print(f' PID PPID UID ARGS\n 123 1 {p.UID} sh -c synthetic\n 124 123 {p.UID} toybox ps');return
    if script==p.mkdir_script():(root/TEMP_DIR).mkdir();emit('DIRECTORY',f'path={TEMP_DIR}');return
    if script==p.decoder_probe_script():
        (root/p.PROBE_ASCII).write_bytes(b'AA==');(root/p.PROBE_RAW).write_bytes(b'\0')
        for stage in ['printf','decoder','od']:emit('PROBE_RC',f'stage={stage}|rc=0')
        emit('PROBE',f'uid={p.UID}|pwd={p.PWD}|parentPid=123|mode=SEQUENTIAL_FILES|asciiStatRc=0|rawStatRc=0|asciiBytes=4|rawBytes=1|hex= 00');return
    for s in specs:
        if script==file_guard_script(s):
            if (root/s.temp).exists() or (root/s.final).exists():raise FileExistsError('FILE_CONFLICT')
            emit('FILE_GUARD',f'uid={p.UID}|pwd={p.PWD}|alias={s.alias}|temp={s.temp}|final={s.final}');df();return
        for final in [False,True]:
            if script==proof_script(s,final):
                path=root/(s.final if final else s.temp)
                if final and (root/s.temp).exists():raise FileExistsError('TEMP_NOT_GONE')
                a=stat(path)
                with path.open('rb') as f:raw=f.read(s.bytes)
                emit('PROOF',f'uid={p.UID}|pwd={p.PWD}|path={s.final if final else s.temp}|bytes={path.stat().st_size}|sha={hashlib.sha256(raw).hexdigest()}|before={a}|after={stat(path)}');return
        path=root/s.temp
        if path.exists() and script==publish_script(s,stat(path)):
            if (root/s.final).exists():raise FileExistsError('NO_OVERWRITE')
            a=stat(path);os.rename(path,root/s.final)
            emit('PUBLISH_ATTEMPT',f'alias={s.alias}|mvRc=0');emit('PUBLISHED',f'uid={p.UID}|pwd={p.PWD}|alias={s.alias}|temp={s.temp}|final={s.final}|tempAbsent=1|stamp={stat(root/s.final)}');return
    raise ValueError('UNRECOGNIZED_FIXED_SCRIPT')
if __name__=='__main__':
    try:main()
    except Exception as error:print(str(error),file=sys.stderr);raise SystemExit(1)
