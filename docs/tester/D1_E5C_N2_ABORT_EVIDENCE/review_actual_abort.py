"""Local independent proof/chain/identity review of the single actual ABORT, no device action."""
from common import *
import uuid
before=(E/'human-01-original-private-stdout.txt').read_text().replace('\r\n','\n')
post=(E/'03-post-abort-private-stdout.txt').read_text().replace('\r\n','\n')
out=(E/'02-original-abort-stdout.txt').read_text().replace('\r\n','\n')
receipt=load('02-original-abort-receipt.json')
assert receipt['exitCode']==0 and receipt['clientReturned'] and not receipt['overflow']
assert 'OK (1 test)' in out and 'INSTRUMENTATION_CODE: -1' in out
assert 'ABORTED_SETTLED' in out and 'retainedBytes=0 sha='+sha(b'')+' originalCloseACK=false retainedOperations=0' in out
assert 'BLOCKED' not in out and 'FAILURES' not in out
def hexes(s):return {p:bytes.fromhex(h) for p,h in re.findall(r'HEX_BEGIN\|([^\n]+)\n(.*?)HEX_END',s,re.S)}
def stats(s,prefix='STAT'):return {p:v.split(',') for p,v in re.findall(r'^'+prefix+r'\|([^|\n]+)\|([^\n]+)',s,re.M)}
prehex=hexes(before);data=hexes(post);prestat=stats(before);st=stats(post);ds=stats(post,'DATA_STAT')
bud='files/e4a_output_budget/';od='files/e4a_outputs/'+TASK;arc=bud+'N2-e5-recovery/'
original=before.split('LEDGER_BEGIN\n')[1].split('LEDGER_END')[0].encode()
assert data[arc+'ledger.before']==original
for suffix in ['identity','journal','lease']:assert data[arc+suffix+'.before']==prehex[od+'.'+suffix]
assert data[od+'.identity']==prehex[od+'.identity']
assert st[od+'.identity']==prestat[od+'.identity']
assert data[bud+'identity.anchor']==BUDGET.encode() and st[bud+'identity.anchor']==prestat[bud+'identity.anchor']
oldlease=prehex[od+'.lease'].decode();fence=data[od+'.lease'].decode();assert str(uuid.UUID(fence))==fence and fence!=oldlease
def utf_read(b,offset):
    n=struct.unpack_from('>H',b,offset)[0];offset+=2;return b[offset:offset+n].decode(),offset+n
j=data[od+'.journal'];assert struct.unpack_from('>I',j)[0]==0x45344131
task,offset=utf_read(j,4);state=struct.unpack_from('>i',j,offset)[0];epoch,offset=utf_read(j,offset+4)
assert task==TASK and state==2 and epoch==fence and j[offset:]==b'\1'
assert st[od+'.lease'][:4]==prestat[od+'.lease'][:4]
assert st[od+'.owner']==prestat[od+'.owner'] and data[od+'.owner']==b''
assert ds[od+'.mp4']==prestat[od+'.mp4'] and ds[od+'.mp4'][2]=='0'
proof=data[arc+'proof.txt'].decode();lines=proof.splitlines();assert len(lines)==6 and lines[0]=='E5_N2_DEATH_FENCE_ABORT_V1'
assert lines[3]=='originalCloseACK=false' and lines[4]=='fence='+fence
exit_records=[]
for line,pid,process in zip(lines[1:3],[24853,24873],['com.videokit.app','com.videokit.app:e4_codec']):
    p=line.split();assert p[0]==str(pid) and p[1]=='10221' and p[2]==process and p[-1]=='absent=true'
    assert 1792208947872<=int(p[3])<=1792208970000 and int(p[4])>0
    assert out.count(line+';')==2 # Actual checks before and again under both original locks.
    exit_records.append(dict(pid=pid,uid=10221,process=process,timestamp=int(p[3]),reason=int(p[4]),status=int(p[5]),procAbsent=True))
payload=f'S {TASK} ABORTED 0 '+sha(b'')
oldchain=original.decode().splitlines()[-1].split()[-1]
chain=sha((oldchain+' '+payload).encode());settlement=(payload+' '+chain+'\n').encode()
assert data[bud+'ledger.bin']==original+settlement
assert lines[5].encode()+b'\n'==settlement
assert data[bud+'ledger.bin'].count(b'\nS ')==1 and len(data[bud+'ledger.bin'])==371
assert st[bud+'ledger.bin'][:2]==prestat[bud+'ledger.bin'][:2]
assert 'ABSENT|'+bud+'operation.pending\n' in post
assert data[bud+'operation.pending.N2-e5-aborted']==b''
assert st[bud+'operation.pending.N2-e5-aborted']==prestat[bud+'operation.pending']
assert data[bud+'N2-e5-recovery.complete']==('E5_N2_ABORTED_SETTLED '+TASK+' '+BUDGET+'\n').encode()
record=data[arc+'guard.identity'];assert len(record)==82 and struct.unpack_from('>I',record)[0]==0x45354231
task,offset=utf_read(record,4);assert task==TASK
guard_ids=[]
for suffix in ['owner','lease']:
    dev,ino,uid=struct.unpack_from('>qqi',record,offset);offset+=20
    fields=prestat[od+'.'+suffix];assert [str(dev),str(ino),str(uid)]==[fields[0],fields[1],fields[3]]
    assert st[od+'.'+suffix][:4]==fields[:4]
    guard_ids.append(dict(role=suffix,device=dev,inode=ino,uid=uid))
assert offset==82
w=data[arc+'recovery.owner'].decode();parts=w.strip().split();assert len(parts)==6 and parts[0]=='E5A_N2_RECOVERY_OWNER_V1'
assert str(uuid.UUID(parts[1]))==parts[1] and int(parts[2]) not in [24853,24873] and parts[3]=='10221' and parts[4]=='com.videokit.app' and int(parts[5])>=1792208970000
assert w==' '.join(parts)+'\n'
for p in ['files/e4_fixtures/basic.mp4','files/e4_fixtures/subtitle.avi']:
    old=next(x.split('|')[2] for x in before.splitlines() if x.startswith('FIXTURE_STAT|'+p+'|'));assert ds[p]==old.split(',')
assert 'TEMP_PRESENT|' not in post
assert sum(map(len,data.values()))==int(re.search(r'METADATA_READ_BYTES\|(\d+)',post).group(1))==1974
rows=[json.loads(p.read_bytes()) for p in sorted(E.glob('*-receipt.json'))]
assert len(rows)==6 and all(r['clientReturned'] and r['exitCode']==0 and not r['overflow'] for r in rows)
meta=[r for r in rows if r['argv'][-1]!=receipt['argv'][-1]]
assert len(list(E.glob('metadata-*-intent.json')))==5 and all(r['elapsedSeconds']<=15 for r in meta)
total=sum(r['savedBytes'] for r in rows);assert total<8*1024*1024
for p,b in data.items():
    name=('post-'+p.split('/')[-1]+'.bin')
    if p.startswith(arc):name='archive-'+p.split('/')[-1]+'.bin'
    with (E/name).open('xb') as f:f.write(b)
value=dict(result='PASS_ABORTED_SETTLED_ONCE_NO_FOLLOWUP',humanApproval='DIRECT_APPROVAL_RECORDED',originalTask=TASK,budget=BUDGET,oldFence=oldlease,newFence=fence,journalState='ABORTED',retainedOutputBytes=0,retainedOutputSha256=sha(b''),originalOutputInodePreserved=True,originalOwnerAndLeaseInodesPreserved=True,guardIdentity=guard_ids,beforeImagesExact=True,originalRPreserved=True,uniqueS=settlement.decode().strip(),settlementChain=chain,ledgerBytes=371,ledgerSha256=sha(data[bud+'ledger.bin']),logicalReservedBytesAfterSettlement=0,logicalActualConsumedBytes=0,pending='ARCHIVED_SAME_INODE_20492',completeBytes=96,recoveryWriter=dict(attempt=parts[1],pid=int(parts[2]),uid=10221,process=parts[4],began=int(parts[5])),originalDeathEvidence=exit_records,originalCloseAck=False,recoveryRetainedOperations=0,recoveryOwnedResources='ACTUAL_RETURN_GATED_BY_FROZEN_PRODUCTION_IMPLEMENTATION_AND_SUCCESS_RECEIPT',individualFdNumbersOrSyscallTrace='NOT_SEPARATELY_COLLECTED',newHostObservation='NOT_RUN',writerDeathAfterRecovery='NOT_QUERIED',newHostAdmission='NOT_GRANTED_BY_THIS_REPORT',fixtureStatsUnchanged=True,junitSeconds=float(re.search(r'\nTime: ([0-9.]+)',out).group(1)),abortAdbSeconds=receipt['elapsedSeconds'],abortRawSha256=sha((E/'02-original-abort-stdout.txt').read_bytes()),postRawSha256=sha((E/'03-post-abort-private-stdout.txt').read_bytes()),abortCalls=1,adbCallsIncludingPriorPreflight=6,metadataCallsIncludingPriorPreflight=5,currentHumanApprovedAdbCalls=4,metadataContentBytesInPostEvidence=1974,metadataCorrectionAttempts=0,batchLogBytes=total,inFlight=[],allCurrentAdbClientsReturned=True,sourceMediaContentHashBytes=0,installCalls=0,gradleOrModelRuns=0,oldN2Failure='UNCHANGED_ROOT_CAUSE_UNKNOWN',normalCases='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
save('actual-abort-independent-review.json',value);print(json.dumps(value,ensure_ascii=False))
