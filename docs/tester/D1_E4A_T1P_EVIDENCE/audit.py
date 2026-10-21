"""Analyze existing batch receipts only. No process, device or media access."""
from pathlib import Path
import json,hashlib,datetime
E=Path(__file__).resolve().parent;R=E.parents[2]
records=[]
for p in E.glob('*.json'):
 if p.name.endswith('-backend-logs.json'):records+=json.loads(p.read_text())
 elif p.name not in {'batch-result.json','batch-start.json','preflight-admitted.json','audit-summary.json','evidence-manifest.json','coordinator-notification.json','review-summary.json'} and not p.name.endswith(('.attempt.json','.result.json')):
  q=json.loads(p.read_text())
  if isinstance(q,dict) and 'originalExitObserved' in q:records.append(q)
batch=json.loads((E/'batch-result.json').read_text());logs=json.loads((E/'basic.mp4-backend-logs.json').read_text());result=batch['results'][0]
assert len(batch['results'])==1 and result['status']=='NOT_ADMITTED'
assert result['transfer']['submittedBytes']==349102 and result['transfer']['originalExitCode']==0
assert all(q['ownership']=='RETURNED' and q['stdinCloseReturned'] and q['sourceCloseReturned'] and q['stdout']['closeReturned'] and q['stderr']['closeReturned'] and q['writerReturned'] for q in records)
raw=lambda q:bytes.fromhex(q['stdout']['prefixHex']).decode('utf-8')
assert raw(logs[-1]).splitlines()==['E4AT_ABSENT']
probes=[]
for q in logs:
 lines=raw(q).splitlines()
 if lines and lines[0]=='E4AT_FILE':probes.append({'length':int(lines[1]),'sha256':lines[2].split()[0],'path':lines[2].split()[1]})
assert len(probes)==2 and all(q['length']==81407 and q['sha256']=='a790f44fc3c6ff4579c83f57b42a4b31cd95278cca28fd4aa6b97fd295fd9695' for q in probes)
budget=sum(p.stat().st_size for p in E.rglob('*') if p.is_file())
facts={'at':datetime.datetime.now().astimezone().isoformat(),'callRecords':len(records),'allRecordedOriginalClientOwnersReturned':True,'retainedOriginalProcessOwners':0,'mp4':'NOT_ADMITTED_INDEPENDENT_TEMP_ABSENT','avi':'BLOCKED_NOT_OPENED','residualProbes':probes,'hostSourcePrehashBytes':349102,'hostSourceStreamReadBytes':349102,'submittedPayloadBytes':349102,'deviceFixtureContentHashBytes':162814,'deviceNewTempContentHashBytes':0,'deviceInstalledApkHashBytes':13309805,'clientProducerElapsedSeconds':result['transfer']['elapsedSeconds'],'producerExit':0,'remoteProducerLifecycle':'UNKNOWN_NOT_INFERRED_FROM_LOCAL_RETURN','realMediaStatOrReadAfterBatch':False,'evidenceBytesBeforeAudit':budget,'productTests':0,'phoneOrEmulatorCalls':0,'installs':0,'gradleRuns':0,'retries':0,'inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(E.rglob('*')) if p.is_file() and p.name not in {'evidence-manifest.json','coordinator-notification.json','review-summary.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps(facts,ensure_ascii=False))
