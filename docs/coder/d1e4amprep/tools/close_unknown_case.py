"""Isolated original sourceclose-return fault blocks all AVI work, never cleared or refunded."""
from pathlib import Path
import json
import sys
import exact_process as ep
import stream_base64 as sb
from media_commands import Spec
from preload_once import BASE,run_preload,retained
from local_transport import LocalTransport
def main():
    root=Path(sys.argv[1]).resolve()
    if not root.is_relative_to(BASE/'evidence/local-main-001'):raise ValueError('OWNED_CASE')
    specs=tuple(Spec(**x) for x in json.loads((root/'specs.json').read_text('utf-8')))
    original=sb.EncodedSource.close
    def fail(self):original(self);raise OSError('CONTROLLED_CLOSE_RETURN_UNKNOWN')
    sb.EncodedSource.close=fail;t=LocalTransport(root);r=run_preload(t,root/'receipts',authorized=True,specs=specs);refused=False
    try:ep.collect(['NO_NEXT_IO_ALLOWED'])
    except RuntimeError:refused=True
    assert r['status']=='NOT_ADMITTED' and r['producerAttempts']=={'basic.mp4':1,'subtitle.avi':0} and retained()==1 and refused
    print(json.dumps(dict(status='EXPECTED_UNKNOWN_RETAINED',result=r,originals=t.records,retainedUntilInterpreterEnd=1,nextIoRefused=refused,osExitNotCredited=True)))
if __name__=='__main__':main()
