"""Local final review; no ADB, media or model execution."""
from common import *
receipt_files=sorted(E.glob('*-receipt.json'));receipts=[json.loads(p.read_bytes()) for p in receipt_files]
assert len(receipts)==11 and all(r['exitCode']==0 and r['clientReturned'] and not r['overflow'] for r in receipts)
for p,r in zip(receipt_files,receipts):assert sha(p.with_name(p.name.replace('-receipt.json','-stdout.txt')).read_bytes())==r['sha256']
qraw=(E/'08-original-query-stdout.txt').read_bytes();q=qraw.decode('utf-8').replace('\r\n','\n')
assert 'OK (1 test)' in q and 'INSTRUMENTATION_CODE: -1' in q and 'QUERY_ELIGIBLE' in q
assert 'retainedBytes=-1 sha=NOT_READ originalCloseACK=false retainedOperations=0' in q
assert 'FAILURES' not in q and 'BLOCKED' not in q
exits=re.findall(r'(24853|24873) (10221) (com\.videokit\.app(?::e4_codec)?) (\d+) (\d+) (-?\d+) absent=true;',q)
assert len(exits)==2
for pid,uid,name,ts,reason,status in exits:
    assert name==('com.videokit.app' if pid=='24853' else 'com.videokit.app:e4_codec')
    assert 1792208947872<=int(ts)<=1792208970000 and int(reason)>0
    assert f'pid={pid} queryRows=1 uniqueMatches=1;' in q
before=(E/'02-original-private-stdout.txt').read_text().replace('\r\n','\n')
for name in ['06-after-install-private','09-final-private']:
    s=(E/(name+'-stdout.txt')).read_text().replace('\r\n','\n');expected(s);assert core(s)==core(before)
assert load('fixture-independent-admission.json')['admitted'] and load('deployment-result.json')['status']=='PASS'
prior=json.loads((R/'docs/tester/D1_E5C_DEVICE_EVIDENCE/blocked-result.json').read_bytes())
total=sum(r['savedBytes'] for r in receipts);assert total+prior['batchLogBytes']<8*1024*1024
value=dict(result='DEPLOYMENT_PASS_FIXTURE_PASS_QUERY_ELIGIBLE_NO_RECOVERY',continuation='D1-E5C-CONT-TABLET-20261017',deployment='PASS',fixture='PASS_3_CASES_1_JUNIT_METHOD',query='PASS_QUERY_ELIGIBLE',G01='PASS_ACTUAL_ANDROID_PRODUCTION_OBSERVATION_LOCK_BOUNDARY_ONLY',oldWindowsSymlink='NOT_RUN_UNCHANGED',fullObservation='NOT_RUN',writeRecovery='NOT_RUN_NOT_AUTHORIZED',productFourCases='NOT_RUN_NOT_AUTHORIZED',device='HA1Q6WXR',uid=10221,testUid=10222,installedVersionCode=5,originalMetadataAndFixtureStatUnchanged=True,originalLedger='R2097152_NO_S',originalPending=True,originalOutputBytes=0,originalProtocolCloseAck=False,originalN2RootCause='UNKNOWN',queryExitEvidence=[dict(pid=int(p),uid=int(u),process=n,timestamp=int(t),reason=int(r),status=int(s),procAbsent=True) for p,u,n,t,r,s in exits],queryRawSha256=sha(qraw),queryJunitSeconds=float(re.search(r'\nTime: ([0-9.]+)',q).group(1)),fixtureRawSha256=load('fixture-independent-admission.json')['rawReceiptSha256'],adbCalls=11,metadataCalls=7,installCalls=2,instrumentationCalls=2,fixtureCalls=1,queryCalls=1,readOnlyCorrectiveAttemptsUsed=0,reusedPriorSuccessfulAPKHashes=True,priorAdbCalls=prior['adbCalls'],batchLogBytes=total,priorAndCurrentLogBytes=total+prior['batchLogBytes'],batchLogLimitBytes=8*1024*1024,allCurrentClientOwnersReturned=True,inFlight=[],fixtureOriginalHoldersReturned=True,fixtureRoot='RETAINED_NOT_DELETED',originalN2ProtocolOwners='OLD_UNKNOWN_NOT_UPGRADED_BY_EXIT_RECORD',mediaContentHashBytes=0,candidateModelOrGradleRuns=0,D1='NOT_PASSED',M0='NOT_STARTED')
save('final-independent-review.json',value);print(json.dumps(value,ensure_ascii=False))
