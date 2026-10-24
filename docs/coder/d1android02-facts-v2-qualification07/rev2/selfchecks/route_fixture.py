"""Finite synthetic tables through the real decoder/state machine. No OS queries."""
import json,sys,time,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
B=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]
from win32_route import BACKEND,decode,sample,validate_stats
from route_model import Model
raw=Path(sys.argv[1]).read_bytes();c=decode(raw)
assert len(sys.argv)==2 and len(raw)<=8192 and c['kind']=='OFFLINE_FIXTURE' and c['routeBackend']==BACKEND
time.sleep(c['fixtureDelay'])
model=Model(c['toolSha256']);d=sample(model,c['toolPath'],c['toolSha256'],c['toolBytes']);validate_stats(model.ledger.data,fixture=True)
d.update(schema='ENTRY_LOCAL_ROUTE_V2',kind=c['kind'],scope=c['scope'],planId=c['planId'],generation=c['generation'],checkedAtUtc=datetime.now(timezone.utc).isoformat(),endpoint='127.0.0.1:5037',identityStable=True,routingOverrides={},contextReadBytes=len(raw),queryCount=0,sourceSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),routeBackend=BACKEND,queryStats=model.ledger.data)
fault=c['fixtureFault']
if fault=='route':d['routingOverrides']={'ADB_SERVER_SOCKET':'fixture'}
elif fault=='generation':d['generation']='other'
elif fault=='source':d['sourceSha256']='0'*64
elif fault=='identity':d['identityStable']=False
elif fault=='future':d['checkedAtUtc']=(datetime.now(timezone.utc)+timedelta(seconds=5)).isoformat()
elif fault=='stale':d['checkedAtUtc']='2020-01-01T00:00:00+00:00'
elif fault=='path':d['serverImage']='C:/wrong/adb.exe'
elif fault=='missing':del d['serverPid']
elif fault=='type':d['serverPid']=True
elif fault=='extra':d['unreviewed']=True
elif fault=='endpoint':d['endpoint']='0.0.0.0:5037'
elif fault!='NONE':raise ValueError('FIXTURE_FAULT_ONLY')
print(json.dumps(d,separators=(',',':')))
