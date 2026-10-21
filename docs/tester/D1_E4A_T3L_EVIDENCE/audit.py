"""Receipt-only localization analysis. No new device or payload access."""
from pathlib import Path
import hashlib,json,datetime,shlex
E=Path(__file__).resolve().parent;R=E.parents[2];result=json.loads((E/'result.json').read_text());review=json.loads((E/'local-review.json').read_text());records=[]
for i,name in [(1,'guards-options-and-bounded-hash'),(2,'one-original-pid-metadata')]:
 p=json.loads((E/f'{i:02d}-{name}.json').read_text());records.append(p);assert p['ownership']=='RETURNED' and p['originalExitCode']==0 and p['stdinCloseReturned'] and p['sourceCloseReturned'] and p['writerReturned']
 for side in ['stdout','stderr']:
  s=p[side];raw=bytes.fromhex(s['prefixHex']);assert len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and not s['prefixTruncated'] and s['closeReturned'] and not s['error'];(E/(name+'-original-'+side+'.txt')).write_bytes(raw)
 script='read_guards.sh' if i==1 else 'read_receiver.sh';assert shlex.split(p['argv'][-1])==[(E/script).read_text()]
raw=bytes.fromhex(records[0]['stdout']['prefixHex']).decode().replace('\r\n','\n');lines=raw.splitlines()
pre=next(x for x in lines if x.startswith('T3L_PRE_STAT|rc=0|')).split('|')[2:];post=next(x for x in lines if x.startswith('T3L_POST_STAT|rc=0|')).split('|')[2:];assert pre==post
assert pre==['64522','7123','10221','8180','26','1792202151']
sha_line=next(x for x in lines if x.startswith('T3L_HASH_RESULT|rc=0|'));digest=sha_line.split('|',2)[2].split()[0]
expected_prefix=hashlib.sha256(bytes(range(26))).hexdigest();assert digest==expected_prefix=='b858da80d8a57dc546905fd147612ebddd3c9188620405d058f9ee5ab1e6bc52'
assert 'T3L_SET_C|rc=0|' in raw and 'noclobber      on' in raw and 'T3L_WINDOW_METADATA_UNCHANGED' in raw and raw.count('T3L_HASH_STARTED|')==1
proc=bytes.fromhex(records[1]['stdout']['prefixHex']).decode();assert 'T3L_PROC_STAT|pid=16643|rc=1|' in proc and 'No such file or directory' in proc
assert result['metadataCommands']==2 and result['retainedLocalOwners']==0
assert hashlib.sha256((R/'docs/tester/D1_E4A_T3R_DIAGNOSTIC_REPORT_V1.0.md').read_bytes()).hexdigest()=='59253ca14fc524925d96c8bcb2876ca6d2374315abc4eaa4968de40f6bf34293'
facts={'at':datetime.datetime.now().astimezone().isoformat(),'conclusion':'CURRENT_SYNTHETIC_FILE_26B_EXPECTED_PREFIX_SHA_MATCH','currentTarget':{'device':64522,'inode':7123,'uid':10221,'modeHex':'8180','size':26,'mtime':1792202151,'sha256':digest},'prePostAvailableStatFieldsEqual':True,'hashDeviceCalls':1,'syntheticDeviceContentHashBytes':26,'targetStatCalls':2,'metadataCommands':2,'producerAttempts':0,'mediaContentBytes':0,'firstUnlandedExpectedByteIndex':26,'firstUnlandedExpectedByteHex':'1a','setCObserved':'RETURN0_NOCLOBBER_ON','originalReceiverPid16643':'ONE_STAT_RC1_NO_SUCH_FILE_REST_SKIPPED','procFdLinkCalls':0,'originalT3RFailureSubstepAndExactLayer':'UNKNOWN_NOT_RETROACTIVELY_PROVEN','originalT3RReportUnchanged':True,'retainedLocalOwners':0,'priorRemoteOwnership':'UNKNOWN_NOT_CLEARED','recordedClientElapsedSeconds':[p['elapsedSeconds'] for p in records],'stdoutBytes':[p['stdout']['bytes'] for p in records],'stderrBytes':[p['stderr']['bytes'] for p in records],'inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(E.rglob('*')) if p.is_file() and p.name not in {'evidence-manifest.json','review-summary.json','coordinator-notification.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8');print(json.dumps(facts,ensure_ascii=False))
