"""Parse saved /proc metadata only. No device, content or signal operations."""
from pathlib import Path
import json,hashlib,datetime
E=Path(__file__).resolve().parent;R=E.parents[2]
record=json.loads((E/'01-identity-and-fds.json').read_text());result=json.loads((E/'result.json').read_text())
outs={}
for side in ['stdout','stderr']:
 s=record[side];raw=bytes.fromhex(s['prefixHex']);assert len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and not s['prefixTruncated'];(E/('original-'+side+'.txt')).write_bytes(raw);outs[side]=raw.decode()
text=outs['stdout'].replace('\r\n','\n');assert 'cat: /proc/7718/stat: Permission denied' in outs['stderr'] and record['originalExitCode']==1
line=next(x for x in text.splitlines() if x.startswith('OWNER_STAT|7722|')).split('|',2)[2]
tail=line.rsplit(') ',1)[1].split();ticks=int(tail[19]);assert line.startswith('7722 (tee) ') and tail[1]=='7718'
cmd=next(x for x in text.splitlines() if x.startswith('OWNER_CMDHEX|7722|')).split('|',2)[2];assert bytes.fromhex(cmd)==b'tee\x00files/e4_fixtures/basic.mp4\x00'
fds=[]
for line in text.splitlines():
 if not line.startswith('OWNER_FD_LINK|'):continue
 _,pid,fd,link=line.split('|',3);info=text.split(f'OWNER_FDINFO_BEGIN|{pid}|{fd}\n',1)[1].split(f'OWNER_FDINFO_END|{pid}|{fd}',1)[0];fds.append({'pid':int(pid),'fd':int(fd),'link':link,'fdinfo':info.strip()})
assert len(fds)==4 and fds[3]['fd']==3 and fds[3]['link']=='/data/user/0/com.videokit.app/files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep'
assert result['signalAttempts']==0 and result['metadataCommands']==1 and result['retainedLocalOwners']==0
facts={'at':datetime.datetime.now().astimezone().isoformat(),'conclusion':'BLOCKED_PARENT_PROC_PERMISSION_DENIED_NO_SIGNAL','child':{'pid':7722,'ppid':7718,'startTicks':ticks,'state':tail[0],'uids':[10221]*4,'cmdlineHex':cmd,'cwd':'/data/user/0/com.videokit.app','exe':'/system/bin/toybox'},'observedFdEntries':fds,'parentIdentity':'UNPROVEN_PROC_STAT_PERMISSION_DENIED','archiveInodeAndCurrentContent':'NOT_OBTAINED_NOT_READ','signalAttempts':0,'termControlDispatched':False,'postUidSnapshot':False,'metadataCommands':1,'mediaContentBytes':0,'fdContentBytes':0,'retainedLocalOwners':0,'priorRemoteOwnership':'UNKNOWN_NOT_CLEARED','inFlightLocalOwners':[]}
(E/'audit-summary.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(E.rglob('*')) if p.is_file() and p.name not in {'evidence-manifest.json','review-summary.json','coordinator-notification.json'}]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps(facts,ensure_ascii=False))
