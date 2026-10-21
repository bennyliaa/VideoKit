"""Assemble final source/JAR provenance and review-only plans. No build/test/device execution."""
from pathlib import Path
import hashlib,json,zipfile,re,difflib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=R/'docs/coder/d1e13a';E=B/'evidence';D=B/'artifacts/D1-20261018-E13E/delivery-final';L=B/'release';L.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=sha(raw))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'e13e-freeze.json').exists()
for row in json.loads((E/'final-build-inputs.json').read_text())['files']:assert pin(R/row['path'])==row,row['path']
audit=json.loads((E/'apk-delivery-final/apk-audit.json').read_text());assert audit['status']=='PASS_LOCAL_APK_IDENTITY_AUDIT'
assert "versionCode='2'" in (E/'apk-delivery-final/fixture-badging.txt').read_text(encoding='utf-8-sig')
dexRows=[]
for apk in audit['apks']:
 with zipfile.ZipFile(R/apk['path']) as z:
  raw=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
  for marker in [b'E13EAndroidCheck',b'E13EProtocolCheck',b'CONTROLLED_PLATFORM_KERNEL_DENIAL',b'monitor1.8.0 non-main contract substitute']:assert marker not in raw,(apk['kind'],marker)
  for marker in ([b'E13FinishOwner',b'E13Stages',b'awaitOriginalTermination'] if apk['kind']=='app' else [b'ownerOutcome',b'E13_ORIGINAL_ACK_INTERRUPTED_UNKNOWN'] if apk['kind']=='fixture' else [b'E13Instrumentation',b'originalResult']):assert marker in raw,(apk['kind'],marker)
  dexRows.append({'apk':apk,'productionMarkersVerified':True,'platformSubstitutesExcluded':True})
write(E/'final-dex-wiring-audit.json',{'status':'PASS','rows':dexRows,'deviceCalls':0})
production=[]
for folder in ['src','upstream-c14/src','binding']:production+=sorted((B/folder).rglob('*.java'))
production+=sorted((B/'tools').glob('*.java'));allow={}
for p in production:
 pkg=re.search(r'package\s+([\w.]+);',p.read_text(encoding='utf-8-sig')).group(1);allow[pkg.replace('.','/')+'/'+p.stem]=p
jar=D/'e13e-host-tools.jar';rows=[];classes=B/'.checks/host-006'
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(classes.rglob('*.class')):
  entry=p.relative_to(classes).as_posix();top=entry[:-6].split('$')[0]
  if top not in allow:continue
  raw=p.read_bytes();z.writestr(entry,raw);rows.append(dict(entry=entry,bytes=len(raw),sha256=sha(raw),source=pin(allow[top])))
write(E/'host-jar-manifest.json',{'jar':pin(jar),'compileAttempt':'host-006','classes':rows,'testClassesIncluded':False,'recompiledAfterFinalChecks':False})
# Exact actual PC bytecode tested across55s still used; exact public entry/guard bytecode also retained.
comparisons=[]
for attempt,prefixes in [('host-004',['E9PcSupervisor','E13OperationArchive','E13HostCase']),('host-003',['E13PendingGuard','E13HostActivationSession','E13HostCase','E9HostActivationSession'])]:
 for p in (B/'.checks'/attempt/'com/videokit/spike/e4').glob('*.class'):
  if p.stem.split('$')[0] not in prefixes:continue
  entry='com/videokit/spike/e4/'+p.name;now=classes/entry;assert p.read_bytes()==now.read_bytes(),(attempt,entry)
  comparisons.append(dict(attempt=attempt,entry=entry,sha256=sha(p.read_bytes()),exactFinalJarMember=True))
write(E/'tested-final-class-equivalence.json',{'status':'PASS','members':comparisons,'scope':'Original late55s PC pipeline and actual public negative entry bytecode, not merely matching source names'})
oldManifest=json.loads((A/'evidence/host-jar-manifest.json').read_text());oldJar=R/oldManifest['jar']['path']
with zipfile.ZipFile(oldJar) as z:
 base={n:sha(z.read(n)) for n in z.namelist()}
write(E/'host-member-difference.json',{'baseJar':pin(oldJar),'newJar':pin(jar),'unchangedClassBytes':sum(base.get(x['entry'])==x['sha256'] for x in rows),'newOrChangedClassBytes':sum(base.get(x['entry'])!=x['sha256'] for x in rows)})
derived=[]
for folder in ['src','android','upstream-c14/src','upstream-c14/android','binding','checks/com','app/src','fixture/src','tools']:
 for p in sorted((B/folder).rglob('*')):
  if not p.is_file() or p.suffix not in ['.java','.ps1','.py','.xml']:continue
  old=(R/'docs/coder/d1e13c/tools'/p.name) if p.name in ['E11DeploymentOnce.java','E13HostActivationSession.java'] and folder=='tools' else A/p.relative_to(B)
  before=pin(old) if old.is_file() else None;after=pin(p);same=before and before['sha256']==after['sha256'];derived.append({'current':after,'baseline':before,'relationship':'BYTE_IDENTICAL' if same else 'MODIFIED' if before else 'NEW_E13E'})
  if not same:
   target=E/'diffs'/p.relative_to(B);target=target.with_suffix(target.suffix+'.diff');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True) if old.is_file() else [],p.read_text(encoding='utf-8-sig').splitlines(True),fromfile=before['path'] if before else '/dev/null',tofile=after['path'])),encoding='utf-8')
write(E/'source-derivation.json',{'files':derived,'nativeBuilds':0})
refs=B/'reference';refs.mkdir(exist_ok=True)
for path in [R/'docs/tester/D1_E13D_OFFLINE_REVIEW_REPORT_V1.0.md',R/'docs/tester/D1_E13C_TABLET_EXECUTION_REPORT_V1.0.md',R/'docs/tester/D1_E13C_TABLET_EXECUTION_REPORT_V1.1.md',R/'docs/coder/d1e13d/evidence/cached-dependency-source-excerpts.json',R/'docs/MILESTONE_COORDINATION_V1.0.md',R/'docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md']:
 shutil.copyfile(path,refs/path.name)
plan={'status':'DRAFT_NO_DISPATCH','candidate':'D1-20261018-E13E','appVersion':18,'fixtureVersion':2,'abi':1,'role':'ACTIVATION','hostJar':pin(jar),'targetApks':audit['apks'],'actualScope':None,'actualRelease':None,'actualOnce':None,'sourceReview':None,'dispositionSourcePin':'ABSENT','oldTask':'E13C_LAST_RECORDED_PENDING_NOT_RECHECKED','lostDiagnostic':'LOST_DIAGNOSTIC_OWNER_UNKNOWN_SEPARATE','installedPredecessorVersionHistorical':17,'predecessorIsDeploymentBytesNotTestPass':True,'fixedOnceBasename':'e13e-lifecycle-deployment.once','batch':'D1-E13E-LIFECYCLE-20261018','freshM1AndExactMetadataRequired':True,'metadataArgv':'NOT_YET_AUTHORIZED; must finalize v17/fixture1 -> v18/fixture2 expectations after original disposition','budgetProposal':{'successOperations':51,'deploymentEntry':1,'deploymentChildren':35,'caseJavaEntries':6,'caseInstrumentChildren':6,'directMetadataClients':3,'occupationRechecks':2,'maxOperationsWithOccupation':53,'externalTextBytes':2097152,'successAllocatedText':1638400,'occupationTextReserve':131072,'remainingText':327680,'archiveDiskBytesProposed':3145728,'fixtureInternalReadRpcLimit':2,'fixtureRequestBytes':1024,'fixtureReplyBytes':4096,'originalPriorBalancesInherited':False},'stageBounds':{'eventsPerProcess':48,'lineAsciiChars':500,'totalBytesPerProcess':24576},'archiveBounds':{'rawPerOriginalOperation':'existing original cap','queueBlocks':8,'blockBytes':4096,'fixedRecordBytes':4096,'writeQualificationSeconds':2,'actualWriteMayRemainPending':True},'T07':'NOT_RUN','D1':'NOT_PASSED','M0':'NOT_STARTED'}
write(L/'candidate-binding.json',plan);write(L/'device-plan-draft.json',plan)
write(E/'android-004/results-audit.json',{'status':'COUNT_AUDIT_ONLY_NO_RERUN','actualExecutedProtocolGroups':6,'oldResultsListIncorrectlyIncludedUnexecutedBaseGroups':11,'authority':'commands.json and exit/stdout/stderr; final android-00518 groups are separately real executed','oldReceiptUnchanged':True})
write(E/'final-summary.json',{'status':'READY_FOR_INDEPENDENT_LOCAL_REVIEW','android005Groups':18,'actualAfter007':True,'host006Groups':4,'host004ArchiveAndLate55sGroups':7,'publicNegativeEntries':4,'outerObserverActualRecordingFailure':True,'T07':'NOT_RUN','sdkOrDeviceExecution':0,'nativeBuilds':0,'oldSuitesRerun':0,'apkBuildAttempts':4,'passingApkBuilds':2,'finalApkBuild':'r01-004','firstSuccessRebuiltOnlyForActualR01SourceChange':True,'hostSelfcheckCompileAttempts':6,'finalJarUsesLastActualClasses':True})
# Update four documents to the final selected identity; previous successful artifacts remain explicitly historical.
p=R/'docs/coder/D1_E13E_LIFECYCLE_DELIVERY_V1.0.md';t=p.read_text();t=t.replace('app/test/fixture只有一次成功的集中离线构建 fixed-003（约80秒）。','app/test/fixture前版fixed-003集中离线构建成功（约80秒），最终r01-004因实际R01源码修正再集中构建成功（约26秒）；不是相同源码重建。').replace('修正为checks/com生产目录，同时补强原ACK接线后构建成功；没有成功后机械重建。','修正为checks/com生产目录并补强原ACK后首次成功；最终将E9整段class锁收紧为ACTIVE原子登记，避免日志/平台调用处于owner锁内，旧成功产物与输入保留。').replace('ac530f731cbd31bf8b4fdad74985b7422b4ca88758163953a05759bdb20f731f',pin(E/'final-build-inputs.json')['sha256']).replace('D1-20261018-E13E/delivery/','D1-20261018-E13E/delivery-final/').replace('28cd1f55c84536cc75a8fc9cf7fee74b1a9e2acc22bb19c6f10ee6f2933f178d',audit['apks'][0]['sha256']);p.write_text(t,encoding='utf-8')
p=R/'docs/coder/D1_E13E_SELF_CHECK_REPORT_V1.0.md';t=p.read_text().replace('host-005','host-006').replace('fixed-003修正源码目录和晚ACK后唯一成功集中构建。','fixed-003修正源码目录和晚ACK后首次成功；r01-004再按真实R01源码修正收窄观察锁，最终成功且旧成功版保留。').replace('## 仍未验证','actual-after-007额外直接执行生产E13DeviceTests.@After、真实JUnit4.13.2 TestName/TestWatcher和实际runner：callback未返时原@After失败，经原TestWatcher记录，晚原返后唯一finish仍含失败。CALLBACK_PASS是直接提交成功结果的完成门分支，不能冒称实际@After在资源未返时也通过。\n\n## 仍未验证');p.write_text(t,encoding='utf-8')
print(json.dumps({'status':'PREPARED_FINAL_E13E','jar':pin(jar),'jarClasses':len(rows),'exactTestedClassComparisons':len(comparisons),'apks':audit['apks']}))
