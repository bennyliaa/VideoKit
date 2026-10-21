from pathlib import Path
import json,hashlib,uuid,shutil,difflib
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e13j-r1';REVIEW='f9e5a63acf2aea2fc51c9c71ec50ceba5ed080cdded46676cd7fd9cec6374583';SCOPE='116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef'
assert not (B/'release/read-only-release.json').exists(),'ONE_RELEASE_ONLY'
for name in ['release','evidence','reference','artifacts','policy']: (B/name).mkdir(parents=True,exist_ok=True)
review=R/'docs/tester/D1_E13J_R1_FIXED_SOCKET_REVIEW_REPORT_V1.0.md';assert hashlib.sha256(review.read_bytes()).hexdigest()==REVIEW;shutil.copyfile(review,B/'reference'/review.name)
source=OLD/'tools/E13JReadOnly.java';shutil.copyfile(source,B/'reference/E13JReadOnly-reviewed.java');shutil.copyfile(OLD/'tools/observe_j_only.ps1',B/'reference/observe-reviewed.ps1');shutil.copyfile(OLD/'artifacts/e13j-host-tools.jar',B/'reference/r1-reviewed.jar')
release=(json.dumps({'e9':1,'fields':dict(sorted(dict(kind='e13jFixedReadOnlyRelease',scope=SCOPE,serial='HA1Q6WXR',review=REVIEW,budget='262144',requests='2').items()))},separators=(',',':'))+'\n').encode('ascii');(B/'release/read-only-release.json').write_bytes(release);digest=hashlib.sha256(release).hexdigest();batch=str(uuid.uuid4())
scope=dict(batch=batch,originalScope='aeefe32f-816d-4c0b-aca7-16f76dbd45ff',runtimeScopeSha256=SCOPE,serial='HA1Q6WXR',review=REVIEW,releaseSha256=digest,role='ONE_G_READONLY_SUPPLEMENT')
(B/'release/execution-scope.json').write_text(json.dumps(scope,separators=(',',':'))+'\n',encoding='utf-8')
t=source.read_text();assert t.count('APPROVED_REQUEST_SHA="ABSENT"')==1;t=t.replace('APPROVED_REQUEST_SHA="ABSENT"','APPROVED_REQUEST_SHA="'+digest+'"').replace('actualRelease=ABSENT','actualRelease='+digest);(B/'policy/E13JReadOnly.java').write_text(t,encoding='utf-8')
(B/'evidence/release-identity.json').write_text(json.dumps(dict(batch=batch,originalScope=scope['originalScope'],runtimeScopeSha256=SCOPE,review=REVIEW,releaseSha256=digest,releaseBytes=len(release),actualExecution=False),indent=2)+'\n')
(B/'evidence/strategy-source.diff').write_text(''.join(difflib.unified_diff(source.read_text().splitlines(True),t.splitlines(True),fromfile=str(source),tofile=str(B/'policy/E13JReadOnly.java'))),encoding='utf-8')
print('Prepared unique execution batch',batch,'typed release',digest,'bytes',len(release))
