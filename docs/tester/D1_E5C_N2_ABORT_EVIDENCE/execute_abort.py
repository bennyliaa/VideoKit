"""One formally authorized original N2 ABORT; no query/observe/retry/install/product methods."""
from common import *
CONT=R/'docs/tester/D1_E5C_CONT_EVIDENCE'
META_LIMIT=8
def meta(name,args):
    used=len(list(E.glob('metadata-*-intent.json')))
    assert used<META_LIMIT
    # Append-only intent accounting, even if the original call fails.
    save('metadata-'+str(used+1)+'-intent.json',dict(name=name,limitSeconds=15))
    s=call(name,args)
    assert load(name+'-receipt.json')['elapsedSeconds']<=15,'METADATA_OBSERVATION_DEADLINE'
    return s
POST='''set -eu
printf 'APP_UID|'; id -u
total=0
for p in files/e4a_output_budget/identity.anchor files/e4a_output_budget/ledger.bin files/e4a_output_budget/operation.pending files/e4a_output_budget/operation.pending.N2-e5-aborted files/e4a_output_budget/N2-e5-recovery.complete files/e4a_outputs/TASK.identity files/e4a_outputs/TASK.journal files/e4a_outputs/TASK.lease files/e4a_outputs/TASK.owner files/e4a_output_budget/N2-e5-recovery/identity.before files/e4a_output_budget/N2-e5-recovery/journal.before files/e4a_output_budget/N2-e5-recovery/lease.before files/e4a_output_budget/N2-e5-recovery/ledger.before files/e4a_output_budget/N2-e5-recovery/recovery.owner files/e4a_output_budget/N2-e5-recovery/guard.identity files/e4a_output_budget/N2-e5-recovery/proof.txt; do
 if [ ! -e "$p" ] && [ ! -L "$p" ]; then printf 'ABSENT|%s\n' "$p"; continue; fi
 test -f "$p"; test ! -L "$p"
 n=$(stat -c %s "$p"); test "$n" -le 4096; total=$((total+n)); test "$total" -le 16384
 printf 'STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
 printf 'HEX_BEGIN|%s\n' "$p"; od -An -v -tx1 "$p"; printf 'HEX_END\n'
done
for p in files/e4a_outputs/TASK.mp4 files/e4_fixtures/basic.mp4 files/e4_fixtures/subtitle.avi; do
 test -f "$p"; test ! -L "$p"; printf 'DATA_STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
done
for p in files/e4a_outputs/TASK.e5-journal-1.tmp files/e4a_outputs/TASK.e5-journal-2.tmp; do
 if [ -e "$p" ] || [ -L "$p" ]; then printf 'TEMP_PRESENT|%s\n' "$p"; else printf 'TEMP_ABSENT|%s\n' "$p"; fi
done
printf 'METADATA_READ_BYTES|%s\n' "$total"
'''.replace('TASK',TASK)
mode=sys.argv[1];save(mode+'-stage-attempt.json',dict(stage=mode,at=time.time(),oneAttempt=True))
try:
    plan=artifacts()
    assert sha((R/'docs/coder/d1e5b/evidence/e5b-freeze.json').read_bytes())=='3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee'
    assert sha((R/'docs/tester/D1_E5C_CONT_DEVICE_TEST_REPORT_V1.0.md').read_bytes())=='6e89690066ac47c83d7ac5ce92e1024b7d0a412ab0018d6c882a98a292184720'
    assert sha((CONT/'08-original-query-stdout.txt').read_bytes())=='0ac55263ad5c2f5af073cc6721274d0d8f1195cb241773007ac1cce1c6b9c115'
    if mode in ('preflight','human-preflight'):
        prefix='human-' if mode=='human-preflight' else ''
        s=meta(prefix+'00-package-continuity',['shell','set -eu; am get-current-user; dumpsys package com.videokit.app; dumpsys package com.videokit.app.test'])
        assert s.startswith('0\n')
        assert len(s.split('Packages:')[1:])==2
        for part,uid,version in zip(s.split('Packages:')[1:],[10221,10222],[5,0]):
            assert 'userId='+str(uid) in part and re.search(r'versionCode='+str(version)+r'\b',part)
            assert re.search(r'User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0\b',part)
        # Only the fixed, read-only metadata preflight. No code/APK or media content hash.
        s=meta(prefix+'01-original-private',['shell','run-as com.videokit.app sh -c '+shlex.quote(SCRIPT)])
        expected(s);assert core(s)==core((CONT/'09-final-private-stdout.txt').read_text().replace('\r\n','\n'))
        save(prefix+'preflight-result.json',dict(status='PASS',metadataCalls=2,originalStateMatchesReviewedQuery=True,reusedDeploymentAndSignature=True))
    elif mode=='abort':
        assert load('preflight-result.json')['status']=='PASS'
        assert load('human-preflight-result.json')['status']=='PASS'
        args=list(plan['steps'][3]['argvAfterBoundAdbSerial']);i=args.index('e5N2Action')+1;assert args[i]=='QUERY';args[i]='ABORT_ORIGINAL_N2'
        call('02-original-abort',args)
        save('abort-client-result.json',dict(status='CLIENT_RETURNED_REQUIRES_INDEPENDENT_REVIEW'))
        meta('03-post-abort-private',['shell','run-as com.videokit.app sh -c '+shlex.quote(POST)])
    else:raise ValueError('UNKNOWN_STAGE')
except BaseException as e:
    save(mode+'-failure.json',dict(status='STOP_NO_RETRY_NO_OBSERVATION',type=type(e).__name__,detail=str(e)));raise
