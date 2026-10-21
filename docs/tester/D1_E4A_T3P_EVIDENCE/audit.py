"""Read existing T3P receipts only; no device or media queries."""
from pathlib import Path
import json,hashlib,datetime
E=Path(__file__).resolve().parent;R=E.parents[2]
result=json.loads((E/'result.json').read_text());records=[]
for name in ['00-features','01-context','02-prior-uid-processes']:
 q=json.loads((E/(name+'.json')).read_text());records.append(q)
 assert q['ownership']=='RETURNED' and q['originalExitCode']==0 and q['originalExitObserved'] and q['stdinCloseReturned'] and q['sourceCloseReturned'] and q['writerReturned']
 for side in ['stdout','stderr']:
  s=q[side];raw=bytes.fromhex(s['prefixHex']);assert len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and not s['prefixTruncated'] and s['closeReturned'] and s['error'] is None
  if side=='stdout':(E/(name+'-original-stdout.txt')).write_bytes(raw)
features=bytes.fromhex(records[0]['stdout']['prefixHex']);context=bytes.fromhex(records[1]['stdout']['prefixHex']).decode();ps=bytes.fromhex(records[2]['stdout']['prefixHex']).decode()
assert 'shell_v2' in features.decode('ascii').splitlines()
assert '|uid=10221|pwd=/data/user/0/com.videokit.app' in context
selfpid=ps.splitlines()[0].rsplit('=',1)[1];observed=[]
for line in ps.splitlines()[1:]:
 fields=line.split(None,3)
 if len(fields)==4 and fields[0].isdigit() and fields[2]=='10221' and fields[0]!=selfpid and fields[3].startswith('tee files/e4_fixtures/basic.mp4'):
  observed.append({'pid':int(fields[0]),'ppid':int(fields[1]),'uid':int(fields[2]),'args':fields[3]})
assert observed==[{'pid':7722,'ppid':7718,'uid':10221,'args':'tee files/e4_fixtures/basic.mp4'}]
assert result['firstFailure']=='POSSIBLE_PRIOR_RECEIVER_STOP_NO_KILL' and result['metadataCommands']==3 and result['producerAttempts']==0 and result['retainedLocalOwners']==0
facts={'at':datetime.datetime.now().astimezone().isoformat(),'conclusion':'NOT_ADMITTED_PRIOR_RECEIVER_OBSERVED','originalFeatureBytes':len(features),'originalFeatureSha256':hashlib.sha256(features).hexdigest(),'featureParserActualGate':'PASS','actualContext':context.strip(),'snapshotSelfPid':int(selfpid),'observedPriorReceiverCandidates':observed,'remoteProcessCreationTimeOrOriginalBatchBinding':'NOT_OBSERVED','oldRemoteOwnership':'UNKNOWN_NOT_CLEARED','metadataCommands':3,'producerAttempts':0,'syntheticSourceReadBytes':0,'payloadSubmittedBytes':0,'deviceHashBytes':0,'realMediaContentBytes':0,'historicalLstatCalls':0,'newDiagnosticDirectoryCreated':False,'retainedLocalOwners':0,'originalClientElapsedSeconds':[q['elapsedSeconds'] for q in records],'killCalls':0,'retries':0,'inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(E.rglob('*')) if p.is_file() and p.name not in {'evidence-manifest.json','review-summary.json','coordinator-notification.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps(facts,ensure_ascii=False))
