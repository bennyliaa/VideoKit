"""Independent local review of actual raw fixture receipt before conditional QUERY admission."""
from common import *
plan=artifacts();receipt=load('07-isolated-fixture-receipt.json')
b=(E/'07-isolated-fixture-stdout.txt').read_bytes();s=b.decode('utf-8').replace('\r\n','\n')
assert receipt['exitCode']==0 and receipt['clientReturned'] and not receipt['overflow'] and sha(b)==receipt['sha256']
assert receipt['elapsedSeconds']<60 and len(b)<4*1024*1024
assert 'OK (1 test)' in s and 'INSTRUMENTATION_CODE: -1' in s
assert s.count('stream=E5C_LOCK_BOUNDARY_PASS\n')==1
for forbidden in ['FAILURES','E5C_PENDING','E5C_BLOCKED','actualReturn=UNKNOWN','close=UNKNOWN','returned=false']:
    assert forbidden not in s,forbidden
case_lines=[x.split('stream=',1)[1] for x in s.splitlines() if 'stream=E5C_CASE ' in x]
assert len(case_lines)==3
for name,result in [('healthy','HEALTHY_TWO_LOCKS_CLOSED'),('owner_symlink','TRUE_SYMLINK_REJECTED'),('lease_symlink','TRUE_SYMLINK_REJECTED')]:
    assert any(x==f'E5C_CASE {name} result={result} metadataBytes=UNCHANGED R_count=0 S_count=0 liveGrant=false actualReturn=CLOSED fullObserve=NOT_RUN' for x in case_lines)
assert s.count('E5C_RAW_NOFOLLOW errno=ELOOP actualClose=CLOSED')==2
assert s.count('E5C_ACTUAL_FD allocation=RAW_AND_DUP close=CLOSED')==3
assert s.count('E5C_ACTUAL_FD allocation=NONE_PREOPEN_REJECTION close=CLOSED')==2
assert s.count('state=CLOSED returned=true')==5
links=re.findall(r'E5C_TRUE_SYMLINK path=(\S+) readlink=(\S+) kind=S_IFLNK originalDev=(\d+) originalInode=(\d+) bytes=(\d+) sha256=([a-f0-9]{64})',s)
assert len(links)==2
for path,target,dev,ino,size,h in links:
    assert target==path+'.original-target' and int(dev)>0 and int(ino)>0
    assert (path.endswith('.owner') and size=='0' and h==sha(b'')) or (path.endswith('.lease') and size=='36')
assert 'metadata=ASSUMED_SYNTHETIC_NOT_EXECUTED death=ASSUMED_SYNTHETIC_NOT_EXECUTED fullObserve=NOT_RUN originalN2=NOT_RUN' in s
assert load('deployment-result.json')['originalStateUnchanged']
value=dict(admitted=True,scope='SAME_FORMALLY_AUTHORIZED_BATCH_FIXED_READONLY_QUERY_ONLY',fixture='PASS',G01='PASS_ACTUAL_ANDROID_ORIGINAL_OBSERVATION_LOCK_BOUNDARY_ONLY',fullObservation='NOT_RUN',recovery='NOT_RUN',rawReceiptSha256=sha(b),receiptPath=str(E/'07-isolated-fixture-stdout.txt'),junitTests=1,junitSeconds=float(re.search(r'\nTime: ([0-9.]+)',s).group(1)),adbSeconds=receipt['elapsedSeconds'],cases=case_lines,trueSymlinks=[dict(path=p,target=t,dev=int(d),inode=int(i),bytes=int(n),sha256=h) for p,t,d,i,n,h in links],actualGuardRawAndDupPairsClosed=3,preopenRejectionsWithoutFD=2,independentNoFollowEloopProbes=2,allOriginalHoldersReturned=True,sourceAssertsSnapshotAndGrantAndBounds=True,queryArguments=plan['queryArguments'],noWriteRecoveryAuthorization=True)
save('fixture-independent-admission.json',value)
print(json.dumps(value,ensure_ascii=False))
