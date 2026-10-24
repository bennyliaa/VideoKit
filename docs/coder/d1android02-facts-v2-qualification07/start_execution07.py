from pathlib import Path
import json,time,hashlib
R=Path(__file__).resolve().parent;p=R/'execution-start.json';assert not p.exists(),'BATCH_START_ONCE'
d=json.loads((R/'batch-declaration07.json').read_bytes());assert d['maxProductGraphs']==50 and d['totalReadReservation']==1006632960 and d['wholeSeconds']==360 and d['stopNew']==320
data=dict(monotonic=time.monotonic(),declarationSha256=hashlib.sha256((R/'batch-declaration07.json').read_bytes()).hexdigest(),startedRevision='REV1',maxRevisions=2,old05Unqueried=True)
with p.open('xb') as f:f.write((json.dumps(data,indent=2)+'\n').encode())
print('Shared batch clock fixed; fresh revision scopes and original caps retained')
