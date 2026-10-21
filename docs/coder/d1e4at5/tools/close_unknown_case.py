"""Isolated source-close-return fault; retained original Job is never cleared or retried."""
from pathlib import Path
import json
import sys
import exact_process as ep
import stream_base64 as sb
from private_commands import SHA
BASE=Path(__file__).resolve().parents[1]
def main():
    root=Path(sys.argv[1]).resolve()
    if not root.is_relative_to(BASE/'evidence/local-main-001'):raise ValueError('OWNED_CASE')
    original=sb.EncodedSource.close
    def throws(self):original(self);raise OSError('CONTROLLED_CLOSE_DID_NOT_RETURN')
    sb.EncodedSource.close=throws
    r=sb.transfer_base64([sys.executable,'-X','utf8','-B',str(BASE/'tools/local_client.py'),str(root),'normal','decode-only'],BASE/'payload256.bin',256,SHA,ep.Limits(timeout=5,cleanup=2))
    retained=ep.retained_owners();refused=False
    try:ep.collect(['NO_NEW_PROCESS_ALLOWED'])
    except RuntimeError:refused=True
    assert r['ownership']=='UNKNOWN_RETAINED' and not r['sourceCloseReturned'] and r['rawSource']['actualRawCloseReturned'] and retained==1 and refused
    print(json.dumps(dict(status='EXPECTED_UNKNOWN_RETAINED',originalRecord=r,retainedUntilInterpreterEnd=retained,nextIoRefused=refused,unknownNotClearedByOsExit=True)))
if __name__=='__main__':main()
