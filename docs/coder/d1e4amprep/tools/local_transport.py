"""Local test adapter; production transport never permits synthetic spec overrides."""
from pathlib import Path
import sys
import exact_process as ep
from stream_base64 import transfer_base64
from preload_once import BASE,limits
class LocalTransport:
    adb='LOCAL_MODEL_NO_ADB';local_only=True
    def __init__(self,root,variant='normal'):self.root=Path(root);self.variant=variant;self.records=[]
    def record_argv(self,args):return [sys.executable,'-X','utf8','-B',str(BASE/'tools/local_client.py'),str(self.root),self.variant,*args[1:]]
    def command(self,args,seconds):
        r=ep.collect(self.record_argv(args),limits(5));self.records.append(r);return r
    def transfer(self,args,s):
        r=transfer_base64(self.record_argv(args),s.source,s.bytes,s.sha256,limits(5));self.records.append(r);return r
