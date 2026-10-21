"""Receipt-only T2P analysis; no ADB, production imports or synthetic producer."""
from pathlib import Path
import json,hashlib,datetime
E=Path(__file__).resolve().parent;R=E.parents[2]
p=json.loads((E/'00-features.json').read_text());result=json.loads((E/'result.json').read_text())
raw=bytes.fromhex(p['stdout']['prefixHex']);assert len(raw)==p['stdout']['bytes']==220 and not p['stdout']['prefixTruncated']
assert hashlib.sha256(raw).hexdigest()==p['stdout']['sha256']
assert 'shell_v2' in raw.decode('ascii').splitlines()
assert 'shell_v2' not in raw.decode('ascii').strip().split(',')
assert p['ownership']=='RETURNED' and p['originalExitCode']==0 and p['stdinCloseReturned'] and p['sourceCloseReturned'] and p['writerReturned'] and p['stdout']['closeReturned'] and p['stderr']['closeReturned']
assert result['metadataCommands']==1 and result['producerAttempts']==0 and result['retainedLocalOwners']==0
(E/'features-original-stdout.txt').write_bytes(raw)
facts={'at':datetime.datetime.now().astimezone().isoformat(),'conclusion':'NOT_ADMITTED_FEATURE_PARSER_FALSE_NEGATIVE','actualFeaturePresent':'shell_v2','featureFormat':'CRLF-separated lines, no comma','toolPredicate':'decode(ascii).strip().split(comma) exact membership rejects this actual output','metadataCommands':1,'producerAttempts':0,'actualSyntheticSourceReadBytes':0,'actualPayloadSubmittedBytes':0,'deviceDiagnosticHashBytes':0,'realMediaContentBytes':0,'historyLstatCalls':0,'newDiagnosticDirectoryCreated':False,'contextOrProcessSnapshotExecuted':False,'originalClientExit':0,'originalClientElapsedSeconds':p['elapsedSeconds'],'retainedLocalOwners':0,'priorRemoteOwnership':result['priorRemoteOwnership'],'automaticRetry':False,'D1Passed':False,'M0Started':False,'inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':f.relative_to(R).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(E.rglob('*')) if f.is_file() and f.name not in {'evidence-manifest.json','review-summary.json','coordinator-notification.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps(facts,ensure_ascii=False))
