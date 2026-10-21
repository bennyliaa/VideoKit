"""Deterministic final package consistency and explicit integration evidence, without any re-execution."""
import csv,hashlib,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent));import e9_package as p
B=p.B;R=p.R
p.verify_inputs();p.checks()
checks=p.read(B/'evidence/local-check-results.json');assert checks['groups']==32 and checks['assertions']==2027 and checks['processInvocations']==38
with (B/'evidence/test-mapping.csv').open(encoding='utf-8-sig',newline='') as f:table=list(csv.DictReader(f))
assert len(table)==32 and sum(int(r['assertions']) for r in table)==2027
audit=p.read(B/'evidence/apk-audit.json')
for apk in audit['apks']:p.check(dict(path=apk['path'],bytes=apk['bytes'],sha256=apk['sha256']))
for document in p.DOCS:
 text=document.read_text(encoding='utf-8');assert '2026-10-18' in text and ('未过' in text or '非正式交付' in text or '未启动' in text or '未执行' in text)
for doc in ['DELIVERY','DEVICE_EXECUTION_APPENDIX']:
 text=(R/f'docs/coder/D1_E9_{doc}_V1.0.md').read_text(encoding='utf-8')
 for apk in audit['apks']:assert apk['sha256'] in text and str(apk['bytes']) in text
policy=(B/'src/com/videokit/spike/e4/E9BuildPolicy.java').read_text();assert 'ROLE="PREPARE"' in policy and 'CATALOG_SHA="ABSENT"' in policy and 'CATALOG_BASE64="ABSENT"' in policy
integration=[
('android/com/videokit/spike/e4/E4Session.java','this(e9CheckedContext(context)','public host constructor delegates through phase before instance fields'),
('upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java','this(e9CheckedContext(context)','public CPU constructor delegates through phase before instance fields'),
('android/com/videokit/spike/c14/E4CpuAdapter.java','E9Phase.requireProduct()','source constructor/next/validate'),
('src/com/videokit/spike/e4/E4FencedTask.java','E9Phase.requireProduct()','initialize'),
('src/com/videokit/spike/e4/E4OutputBudget.java','E5AAdmission.require(directory,identity)','reserve delegates to phase/current proof'),
('android/com/videokit/spike/e4/E4CodecService.java','code==E4CodecWire.BEGIN||code==E4CodecWire.DEBUG','codec BEGIN/debug protected in rejection-cleanup try'),
('upstream-c14/android/com/videokit/spike/c14/CpuIsolatedService.java','E9Phase.requireObservationRole()','CPU START/SELF_SEGV/RESUME/RELEASE_STOP_STALL'),
('android/com/videokit/spike/e4/E4Encoder.java','E9Phase.requireObservationRole()','codec create'),
('src/com/videokit/spike/e4/E5AFinalObservation.java','E9_LEGACY_OBSERVER_ENTRY_DISABLED','old reader disabled'),
('src/com/videokit/spike/e4/E5N2Recovery.java','E9Phase.rejectLegacyRecovery()','old recovery disabled'),
('android/com/videokit/spike/e4/E5N2RecoveryAndroid.java','E9Phase.rejectLegacyRecovery()','old Android recovery public constructor disabled'),
('app/src/androidTest/java/com/videokit/spike/e4/E7AReadOnlyInstrumentation.java','E9Phase.rejectLegacyRecovery()','legacy debug onCreate disabled'),
('app/src/androidTest/java/com/videokit/spike/e4/E4DeviceTests.java','E9Runtime.observe(context())','future normal tests require current observer'),
('src/com/videokit/spike/e4/E9Phase.java','!E9BuildPolicy.role().equals("PREPARE")','activation rejects writable migration'),
]
items=[]
for path,marker,scope in integration:
 file=B/path;assert marker in file.read_text(encoding='utf-8'),path;items.append(dict(file=p.row(file),marker=marker,scope=scope,verification='SOURCE_INTEGRATION_ONLY unless included in direct public-entry check'))
assert len(audit['nativeLibraries'])==7 and p.read(B/'evidence/sbom-difference.json')['coordinates']==35
for baseline in p.read(B/'evidence/external-readonly-verification.json')['baselines']:
 p.check(baseline['seal'])
 for row in p.read(R/baseline['seal']['path'])['immutableFiles']:p.check(row)
p.write(B/'evidence/final-static-review.json',dict(schema=1,status='PASS',integration=items,groups=32,finalMappedAssertions=2027,finiteLocalValidationProcesses=38,androidHostStubEntries=6,sourceInputsVerified=True,APKBytesVerified=True,baselineImmutableItems=242,actualAndroid='NOT_RUN',actualMigration='NOT_RUN',activation='NOT_BUILT',realHActor='NOT_CREATED',d1='NOT_PASSED',m0='NOT_STARTED',longTermAdmission='OPEN',notIndependentTesterReview=True))
print('PASS final input/APK/docs/mapping/integration/baseline consistency; independent review and device gates remain open')
