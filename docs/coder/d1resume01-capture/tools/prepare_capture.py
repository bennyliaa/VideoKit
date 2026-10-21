"""Prepare one new offline-only capture binding, not a device permit or new product candidate."""
from pathlib import Path
import json,hashlib,shutil,uuid
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1resume01-release'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (B/'release/capture-policy.json').exists()
report=R/'docs/tester/D1_RESUME01_RELEASE_EXECUTION_REPORT_V1.0.md';assert pin(report)['sha256']=='d86433cb2b1421ae8e0c8c583fb3a7693b48ff18c5d5d0adb08dfb0c22c98d6d'
oldSeal=OLD/'evidence/release-freeze.json';assert pin(oldSeal)['sha256']=='b7537e7dd4934c248f727064a103c1fbfc099d0e7a28cce55b28a777df7fd461'
for row in json.loads(oldSeal.read_text())['immutableFiles']:
 p=R/row['path'];assert pin(p)==row,row['path']
for p in [report,OLD/'release/metadata-requests.json',OLD/'release/exact-budget.json',OLD/'tools/observe_original.ps1',OLD/'reference/recorded-standard-client-capture-command.txt',oldSeal]:
 q=B/'reference'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
metadata=json.loads((OLD/'release/metadata-requests.json').read_text());write(B/'reference/frozen-metadata-argv.json',dict(commands=[dict(argv=r['argv']) for r in metadata['commands']],scope='Original exact five argv; no -H/-P rewrite.'))
planId=str(uuid.uuid4());plan=dict(kind='RESUME01_CAPTURE_PREPARATION_ONLY',planId=planId,basis=pin(report),sourceReleaseSeal=pin(oldSeal),deviceAuthorization='NOT_ISSUED_BY_CAPTURE_BATCH')
write(B/'release/preparation-plan.json',plan);scope=pin(B/'release/preparation-plan.json')['sha256'];root=R/'docs/tester/D1_RESUME01_CAPTURE_EXECUTION'/planId/'outputs'
slots=[dict(id='RESUME01_CAPTURE_'+r['id'].replace('RESUME01_RELEASE_',''),phase='M1' if i<3 else 'M2',argv=r['argv'],maxTextBytes=r['maxTextBytes'],qualificationSeconds=15) for i,r in enumerate(metadata['commands'])]
policy=dict(schema='RESUME01_CAPTURE_POLICY_V1',mode='PREPARATION_ONLY',planId=planId,scope=scope,evidenceRoot=str(root),slots=slots,entrySha256=pin(B/'tools/capture_metadata.ps1')['sha256'],toolSha256='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f',fixtureScriptSha256=pin(B/'selfchecks/capture_fixture.py')['sha256'],executionAuthorization=None,independentCaptureReview=None,releaseBindingDigest=None,executionPins=[],fixtureFault='NONE')
write(B/'release/capture-policy.json',policy);policyPin=pin(B/'release/capture-policy.json')
for slot in slots:write(B/'release/requests'/(slot['id']+'.json'),dict(schema='RESUME01_CAPTURE_REQUEST_V1',id=slot['id'],policySha256=policyPin['sha256'],scope=scope,evidenceRoot=str(root),argv=slot['argv'],maxTextBytes=slot['maxTextBytes'],qualificationSeconds=15))
write(B/'evidence/prepared.json',dict(status='OFFLINE_ONLY_NO_DEVICE_PERMIT',preparationPlan=pin(B/'release/preparation-plan.json'),policy=policyPin,entry=pin(B/'tools/capture_metadata.ps1'),productionSourcesChanged=0,productionClassesChanged=0,androidBuilds=0,sdkCalls=0,liveRootQueries=0,oldUnknownConsoleSlot=dict(state='UNKNOWN_HELD',bytesReserved=8192,refunded=False),oldUnallocated=dict(bytes=409600,usable=False),oldReleaseUnmodified=True))
print(json.dumps(dict(status='CAPTURE_PREPARED_NO_EXECUTION',planId=planId,policy=policyPin)))
