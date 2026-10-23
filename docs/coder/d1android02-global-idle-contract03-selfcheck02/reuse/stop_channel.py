"""Bounded STOP_NEW_ADMISSION only; adapted from approved StopControl design."""
from pathlib import Path
import time
from capture_policy import stop_body,parse_stop,encoded
class Stop:
    def __init__(self,root,batch,nonce):
        self.path=Path(root)/'stop-request.json';self.body=stop_body(batch,nonce);self.stopped=False;self.polls=0;self.next=0.;self.files=[];self.unknown=False;self.write_entered=False;self.close_records=[]
    def poll(self):
        if self.stopped:return True
        if time.monotonic()<self.next:return False
        self.next=time.monotonic()+.25;self.polls+=1
        if self.polls>512:self.stopped=True;return True
        f=None;record={'closeEntered':False,'closeReturned':False};self.close_records.append(record)
        try:
            f=self.path.open('rb');self.files.append(f);raw=f.read(1025)
            parse_stop(raw,self.body);self.stopped=True
        except FileNotFoundError:return False
        except BaseException:
            self.stopped=True
        finally:
            if f is not None:
                record['closeEntered']=True
                try:f.close();record['closeReturned']=True
                except BaseException:self.unknown=True;self.stopped=True
        return self.stopped
    def request(self,reason):
        self.stopped=True
        if self.write_entered:return
        self.write_entered=True;f=None;record={'closeEntered':False,'closeReturned':False};self.close_records.append(record)
        try:
            f=self.path.open('xb');self.files.append(f);data=encoded(self.body)
            if f.write(data)!=len(data):raise IOError('STOP_SHORT_WRITE')
            f.flush()
        except FileExistsError:return
        except BaseException:
            raise
        finally:
            if f is not None:
                record['closeEntered']=True
                try:f.close();record['closeReturned']=True
                except BaseException:self.unknown=True
    def returned(self):return not self.unknown and all(f.closed for f in self.files) and all(not r['closeEntered'] or r['closeReturned'] for r in self.close_records)
