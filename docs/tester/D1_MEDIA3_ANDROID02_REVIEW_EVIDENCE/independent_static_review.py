from pathlib import Path
import json,hashlib,zipfile,re,datetime,difflib
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1media3-android02';OLD=R/'docs/coder/d1media3-android01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
seal=B/'evidence/media3-android02-freeze.json';assert sha(seal)=='36d3d06ca38da726aa5ee1d97c54a7cffd025be1af686d0f991cdd4fb9e796b2';s=load(seal);assert len(s['files'])==len({x['path'] for x in s['files']})==372
report=R/'docs/coder/D1_MEDIA3_ANDROID02_CONTAINER_DELIVERY_V1.0.md';assert sha(report)=='bcfd21251963145c8241bc7a93602a61527f97df7ba87f121973b2cd9bdd3d72'
assetReads=[];checked={}
for x in s['files']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'];actual=sha(p);assert actual==x['sha256'];checked[x['path']]=actual
 if p.suffix.lower()=='.mp4':assetReads.append(dict(actor='INDEPENDENT_FROZEN372_HASH',path=x['path'],logicalBytes=x['bytes']))
archive=R/'docs/coder/D1-20261021-MEDIA3-ANDROID02-CONTAINER-source.zip';assert archive.stat().st_size==s['archive']['bytes'] and sha(archive)==s['archive']['sha256']=='9e613481e0aca6a91a31010a897b41c8e7ce9ee127c7857e65fc1737c2f45bda'
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(set(z.namelist()))==372 and set(z.namelist())==set(checked)
 for x in s['files']:
  assert z.getinfo(x['path']).file_size==x['bytes'] and hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
  if Path(x['path']).suffix.lower()=='.mp4':assetReads.append(dict(actor='INDEPENDENT_ZIP_MEMBER_HASH_AND_CRC_SINGLE_READ',path=x['path'],logicalBytes=x['bytes']))
assert not list((B/'artifacts').glob('*')) and not list((B/'app').rglob('*.apk'))
assert load(B/'evidence/artifact-status.json')['status']=='UNBUILT_GRADLE_DAEMON_CONNECT_FAILED_BEFORE_COMPILE'
build=load(B/'evidence/build-main-001/receipt.json');fail=load(B/'evidence/build-failure-audit.json');assert build['exitCode']==1 and not fail['firstProjectTaskReached'] and not fail['actualStrictResolutionOrCompileObserved'] and fail['daemonOriginalReturn']=='UNKNOWN_NOT_QUERIED_NO_PID_ATTACH_OR_KILL'
log=(B/'evidence/build-main-001/gradle.log').read_text();daemon=(B/'evidence/build-main-001/daemon-35512-preserved.log').read_text();assert 'Could not connect to the Gradle daemon.' in log and 'Completed writing the daemon greeting.' in daemon and '127.0.0.1' in daemon
assert not (B/'evidence/build-main-001/consumption.jsonl').exists()
diffrows=load(B/'evidence/source-differences.json');assert len(diffrows)==9;diffAudit=[]
for row in diffrows:
 p=B/row['path'];assert sha(p)==row['newSha256'];oldrel=row['path'].replace('android02/','android01/');old=OLD/oldrel
 oldtext=old.read_text() if old.exists() else None;text=p.read_text();semanticSame=oldtext==text if oldtext is not None else False
 diffAudit.append(dict(**row,actualBaselinePath=str(old) if old.exists() else None,actualBaselineSha256=sha(old) if old.exists() else None,textSameIgnoringNativeLineEndings=semanticSame,sourceTextDiff=''.join(difflib.unified_diff(oldtext.splitlines(True) if oldtext is not None else [],text.splitlines(True),fromfile=str(oldrel),tofile=row['path']))))
for rel in ['gradle/verification-metadata.xml','app/gradle.lockfile','settings-gradle.lockfile']:assert (B/rel).read_bytes()==(OLD/rel).read_bytes()
deps=[]
for p in sorted((B/'deps').glob('*.jar')):
 assert sha(p)==sha(OLD/'deps'/p.name)
 with zipfile.ZipFile(p) as z:assert not any(n.startswith(('org/jcodec/','com/videokit/fixturetool/')) for n in z.namelist())
 deps.append(dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)))
asset='docs/coder/d1media3-android02/instrumentation-assets/qualified-six-avc.mp4';assert checked[asset]=='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c'
for phase in ['javac','metadata']:
 own=load(B/f'evidence/nonmedia-001/{phase}-owner.json');assert own['exitCode']==0 and own['originalProcessReturned'] and own['captureHandlesClosed'] and own['killInterruptRetry']==0
nonmedia=(B/'evidence/nonmedia-001/metadata.stdout').read_text();assert 'DONE nonMediaChecks=20 originalsReturned=true' in nonmedia and 'DONE independentBoundaryPasses=8' in nonmedia
origins=load(B/'evidence/nonmedia-class-origins.json');assert len(origins)==178
for x in origins:assert sha(B/x['class'])==x['sha256'] and sha(B/x['source'])==x['sourceSha256'] and x['major']==55
assert not any('instrumentation/' in x['source'] for x in origins)
def excerpt(relative,needle,before=1,after=2):
 p=B/relative;lines=p.read_text().splitlines();at=next(n for n,line in enumerate(lines) if needle in line);return dict(path=p.relative_to(R).as_posix(),sha256=sha(p),startLine=max(0,at-before)+1,lines=[dict(line=n+1,text=lines[n]) for n in range(max(0,at-before),min(len(lines),at+after+1))])
job='instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java';runner='instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java';fd='instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java';contract='src/com/videokit/d1android/ExperimentContract.java';q='src/com/videokit/d1android/QualifiedObservation.java'
findings=[
 dict(id='A02-S01',priority='P2',kind='STATIC_SOURCE_AND_FROZEN_MEDIA3_BYTECODE_PROVEN',title='固定raw flags=1与真实Mp4Extractor末样本标记冲突',trigger='任一qualified正路真实Mp4Extractor产出六个样本并进入QualifiedObservation.require',evidence='固定C.BUFFER_FLAG_LAST_SAMPLE=536870912；TrackSampleTable ctor pc116..128对flags[last] OR此位；Mp4Extractor.readSample pc844/849/850取原flags到local16，pc917/923原样送TrackOutput.sampleMetadata。HostMp4Inspection透传flags；q.flags六项全1，require按raw int全等，末样本必不能等1。NOT_DEPENDED_ON等附加位也应依固定库预声明，不凭keybool填原flags。',impact='正常inspectKnown/short/unknown/seek与muxQualified会在该比较门被拒；无设备复现，结论为确定源码/库合同冲突。',recommendation='保留raw真实flags，按固定Media3语义明确KEY/ENCRYPTED/EOS与FIRST/LAST等框架信息的对照；仅向mux传其支持的flag域，仍拒未知/加密/EOS，不可删除关键门或现场任意mask求绿。',sources=[excerpt(contract,'List.of(1340'),excerpt(q,'s.flags!=q.flags'),excerpt('src/com/videokit/d1input/HostMp4Inspection.java','samples.add(new Sample')],bytecodeEvidence='media3-extractor-flags-static-bytecode.json'),
 dict(id='A02-S02',priority='P2',kind='STATIC_ORIGINAL_COMPLETION_POINT_ORDER_PROVEN',title='单调完成时间仍早于最后受控返回事件',trigger='cleanup后完成时间小于60秒，但其后E13ReturnEvents.returned同步回调或线程调度跨过观察界，等待者随后才检查isAlive',evidence='completedNano和workerBodyReturned在E13ReturnEvents.returned之前写；returned同步遍历listener。onStart只在检查时isAlive或该较早timestamp>=界时判UNKNOWN。worker可在事件尾段后终止而timestamp仍及时，违反最后受控语句定义。',impact='可出现尾段迟返未计入body契约的正常分支；这是源码时序反例，未运行时间注入/线程测试。',recommendation='将同原完成标记放到cleanup及所有可延迟的受控返回信号之后，保留实际join/等界迟/先前UNKNOWN sticky；不以事后isAlive或早marker补绿。',sources=[excerpt(job,'completedNano=System.nanoTime()'),excerpt(runner,'if(worker.isAlive()'),excerpt('upstream/com/videokit/spike/e4/E13ReturnEvents.java','public static void returned()')]),
 dict(id='A02-S03',priority='P2',kind='STATIC_NATIVE_ALLOCATION_ADOPTION_FAILURE_PATH',title='Os.open返回的raw FD未在包装前进入原owner',trigger='Os.open已经返回FD，但new FileOutputStream(fd)包装构造随后异常',evidence='createNew将Os.open直接嵌入new FileOutputStream表达式；E4Owned.resource仅action.run整体返回后赋值。该异常窗口无raw FD字段/登记槽/专门closer，保留的外层owner只有nullresource，无法retain该已打开原FD。',impact='异常路径的原nativeFD保管/归还证据缺口；未注入OOM/权限/原生错误，也不据此断言正常Android一定泄漏。FileOutputStream(fd)正常关闭的Android所有权另待准确平台API证据，JDK模拟不代。',recommendation='原nativeFD在Os.open成功后先挂到已登记owner，再包装；明确单一真实关闭者/失败归还与UNKNOWN保管，防二close。恢复包需给Android真实所有权依据和实际close证据，不做资源攻击。',sources=[excerpt(fd,'try{return new FileOutputStream(android.system.Os.open'),excerpt(job,'dest.allocate('),excerpt(fd,'original.allocate(()->createNew(file))'),excerpt('upstream/com/videokit/spike/e4/E4Owned.java','try{resource=action.run()')]),
 dict(id='A02-S04',priority='P2',kind='STATIC_EXECUTION_BUDGET_CONTRACT_GAP_NOT_ACTUAL_OVERRUN',title='单scope十方法预算与Job局部计量及全操作计划未闭合',trigger='将execution-plan的一个futureScopeId/sameScopeBudget用于最多10方法',evidence='plan标sameScopeBudget输入8MiB/输出16MiB，但inputReserved在每new ExperimentJob起0，nativeattempted每OutputCapability起0；三参数无scope剩余额度，计划没有跨方法预扣账。仅methodsMaximum/每方法capture限额，不是含安装/证据/清理的精确operation列表及wholewall。',impact='当前无APK/设备，不是已发生超限；不能据该提案批准整个设备窗口。Job内全phase累计是已有正确部分，不能扩大为十case共享已实现。',recommendation='冻结前统一scope ledger/剩余额度准入，或由负责人明确各独立case scope与外层总额，禁止静默乘N。补全安装/执行/采集/证明/清理逐操作和总wall/进出站预算，保留无APK时UNBOUND。',sources=[excerpt(job,'volatile HostMp4Inspection.Evidence'),excerpt(job,'inputReserved+=bytes'),excerpt(fd,'long bytes,attempted'),excerpt(runner,'ExperimentJob created=new ExperimentJob')],plan='docs/coder/d1media3-android02/evidence/execution-plan.json')]
save('concentrated-static-findings.json',dict(reportClassification='BUILD_BLOCKED_STATIC_ONLY',findings=findings,confirmedByStaticSourceOrLibraryContract=4,executedReproductions=0,platformFailuresAsserted=False,newRecoveryRead=False))
save('independent-static-audit.json',dict(result='BUILD_BLOCKED_STATIC_ONLY',checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reportSha256=sha(report),sealSha256=sha(seal),frozenRows=372,zipUniqueMembers=372,archiveSha256=sha(archive),sourceDifferenceRows=diffAudit,dependenciesUnchanged=deps,strictRequestsNotActualConsumption=True,androidActualArtifacts=0,actualAndroidCases=0,originalGradleClient=build,originalBuildFailureFacts=fail,oldDaemonPhysicalReturn='UNKNOWN_NOT_QUERIED',originalNonmediaParentGroups=20,originalInheritedSubcases=8,nonmediaActualClassFiles=178,nonmediaDoesNotCompileInstrumentation=True,nonmediaRerunsByTester=0,materialEntryReceipt=load(E/'materials-001/material-verification.json'),newJavaOrGradleProcesses=0,actualMediaParsers=0,deviceOperations=0,oldUnknownActions=0,recoveryFloatingSourceRead=False,independentAssetIdentityLogicalReadLedger=assetReads))
print('BUILD_BLOCKED_STATIC_ONLY independent372 ZIP372,9sources reviewed,4concentrated static findings,no Java/Gradle/device')
