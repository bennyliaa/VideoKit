"""Analyze saved OWNER2 metadata only; no retries, signals or device access."""
from pathlib import Path
import json,hashlib,datetime
E=Path(__file__).resolve().parent;R=E.parents[2]
p=json.loads((E/'01-conditional-term-and-original-observation.json').read_text());result=json.loads((E/'result.json').read_text());outputs={}
for side in ['stdout','stderr']:
 s=p[side];raw=bytes.fromhex(s['prefixHex']);assert len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and not s['prefixTruncated'];(E/('original-'+side+'.txt')).write_bytes(raw);outputs[side]=raw.decode()
assert p['originalExitCode']==127 and 'toybox: Unknown command awk' in outputs['stderr']
line=outputs['stdout'].strip().removeprefix('OWNER2_ORIGINAL_STAT|');tail=line.rsplit(') ',1)[1].split();assert line.startswith('7722 (tee) ') and tail[1]=='7718' and tail[19]=='7571831'
assert 'OWNER2_TERM_ATTEMPT' not in outputs['stdout'] and 'OWNER2_RECHECK_COMPLETE' not in outputs['stdout'] and result['signalAttemptMarkers']==0
assert p['ownership']=='RETURNED' and p['stdinCloseReturned'] and p['sourceCloseReturned'] and p['writerReturned'] and p['stdout']['closeReturned'] and p['stderr']['closeReturned']
facts={'at':datetime.datetime.now().astimezone().isoformat(),'conclusion':'BLOCKED_TESTER_SCRIPT_UNSUPPORTED_TOYBOX_AWK_NO_SIGNAL','finding':'OWNER2-EXEC-01','failureOrigin':'Tester execution script command choice; not product or device permission failure','observedChildStat':{'pid':7722,'ppid':7718,'comm':'tee','state':tail[0],'startTicks':int(tail[19])},'childUidCmdCwdExeFdAndArchiveStatRecheck':'NOT_COMPLETED','remoteCommandExit':127,'elapsedSeconds':p['elapsedSeconds'],'stdoutBytes':p['stdout']['bytes'],'stderrBytes':p['stderr']['bytes'],'metadataCommands':1,'termAttempts':0,'parentProcReads':0,'postObservation':False,'postUidSnapshot':False,'mediaContentBytes':0,'retainedLocalOwners':0,'oldOtherRemoteOwnership':'UNKNOWN_NOT_CLEARED','inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':f.relative_to(R).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(E.rglob('*')) if f.is_file() and f.name not in {'evidence-manifest.json','review-summary.json','coordinator-notification.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps(facts,ensure_ascii=False))
