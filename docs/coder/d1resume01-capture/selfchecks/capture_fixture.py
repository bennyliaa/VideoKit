"""Controlled local child. Never imports an SDK/client/network library."""
from pathlib import Path
import sys,time
mode=sys.argv[1]
if mode=='success':sys.stdout.buffer.write(b'CAPTURE_LOCAL_OK\n');sys.stdout.buffer.flush()
elif mode=='stderr':sys.stdout.buffer.write(b'OUT\n');sys.stdout.buffer.flush();sys.stderr.buffer.write(b'LOCAL_STDERR\n');sys.stderr.buffer.flush()
elif mode=='chunks':
 for raw in [b'A'*64,b'B'*64,b'C'*64]:sys.stdout.buffer.write(raw);sys.stdout.buffer.flush();time.sleep(.08)
elif mode=='timeout':time.sleep(1.2);sys.stdout.buffer.write(b'LATE_AFTER_TIMEOUT\n');sys.stdout.buffer.flush()
elif mode=='late':
 gate=Path(sys.argv[2]);end=time.monotonic()+8
 while not gate.exists() and time.monotonic()<end:time.sleep(.01)
 sys.stdout.buffer.write(b'ORIGINAL_LATE_RETURN\n');sys.stdout.buffer.flush()
elif mode=='exit':sys.stderr.buffer.write(b'CONTROLLED_CHILD_FAILURE\n');sys.stderr.buffer.flush();raise SystemExit(7)
else:raise ValueError('exact local fixture mode required')
