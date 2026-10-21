from pathlib import Path
import ast,datetime,difflib,hashlib,json,shutil,struct,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';A=B/'artifacts';O=R/'docs/coder/d1media3-android02'
assert not (E/'recovery01-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
audit=json.loads((E/'artifact-audit.json').read_text());sign=json.loads((E/'policy-signatures-001/result.json').read_text());assert sign['sourceAndBinaryPinsUnchangedAfterRun'] and sign['policyCases']==17
origins=json.loads((E/'class-origins.json').read_text());counts={'production':sum('instrumentation-' not in x['jar'] for x in origins),'instrumentation':sum('instrumentation-' in x['jar'] for x in origins)};assert sum(counts.values())==86
for p in A.glob('*.jar'):
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   data=z.read(name);assert not any(t in data for t in [b'android/media/MediaCodec',b'android/media/MediaExtractor',b'android/media/AudioTrack',b'android/view/Surface',b'killProcess',b'startActivity',b'setStreamVolume'])
parser=R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py';tree=ast.parse(parser.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','dexclasses']];exec(compile(ast.Module(body=defs,type_ignores=[]),'existing_pure_dex_source','exec'))
mapping=[]
for ap in audit['apks']:
 with zipfile.ZipFile(B/ap['path']) as z:classes={c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))}
 isTest=ap['package'].endswith('.test');items=[x for x in origins if ('instrumentation-' in x['jar'])==isTest]
 assert all('L'+x['className']+';' in classes for x in items)
 mapping.append({'apk':ap['path'],'sameActualSourceClassDefinitionsInDex':len(items),'allPresent':True})
dump(E/'source-class-dex-consumption.json',{'mappings':mapping,'classCounts':counts,'notSourceCompilationOnly':True,'noForbiddenOwnPlatformRuntimeCallReferences':True})
preserve=[]
for rel,expected in [('docs/coder/d1media3-android02/evidence/media3-android02-freeze.json','36d3d06ca38da726aa5ee1d97c54a7cffd025be1af686d0f991cdd4fb9e796b2'),('docs/coder/d1media3-android01/evidence/media3-android01-freeze.json','fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a'),('docs/coder/d1media3-container02/evidence/media3-container02-freeze.json','0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d'),('docs/coder/d1jcodec-observation01/evidence/observation01-freeze.json','8a62ef8e4fcea016870daccfe92097903cde667e4d624892309e6984d44e0725')]:
 p=R/rel;assert sha(p)==expected;rows=json.loads(p.read_text())['files'];assert all(sha(R/x['path'])==x['sha256'] for x in rows);preserve.append({'seal':pin(p),'verifiedRows':len(rows)})
for rel,expected in [('docs/tester/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION03/review-evidence-manifest.json','a814ac8e2b2dc5c38189a1a582ee161646cefe1a4a1f43bae863a50aad9e0926'),('docs/tester/D1_MEDIA3_ANDROID02_CONTAINER_PHASE_A_EVIDENCE/phase-a-evidence-manifest.json','82a2f7942023d16a7cf98a4e5c24be052e2d8ebf946b401ab63742bd2724a02c')]:
 p=R/rel;m=json.loads(p.read_text());assert sha(R/m['report'])==expected and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles']);preserve.append({'manifest':pin(p),'report':pin(R/m['report']),'verifiedRows':len(m['evidenceFiles'])})
dump(E/'all-baseline-preservation.json',preserve)
gaps=[{'id':'REC-OBS01','kind':'SOURCE_OBSERVED_REPORTING_GAP_NOT_RUNTIME_FINDING','area':'Partial batch failure receipts','fact':'ExperimentJob exports caseReceipts only if current method==scopeAll. On mid-batch exception current method remains failing subcase, so earlier completed case snapshots remain in retained Job memory but are omitted from final/pending receipt. Current failing observation/firstFailure and original ownership are still present.','consequence':'Cannot claim complete externally exported per-case evidence on partial failure. Do not schedule device as fully evidence-ready.','proposalNotApplied':'Next concentrated source batch export existing caseReceipts whenever requestedMethod==scopeAll, mark partial/completed counts even failure, with same byte-budget checks; no additional worker or replay.','newBuildAfterSecond':False},{'id':'REC-OBS02','kind':'DECLARED_OBSERVATION_LIMIT','area':'SDK requested versus native attempted bytes','fact':'Scope inputReserved tracks copy/native read attempt sizes+EOF/control reservation; inputActual and provider physicalBytes track returned native bytes. SDK requested total and full per-phase request ledger are not separately emitted. Short3 native request3 must not be called an SDK requested3.','consequence':'8MiB applies native physical attempt accounting; exact SDK requested total remains UNAVAILABLE, not fabricated from actual bytes or readCalls. Layer-separated reporting needs next batch if mandatory.','proposalNotApplied':'Expose bounded cumulative SDK-requested/native-requested/actual per-phase observations on same original paths, no refund or new factory budget.','newBuildAfterSecond':False}]
dump(E/'known-observation-gaps.json',gaps)
cases=['preopenAdmission','rejectFixture','cancelLateRead','writerPending','inspectKnown','inspectShort3','inspectUnknown','inspectSeek1s','bbbObserve','muxQualified']
app,test=[B/x['path'] for x in audit['apks']];binary=app.stat().st_size+test.stat().st_size
plan={'status':'BUILT_OFFLINE_NOT_DEVICE_AUTHORIZATION_KNOWN_OBSERVATION_GAPS','runner':'com.videokit.d1media3.android02.test.Media3Instrumentation','app':'com.videokit.d1media3.android02','test':'com.videokit.d1media3.android02.test','process':'com.videokit.d1media3.android02:media3','version':'D1-MEDIA3-ANDROID02-RECOVERY01','versionCode':1,'apks':[pin(app),pin(test)],'signerCertificateSha256':sign['certificateSha256'],'scopeId':None,'serial':None,'freshIdleGate':None,'captureToolIdentity':None,'requiredArguments':{'case':'scopeAll','fixtureSha256':'19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c','runId':'D1MA02-<reviewed fresh id max32>'},'singleOriginalWorkerScopeOrder':cases,'entry':'Media3Instrumentation.onStart -> one ExperimentJob.run -> scopeCases/runCase, no new per-case Job/factory budget','directIndividualCaseAdmission':'REJECTED; public policy verified','AndroidActualMethodsRun':0,'wholeScopeSdkBudgets':{'nativeInputAttemptedAllCopyHashParseSeekReopenAndCases':8388608,'sdkRequestedAggregate':'UNAVAILABLE_CURRENT_REPORTING_GAP','outputAttemptsAllCasesNoRefund':16777216,'block':65536,'sample':262144,'sources':2,'perSourceInFlight':1,'queue':0,'oneWholeScopeBodyDeadlineMs':60000,'receiptUtf8PerStatus':262144},'futureOperationBudget':{'logicalPlatformInvocations':6,'readOnlyPreflight':['approved exact device build fingerprint once','exact new APP package presence once','exact new TEST package presence once'],'install':['exact new app once without -r','exact new test once without -r'],'execute':['single scopeAll instrumentation once, original stdout/stderr ownership retained'],'binaryOutboundBytesExact':binary,'binaryTransfers':2,'extraFixturePush':0,'commandTextMaxPerOperation':4096,'commandTextMaxTotal':24576,'logicalOutboundPayloadUpperBound':binary+24576,'preflightStdoutStderrMaxTotal':786432,'installStdoutStderrMaxTotal':131072,'instrumentationAllPendingAndFinalStdoutStderrMaxTotal':1048576,'controllerProofLogMax':1048576,'allLogicalInboundTextUpperBound':3014656,'adbTransportFramingExact':'NOT_OBSERVED_OR_INCLUDED_AS_FAKE_EXACT; future capture/tool contract must separately bind protocol overhead','noUnboundedLogcatOrShell':True},'admissionPrerequisites':['independent complete offline B','coordinator resolves/accepts REC-OBS01/02 explicitly; current plan not execution-ready','exact scope/device/fresh idle and capture/transport accounting gate','no old running scope reuse or force-stop'], 'stopRules':['one unknown/error/budget/unsupported seek stops later cases; no retry or factory refund','same original FD/worker/task kept; no interrupt/kill/second close/old deletion','partial case snapshot export gap is known, do not misinterpret missing history as not executed','no generation/decode/audio/player/READY COMMIT/isolated format'], 'currentDeviceOrAdbOperations':0}
dump(E/'execution-plan.json',plan)
contract={'status':'PREDECLARED_NOT_RUNTIME_OBSERVED','hostFixture':'exact8849/hash19e815...778a9c, independent HOST_CONTAINER facts only','csd':'Actual Media3 arrays must each AnnexB4, concatenated actual bytes20/hashf6dc...75a8. No fixed3 arrays, no insertion. Actual raw arrays/hash/cardinality recorded.','sample':'Actual Media3 AnnexB4 sample1340B against independent normalized1340 digests, never rawAU1360. Actual raw flags preserved; KEY_FRAME required, only optional LAST_SAMPLE allowed on index5, reject all other bits. Before mature mux strip LAST_SAMPLE, pass key semantic flag; reopened compares same-framework key semantics/PTS/size/hash and declared actual output flags policy.','DTS':'UNPROVEN_NO_INDEPENDENT_TRACKOUTPUT_DTS_API, no sourcePTS fabricated as DTS','EOS':'actual existing emptyEOS4 at1200000 is intent. Actual reopened SeekMap/TrackOutput duration must1200000; unset stays NOT_PROVEN/failure, not filled. Exactly6 payloads, no7th','sourceAndReturn':'same original E4Owned FD and readAt futures/tasks, no REOPEN while writer/task pending; MC-B01 same grant once/no sticky pending preserved','deadline':'one whole-scope worker body completion after all cleanup <60s and actual sameworkerjoin; finalizer owner-at-receipt1 and actual external finish/streams remain separate','budget':'same Job counters shared across10 cases; controlled late-read1 and writer4 pre-reserved in same counters, no hidden second-case8MiB/16MiB reset','capabilityVsActual':'FD.sync/nativeclose capabilities compiled, all actual Android results NOT_RUN; static code and source counts do not substitute','knownObservationGaps':[x['id'] for x in gaps]}
dump(E/'comparison-and-lifecycle-contract.json',contract)
oracles=json.loads((B/'reference/android02-stage-a/independent-m2a01-m2a48-oracles.json').read_text())['cases'];assert len(oracles)==48
static={'M2A01','M2A02','M2A03','M2A05','M2A06','M2A07','M2A45','M2A46','M2A48'}
matrix=[]
for x in oracles:
 item={'id':x['id'],'area':x['area'],'originalOracleStatus':x['status'],'originalOracle':x['oracle'],'coderEvidenceClassification':'STATIC_MATERIAL_EVIDENCE_ONLY' if x['id'] in static else 'IMPLEMENTED_COMPILED_ANDROID_RUNTIME_NOT_RUN','independentVerdict':'PENDING','actualAndroidRun':False}
 if x['id']=='M2A18':item['coderEvidenceClassification']='DTS_API_UNPROVEN_DECLARED_GAP'
 if x['id'] in ['M2A37','M2A39','M2A44','M2A47']:item['remainingLimit']='REC-OBS01/02 and unbound device/capture gates; see known-observation-gaps/execution-plan'
 matrix.append(item)
dump(E/'m2a01-m2a48-completion-matrix.json',matrix)
sbom=json.loads((B/'reference/android01-sbom.cdx.json').read_text());sbom['metadata']['component']['name']='VideoKit D1 MEDIA3_ANDROID02_BUILD_RECOVERY01 empty experiment';sbom['metadata']['component']['version']='D1-MEDIA3-ANDROID02-RECOVERY01';dump(B/'media3-android02-recovery01-sbom.cdx.json',sbom)
dump(E/'dependency-license-difference.json',{'newCoordinatesOrVersions':[],'actualArtifacts':300,'strictClosures':[12,17,12,0],'same300ActualExternalIdentitiesAsAndroid01':True,'verificationMetadataAndLocksByteIdentical':True,'inheritedFrameworkSourceAndLicenseClosure':'reference/android01 source-admission/license/sbom plus official-added metadata; original limited admission retained, not new commercial/patent signoff','AndroidSdkBuiltinAPI':'Os.open/FD wrapper only, SDK license baseline unchanged','JCodecOrForkApkRuntime':False,'syntheticAssetSource':'original six synthetic pixels; actual generation/qualification history in supplied frozen references, not rerun','BBBAttribution':'inherited SOURCE_AND_LICENSE.txt exact bytes, only bbbObserve, no encoding change'})
dump(E/'config-version-difference.json',{'file':'app/build.gradle.kts','oldSha256':sha(O/'app/build.gradle.kts'),'newSha256':sha(B/'app/build.gradle.kts'),'change':'versionName only D1-MEDIA3-ANDROID02-CONTAINER -> D1-MEDIA3-ANDROID02-RECOVERY01; dependency/locks/API levels unchanged'})
report=f'''# D1_MEDIA3_ANDROID02_BUILD_RECOVERY01 完整交付 V1.0

2026-10-21。**BUILT_OFFLINE_WITH_KNOWN_OBSERVATION_GAPS_PENDING_INDEPENDENT_REVIEW**。准确双APK/源-JAR-DEX/签名/strict双闭包已取得；这关闭本新恢复范围的“无产物”状态，不改旧Android02构建失败。真实Media3提取→mux→fMP4重开及所有Android方法仍NOT_RUN；当前两项已知观测缺口和fresh设备范围未闭合，**不签实机就绪/隔离格式/READY COMMIT/播放**。D1未过M0未启。

## 1. 独立恢复与两次集中构建

新目录D:/CodexProjects/VideoKit/docs/coder/d1media3-android02-recovery01；复制已封存源/准确本地mirror，独立recovery-gradle-home。原Android02/旧缓存registry/daemon35512以及48945/17257未查询/attach/终止/改写。旧日志只证明server写loopback/greeting和client无法连，本批不作唯一根因诊断。

依据负责人明确恢复及阶段A补充，purpose-built exec require_escalated通过自动审查执行固定JDK/Gradle9.5.0已有工具；不改防火墙/ACL/策略、不联网、不关闭strict。直接java -jar官方gradle-gradle-cli-main9.5.0，参数与已固定gradle.bat的默认64MiB/client agent/launcher等价，launcher/bat原hash在owner；daemon原heap2048MiB、--offline --no-daemon --max-workers2 --rerun-tasks --info --dependency-verification strict，只app:assembleDebug+app:assembleDebugAndroidTest。

第一次恢复构建001 UTC03:31:18.427016至03:32:59.039903，client28184自然exit0，stdout349760B/stderr394B；本次daemon22948/UIDcf8fac88-ff0c-4260-a786-800c078335f6，creation03:31:19.383725，同已持有Win32只读进程handle signal/exit0证明自然返回。阶段A补充于构建中到达，故先保全该真实旧源产物/源快照/原classJAR和controller在build-001/before-stage-a，再集中实现新合同，不改运行中输入。

阶段A最新要求明确允许必要源码变更在最多两次集中构建内处理。第二次最终构建002 UTC03:35:33.027334至03:36:10.047127，client36588自然exit0，stdout99992B/stderr394B；daemon39576/UID15d77138-57c5-43dc-845f-6203324b6da2，creation03:35:33.800600，同原handle signal/exit0。两次均非“无daemon”，single-use真实身份/日志/源pin保全；原Popen两流关闭、各≤16MiB、未超600秒、无kill/interrupt/--stop/第三次构建。当前新进程的自然返回不替旧UNKNOWN收尾，不证明host全空闲。

## 2. 准确最终产物与真实消费

最终app artifacts/media3-android02-recovery01-app-debug.apk，**7124541B/SHA2560998beeaa129ef3858fbe1122b80394383f96ad75196c8e4f22b4b856237f6c8**；test artifacts/media3-android02-recovery01-test-debug.apk，**466368B/SHA256f8323a1c0d82d23382baf4f776e56b26174fd5354de5e86d897cb979a467f5de**。

实际包com.videokit.d1media3.android02/.test，versionCode1/versionNameD1-MEDIA3-ANDROID02-RECOVERY01；target进程:media3/准确built-in instrumentation。apksig真实验证最终两APK和首构建保全两APK共四个，v2=true、单证书SHA2565e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。不是用Manifest声明代验签。两APK零权限/零活动服务provider receiver/零native，debug良性空实验同UID非RCE隔离；无JCodec/fork/host checks/platform-fixtures混入。最终test内准确asset8849/hash19e815a4...778a9c、qualification manifest/BBB旧观察资产/来源许可逐字节对应，无替代旧APK。

真实app class JAR **130790B/SHA25695a6068c5719cc4400d2e10d8dd4262a40d7fe4463166b7889975c4b02f62e6b**；instrumentation JAR **32695B/SHA2565742a92cb8910689db7e464a7992093848162e00a47147924c6a79e3de9d6940**。共86真实javac class（生产{counts['production']}/instrumentation{counts['instrumentation']}）逐SourceFile/major55/源hash/实际class/打包JAR核对，再确认对应全部类实际出现在各自DEX中；platform fixture定义不入APK。源码差异7处Java/Manifest及app Gradle仅版本名差异单列，首/末源pin与patch完整。

实际strict消费300artifact=123binary+37module+140POM，全部匹配verification SHA256并与Android01原真实300身份集合完全相同；configurations独立实际closures为appCompile12/appRuntime17/testCompile12/testRuntime0。两次真实编译classpath单列，非从主包17坐标推断测试闭包。锁/app/settings verification字节原样，Media3固定1.9.3、无新依赖/下载/版本/许可边界放宽。继承已准入source/binary/metadata/Apache2闭包、更新本候选SBOM、实际metadata审查副本一并封存；不作专利/商业最终清权声明。

## 3. 阶段A集中修改与完整功能源码

阶段A82a2f794...724a02c/完整M2A01–48合同已复制reference并保原PREPARED_NOT_RUN，不反写独立结论。本恢复batch仅scopeAll可由外部参数准入，内部十case按preopenAdmission/rejectFixture/cancelLateRead/writerPending/inspectKnown/inspectShort3/inspectUnknown/inspectSeek1s/bbbObserve/muxQualified顺序，在**同一个Job、同一个原worker**中运行。内部每case结束先查同原资源返回，所有source/native attempt/copy/hash/parse/seek/reopen与output attempt累计计数不重置；不能逐case各获得8MiB/16MiB。全scope同一60秒deadline，非10个60秒。

原CREATE_NEW O_EXCL|O_NOFOLLOW0600、实际copy全EOF/hash、同FD flush/sync/close及只读后交源保持，每子case新runId+case私有root，不覆盖或删旧文件。资格化六帧真实capture→原MatureMuxerBinding/FragmentedMp4Muxer/E6空EOS→原临时Sink→同writer/FD/任务返回→一次只读grant→真实FragmentedMp4Extractor正路保留；BBB仅观察，不送mux。MC-B01暂待不耗检查/不sticky、同原Provider/REOPEN1不变，不添加账本/新框架。

实际Media3 raw flags原样记录；预声明KEY_FRAME必须、只许末sample带LAST_SAMPLE内部marker，其他bit拒绝。送原mux前仅去LAST_SAMPLE，保key语义，输出按实际flag政策及同框架key/PTS/size/hash核对，绝不从JCodec keybool造raw1。实际AnnexB4六sample1340B与独立规范化hash比较，旧rawAU1360不混；CSD实际数组按真实顺序拼接AnnexB20比hash，不强说三initData，不注入SPS/PPS。独立DTS API无→UNPROVEN，不用PTS填DTS。原空EOS1200000仅意图，重开SeekMap/TrackOutput实际duration必须1200000，TIME_UNSET不补绿。

## 4. 有界必要自检与证据缺口

无变化host旧20父组（含MC-B01内部8）仅继承原证据，不重跑旧未知套件。改动处单独一次512MiB helper javac、一次256MiB/30秒JVM，实际production JAR在classpath前，public policy+apksig原返回均自然exit0/两流关闭。JVM40380 UTC03:39:23.977541至03:39:24.357180；**17项**含唯一scopeAll准入、十单case拒绝、实际rawflags/末marker/EOS/保护bit规则及四真APK签名；不加载Android job/媒体或伪造native对象验证功能。

预算源码同scope输入8MiB/native attempt与EOF/copy、output16MiBattempt含short/UNKNOWN无退款；controlled取消read预留1、writer预留4并计同scope。native实际返回、provider physicalBytes、parser Reader返回字节与scope inputReserved分列。控制输入/整批receipt/平台原返回和最终封存见计划，但以下是**当前明确已知缺口**，不派设备求证后才补：

* **REC-OBS01：** 中途case异常时method仍为失败子case，receipt仅在method==scopeAll时放caseReceipts，故此前完成case快照保留在原Job内存却未导出到pending/final。失败本case/firstError/原任务保管仍有，不代表此前没执行；不能声称整批外部证据完整。建议下一集中批按requestedMethod导出已有partial case历史及实际completedCount，保同字节预算，不新worker或重放。
* **REC-OBS02：** inputReserved是copy/native attempt（short3按实际native请求3预留，不可叫SDK请求3），inputActual/provider physicalBytes为已返；当前没有独立SDK requested累计及完整每phase requested总量。此字段UNAVAILABLE，不能从actual/readCalls推算。建议下一集中批在同原路径补有界分层观察。当前8MiB计量层要如实标native physical attempt，不偷换SDK请求累计。

两项详evidence/known-observation-gaps.json。它们来自coder最终静态复核，不冒独立缺陷裁定；当前两次构建窗口已满，没有第三次偷偷修编译/重跑。整包交负责人统一决定后续集中修复/独立B；不是可执行READY包。

## 5. 原返回、整批计划与准确预算

原worker cleanup后单调completed-start严格<60秒+实际同worker join与timer pending分列；case快照记录sameWorkerStillExecutingScope，不能说每case各join。最终source0/output0与runnerfinalizerOwnerAtReceipt可能1、super.finish外部返回/原两流捕获仍分开要求。设备未运行，因此实际FDsync/close/原task/case/外finish均NOT_RUN，不能用此次本机helper的exit0替它们。

execution-plan.json已绑定准确双APK/证书/runner/process/version和唯一scopeAll三参数、十内部case、无case/factory退款、停止规则。当前scopeId/serial/freshIdle/captureTool仍空；先完整独立B及处理上述缺口，才可另派准确设备scope，不自动使用旧许可。

未来计划逻辑平台调用6次：准确device fingerprint1、仅本APP/TEST存在性各1、准确新双APK各install1（不-r覆盖）、scopeAll instrumentation1。准确二进制出站**{binary}B**；无额外fixture push，参数/命令每op≤4096B总24576B，logical outbound上界**{binary+24576}B**。preflight两流总786432B、install两流131072B、instrumentation所有pending/final两流1048576B、controller proof log1048576B，总logical inbound文本3014656B。每status JSON≤262144B，整批只一worker/60秒，不复用旧14ops或10次新scope额度。

上述是应用层控制/二进制预算；ADB transport framing未观测，明确非假精确wire计量，future capture/tool合同仍需准确绑定。任何未知/超时/不符hash/CSD/PTS/真实时长/不支持seek停止后继case，保管同原FD/thread/任务，未返回不reopen/retry/refund/release；不kill/二close/clear/reinstall/跨项目probe/无界logcat。当前设备/ADB/5037/占用操作0，编码生成/播放/解码0。

## 6. 完整矩阵、封存与交接

M2A01–48每行原oracle、静态/已编译/Android未运行/独立待审分类完整列evidence/m2a01-m2a48-completion-matrix.json；DTS、真实duration、partial导出、SDK requested、外finish、fresh设备等未证不填PASS。原冻结Android02 372、Android01 740、Container02 676、fork2738行逐hash不变，qualification03与新阶段A各原manifest完整保全；旧source/媒体/encoder/App/UNKNOWN不触。

封存evidence/recovery01-freeze.json及外置D1-20261021-MEDIA3-ANDROID02-BUILD-RECOVERY01-source.zip覆盖最终和首构建原源/产物/全流/owner/daemon快照、86原class+JAR/DEX/APK/签名helper、300实际strict消费metadata、准确fixture/来源、许可/SBOM、集中patch/阶段A合同/全scope计划/已知缺口。大cache/mirror非运行结果不封作产物；实际消费身份/审查副本已固定，旧mirror不改。纯Python tools/review_materials.py只核材料/hash/ZIP，不编译/Gradle/JVM/设备。

当前完成新范围内离线构建恢复、实际产物身份与集中源码/政策验证；**完整Android功能与观测仍OPEN**。主动交负责人完整包，不逐字段调试或自行设备；待统一新批范围。
'''
main=R/'docs/coder/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_DELIVERY_V1.0.md';main.write_text(report,encoding='utf-8');dump(E/'main-report-identity.json',pin(main));dump(E/'delivery-summary.json',{'overall':'BUILT_OFFLINE_WITH_KNOWN_OBSERVATION_GAPS_PENDING_INDEPENDENT_REVIEW','mainReport':pin(main),'finalApks':[pin(app),pin(test)],'buildCalls':2,'classCounts':counts,'newPolicyCases':17,'knownObservationGaps':[x['id'] for x in gaps],'AndroidRuntime':0,'deviceOperations':0})
print(json.dumps({'report':pin(main),'counts':counts,'logicalBinaryOutbound':binary,'knownGaps':[x['id'] for x in gaps]},ensure_ascii=False))
