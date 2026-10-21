"""Fixed finite offline child; no SDK, network, arbitrary commands or unknown media."""
from pathlib import Path
import sys,time,hashlib,json
mode=sys.argv[1];gate=Path(sys.argv[2])
if mode=='success':sys.stdout.buffer.write(b'LOCAL_CAPTURE_OK\n')
elif mode in ['binary','binary_stderr']:
 sys.stdout.buffer.write(b'\x89PNG\r\n\x1a\n'+bytes(range(256))*32+b'\xff')
 if mode=='binary_stderr':sys.stderr.buffer.write(b'CONTROLLED_BINARY_DIAGNOSTIC\n')
elif mode=='stdin':
 data=sys.stdin.buffer.read(349103);sys.stdout.buffer.write((json.dumps({'stdinBytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})+'\n').encode())
 if len(data)!=349102:raise SystemExit(7)
elif mode=='stderr':sys.stdout.buffer.write(b'OUT\n');sys.stderr.buffer.write(b'CONTROLLED_STDERR\n')
elif mode=='overrun':
 for b in [b'A'*64,b'B'*64,b'C'*64]:sys.stdout.buffer.write(b);sys.stdout.buffer.flush();time.sleep(.03)
elif mode=='late':
 end=time.monotonic()+5
 while not gate.exists() and time.monotonic()<end:time.sleep(.01)
 sys.stdout.buffer.write(b'ORIGINAL_LATE_RETURN\n')
elif mode=='nonzero':sys.stderr.buffer.write(b'CONTROLLED_FAILURE\n');raise SystemExit(7)
else:raise ValueError('fixed offline fixture mode required')
