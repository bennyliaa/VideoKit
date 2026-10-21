"""Owned-fixture-only child for the production transfer selfcheck. Never accesses ADB/media."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['receive','probe','rename','argv']);p.add_argument('--root',type=Path,required=True);p.add_argument('--target');p.add_argument('--destination');p.add_argument('--behavior',default='exact');p.add_argument('--cap',type=int,default=1048576);p.add_argument('extra',nargs='*');a=p.parse_args()
    root=a.root.resolve();allowed=Path(__file__).resolve().parents[1]/'evidence'
    if not root.is_relative_to(allowed) or (root/'.owned-fixture-root').read_text()!='E4AT_OWNED_FAKE_FILES_ONLY':raise ValueError('NOT_OWNED_FIXTURE_ROOT')
    def owned(name):
        path=root/name
        if not path.resolve().is_relative_to(root) or path.is_symlink():raise ValueError('OWNED_PATH_ESCAPE')
        return path
    if a.mode=='argv':print(json.dumps(a.extra,ensure_ascii=False));return 0
    target=owned(a.target)
    if a.mode=='probe':
        if not target.exists():print(json.dumps(dict(absent=True)));return 0
        if not target.is_file():raise ValueError('OWNED_PROBE_BOUND')
        if a.behavior=='metadata':print(json.dumps(dict(exists=True,length=target.stat().st_size,readBytes=0)));return 0
        if target.stat().st_size>a.cap:print(json.dumps(dict(length=target.stat().st_size,readBytes=0)));return 43
        if target.stat().st_size>1048576:raise ValueError('OWNED_PROBE_BOUND')
        data=target.read_bytes();print(json.dumps(dict(length=len(data),sha256=hashlib.sha256(data).hexdigest(),readBytes=len(data))));return 0
    if a.mode=='rename':
        dest=owned(a.destination)
        if dest.exists() or target.parent!=dest.parent:raise ValueError('OWNED_NO_CLOBBER')
        os.rename(target,dest);return 0
    if os.name=='nt':
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(),os.O_BINARY)
    with target.open('xb') as out:
        if a.behavior in {'pressure','overcap'}:
            count=262144 if a.behavior=='pressure' else 2097152
            sys.stdout.buffer.write(b'o'*count);sys.stdout.buffer.flush()
            sys.stderr.buffer.write(b'e'*131072);sys.stderr.buffer.flush()
        if a.behavior in {'early','hang'}:
            out.write(sys.stdin.buffer.read(1024));out.flush();os.fsync(out.fileno())
            if a.behavior=='hang':time.sleep(30)
            return 0
        data=sys.stdin.buffer.read(1048577)
        if len(data)>1048576:raise ValueError('OWNED_INPUT_BOUND')
        if a.behavior=='exit0-truncate':data=data[:81407]
        elif a.behavior=='exit0-grow':data+=b'x'
        elif a.behavior=='exit0-corrupt':data=bytes([data[0]^1])+data[1:]
        elif a.behavior=='text-eof-example':data=data.split(b'\x1a',1)[0]
        elif a.behavior=='nonzero':out.write(data[:37]);return 19
        out.write(data);out.flush();os.fsync(out.fileno())
    return 0

if __name__=='__main__':sys.exit(main())
