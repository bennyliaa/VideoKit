"""Local review after auto-approval rejection; no device calls or workaround."""
from common import *
assert load('preflight-result.json')['status']=='PASS'
assert not (E/'abort-stage-attempt.json').exists() and not (E/'02-original-abort-attempt.json').exists()
receipts=[json.loads(p.read_bytes()) for p in sorted(E.glob('*-receipt.json'))]
assert len(receipts)==2 and all(r['exitCode']==0 and r['clientReturned'] and r['elapsedSeconds']<=15 for r in receipts)
original=(E/'01-original-private-stdout.txt').read_text().replace('\r\n','\n');expected(original)
assert core(original)==core((R/'docs/tester/D1_E5C_CONT_EVIDENCE/09-final-private-stdout.txt').read_text().replace('\r\n','\n'))
save('final-independent-review.json',dict(result='BLOCKED_AUTO_APPROVAL_EXACT_ABORT_NOT_RUN',action='ABORT_ORIGINAL_N2',preflight='PASS',execution='NOT_RUN_AUTO_REVIEW_REJECTED',device='HA1Q6WXR',uid=10221,versionCode=5,adbCalls=2,metadataCalls=2,metadataLimit=8,metadataEachObservationLimitSeconds=15,abortCalls=0,instrumentationCalls=0,postAbortEvidence='NOT_RUN_NO_ABORT',batchLogBytes=sum(r['savedBytes'] for r in receipts),clientOwnersReturned=True,inFlight=[],originalMetadataContinuity='EXACT_ORIGINAL_WRITING_R2MiB_NO_S_PENDING',originalN2CloseAck=False,originalN2RootCause='UNKNOWN',writeRecoveryResult='NOT_RUN',observeAndNormal='NOT_RUN_NOT_AUTHORIZED',mediaContentHashBytes=0,installCalls=0,candidateModelOrGradleRuns=0,automaticApprovalRejected=True,directHumanApprovalRequired=True,workaround=False,D1='NOT_PASSED',M0='NOT_STARTED'))
print(json.dumps(load('final-independent-review.json'),ensure_ascii=False))

