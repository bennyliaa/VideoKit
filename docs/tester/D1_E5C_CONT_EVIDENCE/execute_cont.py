"""Authorized E5C continuation; original successful APK hashes reused, no action retry."""
from common import *
PRIOR=R/'docs/tester/D1_E5C_DEVICE_EVIDENCE'
CONT='D1-E5C-CONT-TABLET-20261017'
def package_version(s,app_version):
    sections=s.split('Packages:')
    assert len(sections)>=3
    for part,uid,version in [(sections[1],10221,app_version),(sections[2],10222,0)]:
        assert 'userId='+str(uid) in part
        assert re.search(r'versionCode='+str(version)+r'\b',part)
        assert re.search(r'User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0\b',part)
def current_packages(name,version):
    s=call(name,['shell','set -eu; am get-current-user; dumpsys package com.videokit.app; dumpsys package com.videokit.app.test'])
    assert s.startswith('0\n');package_version(s,version);return s
mode=sys.argv[1]
save(mode+'-stage-attempt.json',dict(stage=mode,continuation=CONT,at=time.time(),oneAttempt=True))
try:
    plan=artifacts()
    if mode=='preflight':
        prior=json.loads((PRIOR/'blocked-result.json').read_bytes())
        assert prior['installCalls']==0 and prior['instrumentationCalls']==0 and prior['clientOwnersReturned']
        assert call('00-continuity-device',['get-state']).strip()=='device'
        current_packages('01-continuity-packages',1)
        s=private('02-original-private');expected(s)
        root='if [ -e files/e5c_guard_fixture_20261017_once ] || [ -L files/e5c_guard_fixture_20261017_once ]; then echo ROOT_ALREADY_EXISTS; exit 42; fi; echo ROOT_ABSENT'
        assert call('03-root',['shell','run-as com.videokit.app sh -c '+shlex.quote(root)]).strip()=='ROOT_ABSENT'
        save('preflight-result.json',dict(status='PASS',reusedEvidence='D1_E5C_DEVICE_EVIDENCE/blocked-result.json',priorAPKHashesNotRepeated=True,originalMetadata='EXACT_ORIGINAL_WRITING_R_PENDING',root='ABSENT',continuation=CONT))
    elif mode=='deploy-fixture':
        assert load('preflight-result.json')['status']=='PASS'
        for i in range(2):assert call('04-install-'+str(i),plan['steps'][i]['argvAfterBoundAdbSerial']).strip().endswith('Success')
        current_packages('05-updated-packages',5)
        s=private('06-after-install-private');expected(s)
        assert core(s)==core((E/'02-original-private-stdout.txt').read_text().replace('\r\n','\n'))
        save('deployment-result.json',dict(status='PASS',versionCode=5,uid=10221,testUid=10222,sameSignerExactHostArtifactInstallSuccess=True,originalStateUnchanged=True))
        call('07-isolated-fixture',plan['steps'][2]['argvAfterBoundAdbSerial'],4*1024*1024)
        save('fixture-client-result.json',dict(status='CLIENT_RETURNED_REQUIRES_INDEPENDENT_REVIEW'))
    elif mode=='query':
        assert load('fixture-independent-admission.json')['admitted'] is True
        call('08-original-query',plan['steps'][3]['argvAfterBoundAdbSerial'])
        s=private('09-final-private');expected(s)
        assert core(s)==core((E/'02-original-private-stdout.txt').read_text().replace('\r\n','\n'))
        save('query-client-result.json',dict(status='CLIENT_RETURNED_REQUIRES_INDEPENDENT_REVIEW',originalStateUnchanged=True))
    else:raise ValueError('UNKNOWN_STAGE')
except BaseException as e:
    save(mode+'-failure.json',dict(status='STOP_DEPENDENCIES',type=type(e).__name__,detail=str(e),productActionsNeverRetry=True));raise
