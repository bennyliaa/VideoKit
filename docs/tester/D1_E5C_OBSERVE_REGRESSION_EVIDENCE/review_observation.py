"""Independent local review of actual final observation before normal regression."""
from common import *
r=load('02-original-observation-receipt.json');raw=(E/'02-original-observation-stdout.txt').read_bytes();s=raw.decode().replace('\r\n','\n')
assert r['exitCode']==0 and r['clientReturned'] and not r['overflow'] and sha(raw)==r['sha256']
assert 'OK (1 test)' in s and 'INSTRUMENTATION_CODE: -1' in s and 'BLOCKED' not in s and 'FAILURES' not in s
assert s.count('E5A_FINAL_OBSERVATION FRESH_OBSERVATION_ADMITTED')==1
assert 'oldRecoveryResult=UNCHANGED oldSyncReturn=NOT_INFERRED oldCloseACK=false' in s
match=re.search(r'recoveryAttempt=([a-f0-9-]{36}) recoveryPid=(\d+) uid=(\d+) process=(\S+) ownerRecordedAt=(\d+) exitTimestamp=(\d+) reason=(\d+) status=(-?\d+) absent=true;',s)
assert match
a,p,u,n,b,t,reason,status=match.groups()
assert a=='8c6673b7-38a5-4a24-838d-ca8466d8b75f' and p=='4869' and u=='10221' and n=='com.videokit.app' and b=='1792224193301' and int(t)>=int(b) and int(reason)>0
ledger=load('observation-client-result.json')['ledger'];assert not ledger['pending'] and ledger['reserved']==0 and ledger['consumed']==0 and len(ledger['records'])==1
value=dict(admitted=True,scope='SAME_AUTHORIZED_BATCH_ORDERED_FOUR_EXACT_METHODS',observation='PASS',ledger=ledger,writerDeath=dict(attempt=a,pid=int(p),uid=int(u),process=n,ownerRecordedAt=int(b),exitTimestamp=int(t),reason=int(reason),status=int(status),procAbsent=True,uniqueMatch='REQUIRED_AND_PASSED_BY_FROZEN_ADAPTER'),current15FilesForceCloseAndDirectorySync='PASSED_REAL_RETURN_GATE_IN_FROZEN_IMPLEMENTATION',individualFdNumbersOrSyscallTrace='NOT_SEPARATELY_COLLECTED',metadataUnchanged=True,rawSha256=sha(raw),junitSeconds=float(re.search(r'\nTime: ([0-9.]+)',s).group(1)),hostLiveProof='DOES_NOT_CROSS_PROCESS_EACH_PRODUCT_MUST_OBSERVE_AGAIN',oldRecoveryResult='UNCHANGED',oldCloseAck=False,newAbortAuthorized=False)
save('observation-independent-admission.json',value);print(json.dumps(value,ensure_ascii=False))
