"""Final reproducible E9A source/build/targeted evidence/binary/doc consistency; no new device execution."""
import csv,hashlib,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent));import e9a_package as p
B=p.B;R=p.R;p.verify_inputs();p.checks()
checks=p.read(B/'evidence/targeted-check-results.json');assert checks['groups']==19 and checks['finalValidationInvocations']==21 and checks['assertions']==279
with (B/'evidence/test-mapping.csv').open(encoding='utf-8-sig',newline='') as f:mapping=list(csv.DictReader(f))
assert len(mapping)==19 and sum(int(x['assertions']) for x in mapping)==279
audit=p.read(B/'evidence/apk-audit.json');assert len(audit['apks'])==2 and len(audit['nativeLibraries'])==7
for apk in audit['apks']:p.check(dict(path=apk['path'],bytes=apk['bytes'],sha256=apk['sha256']))
host=p.read(B/'evidence/host-binary-provenance.json');p.check(host['artifact']);assert not host['testClassesIncluded'] and len(host['productionClasses'])==155
assert 'com/videokit/spike/e4/E9PcSupervisor.class' in host['unchangedLifetimeAndSharedClassBytes']
for document in p.DOCS:assert '2026-10-18' in document.read_text(encoding='utf-8')
for suffix in ['DELIVERY','DEVICE_EXECUTION_APPENDIX']:
 text=(R/f'docs/coder/D1_E9A_{suffix}_V1.0.md').read_text(encoding='utf-8')
 for apk in audit['apks']:assert apk['sha256'] in text and str(apk['bytes']) in text
 assert host['artifact']['sha256'] in text
rules=[
('tools/E9HostManager.java','nonWaitingLaunch','F01 actual non-wait helper used by launch'),
('tools/E9HostManager.java','checkTransport(broadcastFrame(raw)','F03 semantic frame validation is in original decoder'),
('tools/E9HostManager.java','commands.controlResponse','F03 same five-second response task'),
('tools/E9HostManager.java','closeIngressAndSupervise','F02 every console and initialization end'),
('tools/E9HostManager.java','E9_READONLY_NO_RESERVE','F01 readonly narrower PC mode'),
('tools/E9PcSupervisor.java','CONTROL_NS=5_000_000_000L','F03 exact control budget'),
('tools/E9PcSupervisor.java','LIVE.put(handle,this)','F02 original strong custody root'),
('tools/E9PcSupervisor.java','custodian.setDaemon(false)','F02 persistent original JVM'),
('tools/E9PcSupervisor.java','pcIsolationAck','F02 actual in-process takeover acknowledgment'),
('tools/E9PcSupervisor.java','startReturned&&starterReturned','F02 cannot infer process return from reader'),
('tools/E9PcSupervisor.java','cleanupPin','F02 original configuration scope for cleanup'),
('tools/E9HostActivationSession.java','finally{System.err.println(new String(processes.closeSession()','F02 deployment entry exit path'),
('src/com/videokit/spike/e4/E9CurrentObservation.java','final long observationEpoch=E5AAdmission.beginCurrentObservation()','F04 revoke before serial lock/early rejection'),
('src/com/videokit/spike/e4/E5AAdmission.java','epoch!=observationEpoch','F04 old in-flight publication blocked'),
('src/com/videokit/spike/e4/E5AAdmission.java','static synchronized void requireCurrent','F04 atomic admission check'),
('android/com/videokit/spike/e4/E9Runtime.java','E5AAdmission.invalidateCurrent();try','F04 exception before context/authority also revokes'),
('app/src/androidTest/java/com/videokit/spike/e4/E9MigrationInstrumentation.java','original.observeStatus(handle,seq)','F01 actual guarded receiver status'),
('src/com/videokit/spike/e4/E9Registry.java','E9_ONCE_CONTROL_NO_REPLAY','F01/F03 no second EXECUTE or ACK'),
]
integration=[]
for name,marker,scope in rules:
 file=B/name;assert marker in file.read_text(encoding='utf-8-sig'),name;integration.append(dict(file=p.row(file),marker=marker,scope=scope,verification='SOURCE_INTEGRATION plus separately enumerated actual-object checks; not Android execution'))
runner=(B/'app/src/androidTest/java/com/videokit/spike/e4/E9MigrationInstrumentation.java').read_text();assert 'sendStatus(' not in runner and 'android.permission.DUMP' in runner and 'D1-E9A-PREPARE-TABLET-20261018' in runner
manager=(B/'tools/E9HostManager.java').read_text();assert '"-w"' not in manager and 'new Managed(n,request,remote,mode)' in manager
for name in ['E9PcSupervisor.java','E9HostDeployment.java','E9HostManager.java','E9HostActivationSession.java','E9PcClient.java']:
 text=(B/'tools'/name).read_text();assert '.destroy(' not in text and '.destroyForcibly(' not in text and '.cancel(' not in text and 'setDaemon(true)' not in text,name
policy=(B/'src/com/videokit/spike/e4/E9BuildPolicy.java').read_text();assert 'ROLE="PREPARE"' in policy and 'CATALOG_SHA="ABSENT"' in policy and 'CATALOG_BASE64="ABSENT"' in policy
build=p.read(B/'evidence/build-results.json');assert len(build['attempts'])==1 and build['attempts'][0]['exitCode']==0
for baseline in p.read(B/'evidence/external-readonly-verification.json')['baselines']:
 p.check(baseline['seal'])
 for x in p.read(R/baseline['seal']['path'])['immutableFiles']:p.check(x)
public=p.read(B/'evidence/public-android-entry-check.json');assert public['publicEntries']==6 and public['runtimeGrantInvalidationSequence']==1
p.write(B/'evidence/final-static-review.json',dict(schema=1,status='PASS',integration=integration,targetedGroups=19,assertions=279,finalValidationInvocations=21,originalBuildAttempts=1,APKBytesVerified=True,sourceInputsVerified=True,hostBinaryClasses=155,oldE9ImmutableVerified=1045,baselineTotalImmutableVerified=1287,actualAndroid='NOT_RUN',actualMigration='NOT_RUN',activation='NOT_BUILT',actualHActor='NOT_CREATED',d1='NOT_PASSED',m0='NOT_STARTED',longTermAdmission='OPEN',independentTesterReview='PENDING'))
print('PASS E9A final consistency; independent review/device/long-term gates still open')
