"""Receipt-only proof of exact OWNER3 action and bounded local review; no device access."""
from pathlib import Path
import hashlib,json,datetime,shlex
E=Path(__file__).resolve().parent;R=E.parents[2]
review=json.loads((E/'local-review.json').read_text());result=json.loads((E/'result.json').read_text())
assert review['status']=='PASS' and hashlib.sha256((E/'owner3_control.sh').read_bytes()).hexdigest()==review['controlSha256']
records=[]
for name in ['01-harmless-compatibility','02-exact-control-and-observation','03-one-post-uid-snapshot']:
 p=json.loads((E/(name+'.json')).read_text());records.append(p)
 assert p['ownership']=='RETURNED' and p['status']=='PROCESS_IO_COMPLETE_ONLY' and p['originalExitCode']==0 and p['stdinCloseReturned'] and p['sourceCloseReturned'] and p['writerReturned']
 for side in ['stdout','stderr']:
  s=p[side];raw=bytes.fromhex(s['prefixHex']);assert len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and not s['prefixTruncated'] and s['closeReturned'] and not s['error'];(E/(name+'-original-'+side+'.txt')).write_bytes(raw)
out=bytes.fromhex(records[1]['stdout']['prefixHex']).decode().replace('\r\n','\n')
assert shlex.split(records[1]['argv'][-1])==[(E/'owner3_control.sh').read_text()]
assert 'OWNER3_UIDS|10221 10221 10221 10221' in out
assert 'OWNER3_FD3_TARGET_STAT|64522|21416|10221' in out and 'OWNER3_ARCHIVE_STAT|64522|21416|10221' in out
assert out.count('OWNER3_TERM_ATTEMPT|pid=7722')==1 and 'OWNER3_TERM_RETURN|rc=0' in out and 'OWNER3_OBSERVATION|GONE|pid=7722|ticks=7571831' in out
assert result['termAttempts']==1 and result['metadataCommands']==3 and result['retainedLocalOwners']==0
post=bytes.fromhex(records[2]['stdout']['prefixHex']).decode();assert not any(line.split() and line.split()[0]=='7722' for line in post.splitlines())
assert hashlib.sha256((R/'docs/tester/D1_E4A_OWNER2_REPORT_V1.0.md').read_bytes()).hexdigest()=='b94cfa560edc009c7044749922368d39ee8644e063068b126875a058d7ddac04'
facts={'at':datetime.datetime.now().astimezone().isoformat(),'conclusion':'PASS_SCOPED_ORIGINAL_OWNER_ENDED','originalIdentity':{'pid':7722,'startTicks':7571831,'ppid':7718,'uid':10221,'fd':3,'device':64522,'inode':21416},'termAttempts':1,'termOriginalReturn':0,'originalIdentityObservation':'PROC_GONE','localReviewAssertions':19,'localShellSyntaxAndFieldProcesses':2,'deviceMetadataCommands':3,'recordedClientElapsedSeconds':[p['elapsedSeconds'] for p in records],'stdoutBytes':[p['stdout']['bytes'] for p in records],'stderrBytes':[p['stderr']['bytes'] for p in records],'parentProcReads':0,'otherSignals':0,'killNamesListIsNotSignal':True,'mediaContentBytes':0,'localRetainedOwners':0,'otherHistoricalRemoteOwnership':'UNKNOWN_NOT_CLEARED','currentArchiveContentHash':'NOT_READ','oldReportUnchanged':True,'inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(E.rglob('*')) if p.is_file() and p.name not in {'evidence-manifest.json','review-summary.json','coordinator-notification.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps(facts,ensure_ascii=False))
