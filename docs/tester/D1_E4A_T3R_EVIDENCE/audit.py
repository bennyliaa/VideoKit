"""Audit only saved T3R evidence; no extra device probe or payload read."""
from pathlib import Path
import json,hashlib,datetime
E=Path(__file__).resolve().parent;R=E.parents[2];result=json.loads((E/'result.json').read_text());records=[]
for row in result['records']:
 p=json.loads((E/row['file']).read_text());records.append(p)
 assert p['ownership']=='RETURNED' and p['originalExitObserved'] and p['stdinCloseReturned'] and p['sourceCloseReturned'] and p['writerReturned']
 for side in ['stdout','stderr']:
  s=p[side];raw=bytes.fromhex(s['prefixHex']);assert len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and not s['prefixTruncated'] and s['closeReturned'] and not s['error'];(E/(row['stage']+'-original-'+side+'.txt')).write_bytes(raw)
p=records[-1];raw=bytes.fromhex(p['stdout']['prefixHex']).decode();lines=raw.splitlines();assert len(lines)==1 and lines[0].startswith('E4T2_BEGIN|E4T3P_TABLET_20261017_ONCE|')
begin=dict(x.split('=',1) for x in lines[0].split('|')[2:]);assert begin=={'uid':'10221','pid':'16643','pwd':'/data/user/0/com.videokit.app','path':'files/e4_diag_T3P_TABLET_20261017_once/payload256.bin'}
assert p['originalExitCode']==1 and p['errors']==['PROCESS_NONZERO_EXIT'] and p['submittedBytes']==256 and p['sourcePrehashBytes']==256 and p['sourceStreamReadBytes']==256 and p['submittedSha256']=='40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880'
assert result['producerAttempts']==1 and result['metadataCommands']==5 and len(records)==6 and result['retainedLocalOwners']==0
assert hashlib.sha256((R/'docs/tester/D1_E4A_T3P_DIAGNOSTIC_REPORT_V1.0.md').read_bytes()).hexdigest()=='5e6d3deee69d4e0a672ab2e4b35ddfa6637ef2218e3c8a5c1125803ba50736fc'
assert hashlib.sha256((R/'docs/tester/D1_E4A_OWNER3_REPORT_V1.0.md').read_bytes()).hexdigest()=='8b155c402c61ab52ac95e17247fd030975a909cfaa0b375ec52b0879ef1a6540'
facts={'at':datetime.datetime.now().astimezone().isoformat(),'externalBatch':'D1-E4A-T3R-TABLET-20261017','internalFrozenToolBatch':result['batch'],'reuseAuthority':'docs/milestones/D1_E4A_T3R_TESTER_REQUIREMENTS_V1.0.md','conclusion':'NOT_ADMITTED_RECEIVER_EXIT1_BEGIN_ONLY','actualBegin':begin,'actualEnd':'NOT_OBSERVED','remoteFailureSubstep':'UNKNOWN','landedLengthAndSha':'UNKNOWN_NOT_INDEPENDENTLY_PROBED','newDiagnosticDirectory':'CREATION_MARKER_OBSERVED','hostSyntheticReadBytes':512,'submittedBytes':256,'deviceIndependentHashBytes':0,'realMediaContentBytes':0,'historyExactLstatCommands':1,'metadataCommands':5,'producerAttempts':1,'originalClientCalls':6,'recordedClientElapsedSeconds':[x['elapsedSeconds'] for x in records],'stdoutBytes':[x['stdout']['bytes'] for x in records],'stderrBytes':[x['stderr']['bytes'] for x in records],'retainedLocalOwners':0,'priorRemoteOwnership':'UNKNOWN_NOT_CLEARED','newReceiverFullCompletion':'UNPROVEN','oldT3PAndOwner3ReportsUnchanged':True,'inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':f.relative_to(R).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(E.rglob('*')) if f.is_file() and f.name not in {'evidence-manifest.json','review-summary.json','coordinator-notification.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8');print(json.dumps(facts,ensure_ascii=False))
