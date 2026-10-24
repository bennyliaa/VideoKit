"""Future bounded original evidence writers; no IO runs on import."""
from pathlib import Path
from capture_policy import encoded
class EvidenceUnknown(RuntimeError):pass
class Journal:
    def __init__(self,root):
        self.root=Path(root);self.files=[];self.count=0;self.bytes=0;self.reserved=0;self.errors=[];self.unknown=False
    def write(self,label,value):
        data=encoded(value)
        if len(data)>32768 or self.count>=128 or self.reserved+len(data)>4194304:raise ValueError('EVIDENCE_BOUND_BEFORE_OPEN')
        if type(label) is not str or not label.replace('-','').isalnum():raise ValueError('FIXED_LABEL')
        self.count+=1;self.reserved+=len(data);path=self.root/(str(self.count).zfill(3)+'-'+label+'.json')
        for q in [path,*path.parents]:
            if q.exists() and q.stat().st_file_attributes&1024:raise ValueError('EVIDENCE_NO_REPARSE')
        f=None;row={'path':str(path),'writeEntered':False,'writeReturned':False,'writeAmountUnknown':False,'reservation':len(data),'flushReturned':False,'closeEntered':False,'closeReturned':False,'error':None};self.files.append(row)
        try:
            f=path.open('xb');row['originalFile']=f
            row['writeEntered']=True;n=f.write(data);row['writeBytes']=n;self.bytes+=n
            if n!=len(data):raise IOError('SHORT_EVIDENCE_WRITE')
            row['writeReturned']=True;f.flush();row['flushReturned']=True
        except BaseException as e:
            row['error']=type(e).__name__;row['writeAmountUnknown']=row['writeEntered'] and 'writeBytes' not in row;self.errors.append(row['error']);raise
        finally:
            if f is not None:
                row['closeEntered']=True
                try:f.close();row['closeReturned']=True
                except BaseException as e:self.unknown=True;row['error']=type(e).__name__;raise EvidenceUnknown('ORIGINAL_EVIDENCE_CLOSE_UNKNOWN') from e
        return path
    def returned(self):return not self.unknown and all('originalFile' not in r or r['closeReturned'] for r in self.files)
    def facts(self):return {'bytesKnownLowerBound':self.bytes,'reservedNotRefunded':self.reserved,'writeAmountUnknown':any(r['writeAmountUnknown'] for r in self.files),'files':self.count,'errors':list(self.errors),'returnsKnown':self.returned()}
def chunk_rows(rows,max_bytes=65536):
    """Pure bounded partition before opening any output; never dump a giant list."""
    if type(rows) is not list or len(rows)>4096:raise ValueError('ROWS_BOUND')
    result=[];part=[]
    for row in rows:
        if len(encoded([row]))>max_bytes:raise ValueError('SINGLE_ROW_BOUND')
        if part and len(encoded(part+[row]))>max_bytes:result.append(part);part=[]
        part.append(row)
    if part:result.append(part)
    if len(result)>128:raise ValueError('CHUNK_COUNT_BOUND')
    return result
