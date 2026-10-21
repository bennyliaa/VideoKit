from pathlib import Path
import ast,datetime,hashlib,json,struct,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';A=B/'artifacts';O=R/'docs/coder/d1media3-android02-recovery01'
assert not (E/'fix02-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
audit=json.loads((E/'artifact-audit.json').read_text());origins=json.loads((E/'class-origins.json').read_text());sign=json.loads((E/'signatures-001/result.json').read_text());typed=json.loads((E/'typed-001/result.json').read_text());assert typed['typedCases']==36 and typed['wholeWindowReturnedWithin30s'] and sign['allInputsUnchanged']
counts={'production':sum('instrumentation-' not in x['jar'] for x in origins),'instrumentation':sum('instrumentation-' in x['jar'] for x in origins)};assert sum(counts.values())==105
parser=R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py';tree=ast.parse(parser.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','dexclasses']];exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen_pure_dex_parser','exec'))
mapping=[]
for ap in audit['apks']:
 with zipfile.ZipFile(B/ap['path']) as z:classes={c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))}
 test=ap['package'].endswith('.test');items=[x for x in origins if ('instrumentation-' in x['jar'])==test];assert all('L'+x['className']+';' in classes for x in items);mapping.append({'apk':ap['path'],'actualSourceClassDefinitionsInDex':len(items),'allPresent':True})
for p in A.glob('*.jar'):
 with zipfile.ZipFile(p) as z:
  for n in z.namelist():assert not any(x in z.read(n) for x in [b'android/media/MediaCodec',b'android/media/MediaExtractor',b'android/media/AudioTrack',b'android/view/Surface',b'killProcess',b'startActivity',b'setStreamVolume'])
dump(E/'source-class-dex-consumption.json',{'mapping':mapping,'classCounts':counts,'noForbiddenOwnPlatformCallReferences':True})
tested={x['path']:x for x in json.loads((E/'typed-001/source-pins.json').read_text())};comparisons=[]
for x in origins:
 if not x['source'].startswith('src/com/videokit/d1android/'):continue
 t=E/'typed-001/classes'/x['entry'];assert t.exists();comparisons.append({'className':x['className'],'source':x['source'],'typedSourceSha256':tested[x['source']]['sha256'],'finalSourceSha256':x['sourceSha256'],'typedClassSha256':sha(t),'finalClassSha256':x['sha256'],'byteIdentical':sha(t)==x['sha256']})
dump(E/'typed-versus-final-policy-classes.json',{'comparisons':comparisons,'exactClassBytes':sum(x['byteIdentical'] for x in comparisons),'total':len(comparisons),'metadataOnlySourceDelta':'post-typed-metadata-only-differences.json; no second state/typed JVM, guards unchanged','notClaimingAndroidOrDEXRuntime':True})
preserve=[]
for rel,expected in [('docs/coder/d1media3-android02-recovery01/evidence/recovery01-freeze.json','f58ff8acfea8d05a75af6dc46f80307afac3d5d9d12ed175dc838fc976786937'),('docs/coder/d1media3-android02/evidence/media3-android02-freeze.json','36d3d06ca38da726aa5ee1d97c54a7cffd025be1af686d0f991cdd4fb9e796b2'),('docs/coder/d1media3-android01/evidence/media3-android01-freeze.json','fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a'),('docs/coder/d1media3-container02/evidence/media3-container02-freeze.json','0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d'),('docs/coder/d1jcodec-observation01/evidence/observation01-freeze.json','8a62ef8e4fcea016870daccfe92097903cde667e4d624892309e6984d44e0725')]:
 p=R/rel;assert sha(p)==expected;rows=json.loads(p.read_text())['files'];assert all(sha(R/x['path'])==x['sha256'] for x in rows);preserve.append({'seal':pin(p),'verifiedRows':len(rows)})
for rel,expected in [('docs/tester/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_REVIEW_EVIDENCE/review-evidence-manifest.json','51b9181446d747bc3030cb2c13ce3d8fa1f1d5c9089267418a3f40f122bee8fa'),('docs/tester/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION03/review-evidence-manifest.json','a814ac8e2b2dc5c38189a1a582ee161646cefe1a4a1f43bae863a50aad9e0926'),('docs/tester/D1_MEDIA3_ANDROID02_CONTAINER_PHASE_A_EVIDENCE/phase-a-evidence-manifest.json','82a2f7942023d16a7cf98a4e5c24be052e2d8ebf946b401ab63742bd2724a02c')]:
 p=R/rel;m=json.loads(p.read_text());assert sha(R/m['report'])==expected and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles']);preserve.append({'manifest':pin(p),'report':pin(R/m['report']),'verifiedRows':len(m['evidenceFiles'])})
dump(E/'all-baseline-preservation.json',preserve)
rawApi={'source':'https://developer.android.com/reference/android/system/Os','accessedLocalDate':'2026-10-21','relevantEntries':['open(String,int,int)','close(FileDescriptor)','fsync(FileDescriptor)','write(FileDescriptor,byte[],int,int)'],'use':'Public API signatures checked against official Android reference and actual android-36.1 SDK typecheck. Existing fixed SDK/runtime dependency/license boundary retained.','ownershipChoice':'No FileOutputStream(fd) alias after open. RawWrite OutputStream object/OriginalOwner/Descriptor slot registered in original Job BEFORE Os.open. Returned original FileDescriptor is adopted before later operations; sole original close authority Os.close.','conservativeLimits':'Native throws/uncertain allocation/close remain UNKNOWN. No claims of EINTR recovery, internal platform FD count, Android Os execution or kernel-close behavior proven. No OOM/platform crash injected.'}
dump(B/'reference/android-raw-fd-api-contract.json',rawApi)
fixes=[{'id':'R01-B01','implementation':'ScopeJournal immutable strings/same-lock snapshots; requested scope identity always emitted with complete existing history/completed count/current partial/currentIOPhase/firstFailure. Worker alone builds full JSON; observer never walks mutable parser/case collections. Content196608 reserves status262144/whole emission1048576; overflow blocks explicitly and preserves earlier history. Runner no bare last-json fallback.','typedEvidence':'typed-001 journal6 cases: pending/failure/history/immutable list/concurrent publication/limit no drop+global emission','remaining':'Android JSONObject/platform pending/finish integration NOT_RUN; final source type/DEX verified'},
 {'id':'R01-B02','implementation':'Same ScopeMeter SDK readAt requested/native attempted/native actual/EOF/unknown and copy/controlled/output by case+COPY/HASH/PARSE/SEEK/REOPEN prefix. All scope reservations before calls, input8MiB/output request and attempt16MiB, no resets/refunds. Short3 mature Reader admits SDK requests max4, original native cap3 => real4/3/actual separately; mature internal request length is not called observed SDK readAt count. Native FD slots register before open/adopt/close; known registered peak separate asset stream and source lease peak.','typedEvidence':'typed-001 meter8 cases incl atomic cross-case budget,4/3/1,EOF,unknown,short write and FD/source distinction','remaining':'AssetManager/internal platform total FD peak API_UNPROVEN; actual Android phase counts/FD peaks NOT_RUN'},
 {'id':'R01-B03','implementation':'CompletionPoint.finishAfterSignal runs synchronous E13ReturnEvents and error recording BEFORE marker/body flag. Same original worker; strict elapsed>=0 && <60s, actual join and finalizer/outer finish separate. No controlled callbacks after marker.','typedEvidence':'typed-001 7 callback/clock cases incl actual E13 listener gate,59.9 timely/60 equality late/60.1 late,late observer and failure handler before marker','remaining':'Typed clock stimuli/real controlled threads; not actual60s Android deadline reproduction'},
 {'id':'R01-B04','implementation':'Pre-open Job rawWriters and OriginalOwner<FileDescriptor>, holder itself is unbuffered OutputStream created before open. No post-open platform stream wrapper/alias. Same Os.write/fsync/Os.close exact owner, one close admission; allocation/close unknown blocks return, no replacement/second close. Read RAF owners before constructor plus failed-open unclaimed keeper cleanup.','typedEvidence':'typed-001 raw6 owner cases pending/allocation/init/close unknown and same original close+thread join; full Android source types compile','remaining':'Actual Android Os/close behavior/API uncertainty not upgraded by typed ports; full platform FD cardinality UNPROVEN'},
 {'id':'R01-B05','implementation':'Original Job muxerBinding before mature constructor. OriginalOwner<FragmentedMp4Muxer> records allocation intent/object/calls/EOS/close. MatureContainerRemux requires registered binding, legacy unowned entry rejects. Existing six payload/EOS intent split from one original close to observe independent stages. Cleanup closes original once, UNKNOWN retained with Sink/FD; resourcesReturned includes muxer.','typedEvidence':'typed-001 muxer6 owner plus ADD_TRACK/SAMPLE/EMPTY_EOS3 stage cases; Sink return cannot stand for muxer return','remaining':'Real Media3 construction/addTrack/sample/EOS/close and positive fMP4 chain Android NOT_RUN'}]
dump(E/'five-fix-completion-matrix.json',{'independentBaselineReportSha256':'51b9181446d747bc3030cb2c13ce3d8fa1f1d5c9089267418a3f40f122bee8fa','coderStatus':'IMPLEMENTED_COMPILED_TYPED_LIMITED_EVIDENCE_PENDING_INDEPENDENT_B','actualAndroidReproductions':0,'fixes':fixes})
app,test=[B/x['path'] for x in audit['apks']];binary=app.stat().st_size+test.stat().st_size
oldplan=json.loads((O/'evidence/execution-plan.json').read_text());plan=oldplan;plan['status']='FIX02_BUILT_OFFLINE_PENDING_WHOLE_INDEPENDENT_REVIEW_NOT_DEVICE_AUTHORITY';plan['version']='D1-MEDIA3-ANDROID02-FIX02';plan['apks']=[pin(app),pin(test)];plan['scopeId']=plan['serial']=plan['freshIdleGate']=plan['captureToolIdentity']=None;plan['admissionPrerequisites']=['complete independent FIX02 B across all five and whole scopeAll','new coordinator-bound scope/device/fresh idle/transport capture contract','no old scope reuse/force-stop; all prior UNKNOWN unchanged'];plan['stopRules']=[x for x in plan['stopRules'] if 'partial case snapshot export gap' not in x];plan['stopRules'].append('immutable partial/failure history always reported; content or output budget blocks explicitly, no reexecution or silent history drop')
plan['wholeScopeSdkBudgets']={'sdkReadAtRequestedPlusCopyControlDirectEof':8388608,'nativeAttemptedSeparateBoundedBySameAdmittedReads':8388608,'outputRequestedAndAttemptedEachAllCasesNoRefund':16777216,'block':65536,'short3SdkReadRequestMax':4,'short3NativeReadMax':3,'sample':262144,'sources':2,'perSourceInFlight':1,'queue':0,'singleWholeScopeBodyDeadlineMs':60000,'caseRowsMaximum':128,'descriptorHistoryMaximum':128,'journalContentUtf8':196608,'receiptPerEmissionUtf8':262144,'allReceiptEmissionAttemptedUtf8':1048576,'actualAndroidNativeFdPeak':'NOT_RUN; registered known FD peak separate from asset internals UNPROVEN'}
plan['futureOperationBudget']['binaryOutboundBytesExact']=binary;plan['futureOperationBudget']['logicalOutboundPayloadUpperBound']=binary+24576;plan['futureOperationBudget']['outerWholeWallObservationSeconds']=90;plan['futureOperationBudget']['outerObservationTimeout']='No kill/second close/forced capture shutdown. Stop new operations, retain same SDK worker/FD/finisher and original outer pipes; no success on deadline. Cleanup only new owned files after original returns and separate authorization; no automatic uninstall/clear/retry.'
dump(E/'execution-plan.json',plan)
contract=json.loads((O/'evidence/comparison-and-lifecycle-contract.json').read_text());contract['knownObservationGaps']=['Independent D1/P0/J11/isolation/platform gates unchanged; five source blockers addressed only pending B'];contract['budget']='One ScopeMeter across all cases; SDK readAt request/native attempted/native actual separately. Short3 request4/native3; SDK+copy/control/directEOF gate8MiB; outputs include copy native writes, controlled4, mux/partial/unknown up to16MiB request and attempt independently.';contract['deadline']='Last controlled point AFTER synchronous E13 return signal/error handling; same worker actual join and external platform finish separate.';contract['rawFd']='Pre-open keeper is unbuffered OutputStream; zero post-open FileOutputStream aliases; original Os.close once, close UNKNOWN retained.';contract['muxer']='Pre-registered Job binding/allocation intent and original object; EOS/close facts separate; unknown retains Sink/FD and blocks finish.';dump(E/'comparison-and-lifecycle-contract.json',contract)
oracles=json.loads((B/'reference/android02-stage-a/independent-m2a01-m2a48-oracles.json').read_text())['cases'];assert len(oracles)==48;matrix=[]
for x in oracles:
 matrix.append({'id':x['id'],'area':x['area'],'originalOracleStatus':x['status'],'originalOracle':x['oracle'],'coderEvidence':'SEE_FIVE_FIX_TYPED_MATRIX_AND_ACTUAL_ARTIFACTS','actualAndroidRun':False,'independentVerdict':'PENDING_FIX02_B','platformDtsFdFinishIsolation':'UNPROVEN_OR_NOT_RUN_NOT_FILLED'})
dump(E/'m2a01-m2a48-completion-matrix.json',matrix)
sbom=json.loads((B/'reference/android01-sbom.cdx.json').read_text());sbom['metadata']['component']['name']='VideoKit D1 MEDIA3_ANDROID02_FIX02 empty experiment';sbom['metadata']['component']['version']='D1-MEDIA3-ANDROID02-FIX02';dump(B/'media3-android02-fix02-sbom.cdx.json',sbom)
dump(E/'dependency-license-difference.json',{'newCoordinatesOrVersions':[],'actualArtifacts':300,'actualClosures':[12,17,12,0],'allActualIdentitiesSameAsFrozenAndroid01':True,'originalLocksVerificationByteIdentical':True,'sourceBinaryMetadataRights':'Inherited frozen source-admission/official metadata/Apache2 closure; no new runtime library, no JCodec/fork in APK; no final commercial/patent admission','OsAPI':'Official built-in API reference and existing SDK signatures only; original platform license boundaries retained','fixture':'Exact synthetic8849/hash19e815...778a9c HOST_CONTAINER reference plus original BBB attribution observation-only; no regeneration'})
dump(E/'config-version-difference.json',{'file':'app/build.gradle.kts','oldSha256':sha(O/'app/build.gradle.kts'),'newSha256':sha(B/'app/build.gradle.kts'),'change':'Only versionName RECOVERY01 -> FIX02; no version/lock/dependency policy change'})
report=f'''# D1_MEDIA3_ANDROID02_FIX02 完整五项集中交付 V1.0

2026-10-21。**BUILT_OFFLINE_FIVE_FIXES_IMPLEMENTED_TYPED36_PENDING_INDEPENDENT_B**。R01-B01–B05已集中实现，实际全源类型检查、36项typed非媒体状态/顺序测试和一次离线strict app/test构建已完成，双APK真实验签及源-class-JAR-DEX/300实际消费已核。此为coder有限自检/实现交付，**不自行关闭独立五项，不签Android功能/设备就绪/隔离格式/READY COMMIT/播放**。原报告51b91814...bee8fa为五项静态P2、Android复现0的结论保持；D1未过M0未启。

## 1. 新候选与全部五项

独立目录D:/CodexProjects/VideoKit/docs/coder/d1media3-android02-fix02及fix02-gradle-home；基于冻结recovery01准确源/镜像/许可。原seal/旧cache registry/媒体/encoder/产品App不改；旧35512/48945/17257 UNKNOWN无查询/attach/处置。一次全scopeAll十case功能簇仍在同一原Job/worker运行：preopenAdmission/rejectFixture/cancelLateRead/writerPending/inspectKnown/Short3/Unknown/Seek1s/bbbObserve/muxQualified。真实捕获6→原MatureMuxer→Sink→原writer/FD/任务返回→同grant fMP4重开全链未删，Media3 1.9.3/原17版本/flags政策保持，无JCodec或新框架。

**B01**：ScopeJournal保存已编码不可变case字符串，同锁发布/快照；观察者只读immutable completed/current和同步meter/owner快照，不遍历worker正写JSONObject/parser集合。回执不依赖易变current method判断批次，始终用requested scope身份输出已有history、完成数、失败当前case/currentIOPhase/partial/firstFailure及原owner门；不重跑补历史。content196608B预留状态262144B/全scope emission1048576B，超界明确BLOCKED并保既有history；runner删除“仅最后裸JSON”降级。worker当前实际sample不完整时不编造中间parser结果。

**B02**：同ScopeMeter逐case+COPY/HASH/PARSE/SEEK/REOPEN/CONTROLLED记SDK readAt requested、native attempted/actual/EOF/unknown，copy/controlled单独；所有预留在同原调用前、全case累计。SDK+copy/control/directEOF请求门8MiB，native计量独立但由已准入请求覆盖；output SDK请求与native attempt各16MiB，无partial/unknown退款，含私有copy写及controlled写4，不换factory清零。short3预声明真实mature Reader请求上限4、原native chunk3，记录实际4/3/返回数，不从readCalls猜，库内部更上层请求长度不冒此readAt观测。原FD slot在open前登记、成功adopt和同close单独记；known registered native FD peak、asset-stream owner peak和source lease peak分开，AssetManager/全平台内部FD数API_UNPROVEN，不假称source0即nativeFD0。

**B03**：CompletionPoint把同步E13ReturnEvents.returned及其异常记录都放最后marker之前；marker/body flag后无受控资源回调。严格单调差>=0且<60000000000ns，等号/真正迟返不升级，准时完成晚观察仍准时；同原worker实际join、runner finisher owner及platform finish/外capture另列。marker不是OS退出。

**B04**：RawWrite这个unbuffered OutputStream/OriginalOwner<FileDescriptor>/计量slot均在Os.open前登记到原Job。**没有打开后FileOutputStream(fd)平台包装/别名窗口**；原FD返回后先被原holder采用，后续Os.write/flush/fsync/close一直同对象，唯一原close准入，错误/close UNKNOWN强保管并阻止resourcesReturned。包装对象本身在open前构造，无post-open平台流close所有权假设。读RAF也先注册OriginalOwner，open后未成功交桥的原对象由同keeper清理，不用替代句柄冒close。公开API依据见[Android Os reference](https://developer.android.com/reference/android/system/Os)及reference/android-raw-fd-api-contract.json；这里只核API类型与保守调用合同，实际Android close/内核错误行为未运行，未知不重试。

**B05**：Job.muxerBinding元数据keeper先登记，再允许原MatureMuxer构造；OriginalOwner强持有分配意图及成功返回真实对象，addTrack/sample/EMPTY_EOS/close各原调用状态/首错独立。原六payload/空EOS意图未变，仅把EOS与原close拆为可分别观测的两步；原close最多一次。错误时仍清同原对象；构造不明/close抛错或未返均保留UNKNOWN，阻止原Sink/FD被当成muxer已返，resourcesReturned/finish门明确包括muxer。无替换muxer、重导出或第二close。legacy无Job keeper的正路入口直接拒绝。

详evidence/five-fix-completion-matrix.json，类型/静态实现与Android未证分层，不以自检直接改独立结论。

## 2. 必要实际typed验证

一次javac256MiB/release11/-g对**全部真实src/android/upstream/instrumentation**和两个小helper做类型检查，固定android-36.1 SDK jar/原deps/apksig作编译输入；不是host stub替身。单typed JVM256MiB、整窗口30秒、payload<64KiB，仅实际Java政策/原keeper状态/受控future-worker-callback端口，**36项通过**：journal6、layer/budget/FD8、实际E13同步listener+受控时钟7、raw owner6、muxer owner6+阶段3。pending/失败/未知不二close、跨case预留不退款、回执快照并发和原callback尾段都有实际同原线程finally放门/join；没有故意永久挂起、反射改状态、旧未知套件或实际Os/Media3解析/mux。

typed JVM PID31592 UTC04:23:42.426171至04:23:42.908277，自然exit0/原两流关闭；编译及单JVM总窗口<30秒。typed-001源码/class/原stdout-stderr/owner保全。测试后最终复核只补两处**显示字段**：receipt currentIOPhase及小测试配置snapshot报告实际limits；没有改预算守门/owner/journal/完成算法，也未重放typed JVM。post-typed-metadata-only-differences.json明确原/末hash；最终全Android编译覆盖末源。typed-versus-final-policy-classes.json逐类给真实字节对比，不笼统冒执行过最终DEX。后置独立apksig JVM仅查签名，不再跑typed状态测试。

## 3. 一次真实集中构建与准确产物

固定官方Gradle9.5.0/JDK21 launcher/原agent、client64MiB、single-use2048MiB，--offline --no-daemon --max-workers2 strict/metadata/原锁；purpose-built require_escalated按负责人恢复成功许可经自动审查处理本地loopback，不改防火墙/ACL/网络策略、不联网。仅:app:assembleDebug+:app:assembleDebugAndroidTest，**001一次成功，无第二构建**。client13656 UTC04:25:04.476803至04:26:51.553604自然exit0，stdout345021B/stderr389B，各<16MiB且<600秒；新daemon36964 UIDd9560244-ff53-47f5-bd27-432cd30d2077 creation04:25:05.333860，原client声明准确PID+镜像/创建校核+同Win32只读handle signal/exit0/原shutdown日志。原两流关，非仅isAlive/计数推退出；新两进程返回不替旧UNKNOWN收尾。

| 最终产物 | 大小B | SHA256 |
| --- | ---: | --- |
| app APK | 7151481 | f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad |
| test APK | 478124 | b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9 |
| production class JAR | 150394 | f246fff1e4faebbc05279283f47ca264523b4bf87ff1491c198c814352b1719c |
| instrumentation JAR | 40142 | 114aa266fb60d010f07a851c4a013a35ebb15c59bbaaaa4494566d2e20390722 |

目录artifacts下media3-android02-fix02-*；实际com.videokit.d1media3.android02及.test、versionCode1/nameD1-MEDIA3-ANDROID02-FIX02、process:media3/准确built-in runner。原apksig9.3.3 SHA先准入，后置一次256MiB/30s签名JVM27040自然exit0/两流关；两APK v2true/同单cert5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。实际AXML零权限/活动服务provider receiver/native、无sharedUID；同UID只是良性实验，不签RCE隔离。JCodec/JAAD/fork/host checks/platform-fixtures未混入APK。

105真实javac class（生产{counts['production']}、instrumentation{counts['instrumentation']}）逐SourceFile/major55/源pin/class/JAR entry核对，并核各定义在所属DEX真实存在；不冒JVM/DEX逐指令等价或实际方法已跑。14处Java/Manifest相对recovery01差异及appGradle仅versionName另列，所有前后patch/source hash保留。上游E4/E13/E6成熟源不改，薄适配调整原API调用/保管与phase hook。

300实际strict artifact=123binary/37module/140POM，SHA均匹配verification及原Android01实际集合；四个独立实际closure为12/17/12/0，实际javac classpaths独立保全。锁/metadata原字节、17坐标/Media31.9.3原样，无新依赖/下载，继承source/binary/metadata许可闭包及更新SBOM；不签最终商业/专利/FFmpeg清权。

## 4. 原fixture/功能与未证边界

test APK中准确8849B/hash19e815a4...778a9c、qualification03报告a814ac8e...9e0926/manifest、BBB349102B及原来源许可逐字对应。原文件/encoder未重生成，BBB仍只bbbObserve。实际Media3 raw flags保留，KEY_FRAME与仅末LAST_SAMPLE预声明政策不变，送mux只去内部marker；AnnexB1340规范化hash不混rawAU1360，实际CSD数组不强说三项，拼接AnnexB20。独立DTS仍UNPROVEN，空EOS1200000只是意图，真实重开duration须原SeekMap/TrackOutput证明，不填golden。

当前Android方法/原生FD fsync/close/实际muxer及正路fMP4重开/平台finish全部NOT_RUN；typed端口不冒这些事实。Asset内部FD/整个OS FD峰值API_UNPROVEN，known registered FD计量不是全平台总数。原MC-B01同原Provider/一次REOPEN/暂待不耗检查、真正UNKNOWN sticky保持；无旧大套件/ContainerPendingOrderCheck重跑、无host全空闲声明。所有原seal/history/旧FAIL/UNKNOWN保留。

## 5. 准确执行准备与停止

execution-plan.json重新绑定准确双APK/签名/runner/process/version及唯一scopeAll三参数，十内部case共享SDK readAt+copy/control/directEOF输入8MiB、output请求/attempt各16MiB、块64KiB/sample262144/source2/每源1/queue0，全scope单60秒。phase/FD历史各128、immutable journal196608/每status262144/全emission1048576界明确；无case/factory退款。全48原oracle分类与五修matrix均保，不把36typed项冒48Android PASS。

future仍6个逻辑调用：准确fingerprint1、本APP/TEST存在性各1、准确双新APK各install1不-r、scopeAll instrumentation1。准确binary出站**{binary}B**，命令每op4096总24576，logical outbound上界**{binary+24576}B**；preflight786432/install131072/所有pending-final两流1048576/controllerproof1048576，总logical inbound3014656B。无额外fixture push/无界logcat/其他项目操作。协议framing未观测，不冒精确wire字节，需未来capture工具合同绑定。

外wholewall观察90秒拟定，只停新准入并保管原capture/FD/worker/finisher，不强关管道/kill/二close；cleanup只在原返回后且单独准确批准处理新自有文件，不自动uninstall/clear/retry。现在scope/serial/freshIdle/captureTool仍null，先完整独立FIX02 B再负责人准确实机新范围；无自动许可或设备动作。本批设备/ADB/5037/占用/生成/编码/解码/播放0。

## 6. 封存与交接

evidence/fix02-freeze.json及外置D1-20261021-MEDIA3-ANDROID02-FIX02-source.zip覆盖全部相关源、五项typed原代码/class/流/owner、实际105class/JAR/DEX/APK/签名、准确asset/来源、300strict metadata副本/许可/SBOM、实际build原返回、五项/48矩阵/计量与API边界/准确计划/全部前后差异。大Gradle cache/mirror不是新产物；准确实际消费pin另留，原镜像不改。tools/review_materials.py仅纯Python核材料/hash/ZIP，不编译/Gradle/JVM/设备。

原recovery01 728/Android02 372/Android01 740/Container02 676/fork2738逐hash不变，独立B51b...及原QUAL03/A各manifest全保全。五项集中交负责人，不逐字段交接/自行关闭独立问题；等待整包B后统一后续。
'''
main=R/'docs/coder/D1_MEDIA3_ANDROID02_FIX02_DELIVERY_V1.0.md';main.write_text(report,encoding='utf-8');dump(E/'main-report-identity.json',pin(main));dump(E/'delivery-summary.json',{'overall':'BUILT_OFFLINE_FIVE_FIXES_IMPLEMENTED_TYPED36_PENDING_INDEPENDENT_B','mainReport':pin(main),'apks':[pin(app),pin(test)],'buildCalls':1,'classCounts':counts,'typedCases':36,'actualNativeAndroidMediaTests':0,'deviceOperations':0,'independentFiveFixClosure':'PENDING'})
print(json.dumps({'report':pin(main),'classCounts':counts,'logicalBinaryOutbound':binary,'typedFinalByteMatches':sum(x['byteIdentical'] for x in comparisons),'typedFinalClasses':len(comparisons),'fiveFixes':'PENDING_INDEPENDENT_B'},ensure_ascii=False))
