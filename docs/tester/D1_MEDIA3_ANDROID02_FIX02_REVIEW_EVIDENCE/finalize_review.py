from pathlib import Path
import datetime,hashlib,json
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-android02-fix02';E=Path(__file__).resolve().parent;REPORT=R/'docs/tester/D1_MEDIA3_ANDROID02_FIX02_PHASE_B_REVIEW_REPORT_V1.0.md';assert not REPORT.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit=read(E/'independent-audit-summary.json');typed=read(E/'typed-signatures-001/result.json');fixes=read(E/'independent-five-finding-closure.json')['fixes'];assert typed['totalGroups']==46 and len(fixes)==5
baseline=[]
for x in read(B/'evidence/all-baseline-preservation.json'):
 y=x.get('seal',x.get('manifest'));p=R/y['path'];assert p.stat().st_size==y['bytes'] and sha(p)==y['sha256'];d=read(p);rows=d.get('files',d.get('evidenceFiles'))
 for z in rows:
  q=R/z['path'];assert q.stat().st_size==z['bytes'] and sha(q)==z['sha256']
 if 'report' in x:
  z=x['report'];q=R/z['path'];assert q.stat().st_size==z['bytes'] and sha(q)==z['sha256']
 baseline.append({'identity':y,'rowsVerified':len(rows)})
sbom=read(B/'media3-android02-fix02-sbom.cdx.json');coords={':'.join(c[k] for k in ['group','name','version']) for c in sbom['components']};locks={l.split('=')[0] for l in (B/'app/gradle.lockfile').read_text().splitlines() if l and not l.startswith(('#','empty='))};assert coords==locks and len(coords)==17
art=read(B/'evidence/actual-consumption/artifacts.json')
for c in sbom['components']:
 coord=':'.join(c[k] for k in ['group','name','version']);h={v['content'] for v in c['hashes'] if v['alg']=='SHA-256'};sel=[x for x in art if x['coordinate']==coord];b={x['sha256'] for x in sel if x['kind']=='binary'};assert sel and c['licenses']
 if b:assert h&b
 else:assert not h and coord in ['androidx.annotation:annotation:1.6.0','org.jetbrains.kotlin:kotlin-bom:1.8.0']
save('independent-baseline-license-review.json',{'baselines':baseline,'sbomCoordinates':sorted(coords),'scope':'Inherited fixed source/binary/metadata and asset rights evidence only; no new global license/patent/FFmpeg/model clearance','oldUnknownQueries':0})
old=read(R/'docs/tester/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_REVIEW_EVIDENCE/independent-m2a01-m2a48-results.json')['cases'];assert len(old)==48
updates={
 'M2A04':'真实APK asset identity通过；preopen RawWrite/OriginalOwner代post-open wrapper，copy/hash/flush/sync/read-only仅源集成，Android NOT_RUN。',
 'M2A09':'preopen/capability/role源拒门保持；唯一scopeAll纯Java准入代表性通过，真实native open未跑。',
 'M2A10':'SDK readAt max4/native short3/source实际返回独立计量；higher-library request非此边界，实际short native结果NOT_RUN。',
 'M2A19':'原capture完成门保持，Job muxer keeper已集成；typed原holder通过，realcapture及mature对象NOT_RUN。',
 'M2A21':'Job muxer keeper构造前保管，真实DEX和源路径完整；typed阶段失败/单close门通过，不冒实际mux。',
 'M2A28':'copy及mux原OutputStream request/attempt/actual/unknown计同scope，short continuation也计attempt；全Digest/readback门源保持，实际输出未生成。',
 'M2A29':'raw对象/slot/owner在Os.open前登记，muxer keeper分配前挂Job；typed allocating/calling/closing与unknown强持有通过；平台分配未跑。',
 'M2A30':'Java unbuffered flush明确no-buffer，本原Os.fsync/close待Android；真实DEX类型不代native成功。',
 'M2A31':'最终OriginalOwner同步原操作状态门typed证；Future/counter/outerSink不代真实mux/native归还。',
 'M2A33':'typed真实原线程/回调尾段/close pending通过；controlled boundary源更新返回ack；非真实blocked native。',
 'M2A35':'meter registered descriptor/known native FD peak与asset-stream/source lease各分层，API_UNPROVEN平台内部FD不补；typed独立峰值通过。',
 'M2A36':'同原worker join/E13平台finisher源，muxer/raw keeper已纳入resourcesReturned；真实外finish仍NOT_RUN。',
 'M2A37':'同ScopeMeter inputRequested SDK readAt+copy/control/directEOF8MiB预扣，无case reset；nativeattempt/actual/EOF/unknown及phase分列，typed有限cap验证通过。',
 'M2A38':'同ScopeMeter outputRequested与attempt各16MiB含copy/controlled/mux，short/unknown不退款；typed验证通过，平台实际未跑。',
 'M2A39':'新6logicalops/双APK7629605/outbound7654181/inbound3014656；wholewall90秒，scope/capture/framing/实际清理合同未绑定，非设备令。',
 'M2A40':'仅授权typed原holder及真实E13同步callback顺序代表性通过；全部Android取消阶段未覆盖。',
 'M2A42':'最后受控signal/errorcallback后CompletionPoint marker；deadline-1/equal/+1与晚观察同原join通过；非OS退出或实机60s。',
 'M2A43':'首错unknown sticky与MC-B01源保持，异常已完成history/current快照不依currentmethod判断导出；typed代表性通过。',
 'M2A44':'immutable journal内容/单status/全emission界，失败/pending历史保留；typedoverflow/单close通过；原UNKNOWN不删不kill。',
 'M2A45':'874/ZIP874/105class/双APK真实DEXcode/signature/300strict实际闭包通过。',
 'M2A47':'scopeId/serial/freshIdle/captureTool仍null；当前离线B不触设备，持续平板许可保持无需重复索取。'}
for c in old:
 c['priorRecoveryBNotes']=c.pop('notes');c['independentBResult']='FIX02_COMPLETE_OFFLINE_LIMITED_EVIDENCE_ANDROID_NOT_RUN';c['notes']=updates.get(c['id'],c['priorRecoveryBNotes'].replace('R01-B03','FIX02已修时间门（有限typed）').replace('R01-B04','FIX02已修原raw keeper（平台未跑）').replace('R01-B05','FIX02已修原mux keeper（平台未跑）'));c['runtimePass']=False;c['actualAndroidStatus']='NOT_RUN'
save('independent-m2a01-m2a48-results.json',{'cases':old,'phaseAUnchanged':True,'actualAndroidRuntimeCases':0,'independentFiniteGroups':46,'originalCoderTyped36NotOverwritten':True})
plan=read(B/'evidence/execution-plan.json');p=plan['futureOperationBudget'];assert p['logicalPlatformInvocations']==6 and sum(x['bytes'] for x in plan['apks'])==p['binaryOutboundBytesExact']==7629605 and p['logicalOutboundPayloadUpperBound']==7629605+24576==7654181 and p['allLogicalInboundTextUpperBound']==786432+131072+1048576*2==3014656 and p['outerWholeWallObservationSeconds']==90
assert all(plan[k] is None for k in ['scopeId','serial','freshIdleGate','captureToolIdentity'])
save('independent-operation-budget-review.json',{'plan':pin(B/'evidence/execution-plan.json'),'exactBinaryOutbound':7629605,'commandUpperBound':24576,'logicalOutbound':7654181,'logicalInboundText':3014656,'operations':6,'sdkBodySeconds':60,'outerWholeWallObservationSeconds':90,'captureToolScopeSerialFreshIdleUnbound':True,'adbWireBytes':'UNOBSERVED_NOT_FAKE_EXACT','cleanup':'No automatic delete/clear/uninstall/kill; only new owned files after original returns under later accurate scope','deviceAuthorizationFromThisB':False})
seal=read(B/'evidence/fix02-freeze.json')
for x in seal['files']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
save('review-process-and-read-ledger.json',{'newHelperCompiles':1,'newHelperJvms':1,'newHelperGroupCount':46,'finiteTypedPolicyGroups':45,'signatureGroup':1,'actualApksVerified':4,'typedPayloadUtf8Bytes':301,'wholeWindowSeconds':typed['wholeSeconds'],'heapMiB':256,'newGradleDeviceAndroidMediaCalls':0,'oldUnknownActions':0,'staticAuditCorrections':['Initial shell quoting prevented Python preparation from running; no candidate write or JVM occurred.','Adapted prior tester audit briefly compared new source to itself due replacement order; exact declared-diff assertion failed. Set exact recovery01 baseline, then full audit.','DEX expectations still named removed ExperimentJob.reserveInput/createNew; updated to actual ScopeMeter/RawWrite plus implemented code offsets. No product edits and no helper rerun.'],'rawIdentityReads':'Finite hashes/ZIP members/AXML/DEX/class/APK signature and opaque assets, including media bytes inside files. No MP4/AVC/Media3 parser. Not physical I/O and not old QUAL03/future Android8MiB ledger.','apksigInternalReadBytes':'NOT_INSTRUMENTED_NO_ZERO_OR_EXACT_TOTAL_CLAIM','sameFrozen874After':True})
ftext='\n\n'.join('### '+f['id']+' — '+f['verdict']+'\n\n'+f['finiteEvidence']+'。\n\n准确冻结来源：'+'；'.join(a['path']+':'+str(a['line'])+'（SHA '+a['sha256']+'）' for a in f['sourceEvidence'])+'。\n\n限制：'+f['remaining'] for f in fixes)
text='''# D1 Media3 Android02 FIX02 独立整包阶段B复审 V1.0

2026-10-21；tester；完整五项集中修复候选，离线B。

## 结论

**PASS_LIMITED_OFFLINE_FIVE_SOURCE_FIXES_ANDROID_NOT_RUN**。874项冻结材料、全部源差异、105真实class→JAR/DEX/双APK、实际strict300和一次构建原client-daemon返回已独立核；tester自有单helper对最终生产JAR完成**46检查组（45有限typed/政策组+1四APK签名组）通过**。旧R01-B01–B05的具体源码缺口及有限纯Java原keeper/ledger/journal/完成点门可在本文限定范围关闭，未发现新增确定源码阻断。

不是五项Android动态复现转绿，也不是48个Android PASS。实际Os/nativeFD/AssetManager/Media3提取捕获→真实mux→fMP4重开/真实duration与DTS/外platform finish均**NOT_RUN或能力UNPROVEN**；当前scope、设备、freshIdle、capturetool及协议采集未绑定，不签设备执行就绪或自动开测。D1未过/M0未启，不签隔离格式/READY/COMMIT/播放/RCE/J11/P0/发行清权。由负责人依据完整结果一次决定下一准确范围。

## 封存、差异与实际产物

coder报告11813B/SHA880a251377cff7544a00fc0ba051ff1bd36ff55d8d911fc5a8e2d7a3ad72fac1；seal39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad。新纯Python材料入口receipt871b058d379ca90de8f310850c5a3a770c22519e1395fc29241f39be4af11f6d通过；另自写独立审**874原文件/ZIP874唯一成员**、集合/大小/hash/成员CRC及结束再hash。外ZIP10057392B/SHAba634412bc71ee0fe062d715956f2618bf0ff2cee9226d3ce730ff94e7af2102。无候选写入、Gradle重建或cache/旧进程查询。

相对冻结recovery01逐src/android/upstream/instrumentation/app/src全集比对：**14项源差异=4新纯Java辅助+9既有Java变化+1testManifest**；无旧源删除/未声明变更。appGradle仅versionName FIX02另列，原锁/verification逐字不变；上游E4/E13/E6成熟源码保持，薄适配增加phase/短请求/原owner门，没有换后端或删十case功能。patch文件表头沿生成器旧名称不作为来源判断，实际前后hash及全集比较是依据。

| 最终产物 | 大小B | SHA256 |
| --- | ---: | --- |
| app APK | 7151481 | f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad |
| test APK | 478124 | b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9 |
| production class JAR | 150394 | f246fff1e4faebbc05279283f47ca264523b4bf87ff1491c198c814352b1719c |
| instrumentation JAR | 40142 | 114aa266fb60d010f07a851c4a013a35ebb15c59bbaaaa4494566d2e20390722 |

105真实javac class（94生产+11instrumentation）独立解析SourceFile/major55/实际class源hash/JAR entry，全部所属DEX定义存在；实际app DEX4974/test324类，run/receipt/预算/RawWrite/OriginalOwner/CompletionPoint/ScopeJournal/muxer门及真实Extractor/FragmentedMuxer方法均有codeOffset/指令体。它是源pin/编译事件与产物交叉链，不声称JVM→DEX逐指令等价或代码已在Android执行。

二进制AXML独立核com.videokit.d1media3.android02/.test、versionCode1/FIX02、:media3、准确内置runner/targetProcesses；零权限/活动服务provider receiver/native/sharedUID，无JCodec/JAAD/fork/fixturetool/host checks混入，继承android构建定义集合准确同旧。test不带Media3本体，通过app闭包访问。test内原qualified8849/hash19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c、BBB349102与资格manifest/来源许可逐字对应，没有新生成/替媒体。

## 一次原构建与strict真实消费

仅读冻结build001全流/controller/owner/daemon快照：client13656 UTC04:25:04.476803–04:26:51.553604自然exit0，stdout345021/stderr389B/两流关；本次single-use daemon36964 UIDd9560244-ff53-47f5-bd27-432cd30d2077，creation04:25:05.333860，同原Win32只读handle signal/wait0/exit0。准确PID/UID/镜像/创建时间与各原日志/client声明对应，BUILD SUCCESSFUL/shutdown同时可见。单次<600秒/每流<16MiB，无第二构建或kill/stop；--no-daemon不冒没有新JVM。

独立提取实际verification原事件300身份：123binary/37module/140POM，镜像及metadata副本SHA均吻合原verification和Android01实际300集合；appCompile12/runtime17/testCompile12/testRuntime0四独立实际closure逐集合吻合锁，两条真实javac classpath事件存在，不从app17推test，也不以请求strict布尔代消费。原17坐标/Media31.9.3/locks/verify-metadata=true字节不变，无新依赖。

SBOM17坐标/适用binaryhash/许可核实，annotation聚合与kotlin-bom仅metadata消费，空binaryhash不冒二进制；继承source-admission/官方metadata与准确资产许可保全，不扩大成商业/专利/FFmpeg/模型/最终发行结论。原recovery01 728/Android02 372/Android01 740/Container02 676/fork2738及列入的testerB/QUAL03/A原manifest全行hash复核不变。新client/daemon返回不解决旧35512/48945/17257 UNKNOWN，也不证明host全空闲。

## 原typed36与最终版本准确分层

原coder单typed JVM31592 UTC04:23:42.426171–04:23:42.908277、36组/原exit0及流保持；没有重放或改其原收据。独立比真实class：原比较集合21类中**19字节一致，2不一致为OriginalOwner与ScopeMeter**。OriginalOwner源hash未变但class字节不同，本审不猜字节差异原因，不把它说成显示字段修改；不能用19/21声明全部最终class已动态验。

原typecheck source-pins与最终源码有且仅两处文件差异：ExperimentJob增加currentIOPhase显示；ScopeMeter snapshot把静态INPUT/OUTPUT显示改为实际inputLimit/outputLimit。供审原版为**按原pin hash反向重建**的两文件，不冒当时保全原文件副本；本审独立验证重建hash和严格文本差异，未发现其他算法修改。ExperimentJob Android类本轮始终未执行。下面自身单JVM加载最终JAR的真实OriginalOwner/ScopeMeter等，补的是代表性有限最终政策门，仍不冒完整原36在最终DEX上重放。

## tester自有最终JAR有界验证

一个自有最小typed helper，一次javac+一次JVM、各heap256MiB，总**1.406秒**<30秒；全部typed字符串payload UTF8计301B<65536，Token为内存端口。javac38212 UTC04:49:14.996193–04:49:15.959894 exit0/stdout0/stderr0；JVM35756 UTC04:49:15.959894–04:49:16.363803 exit0/stdout4385/stderr0；原Popen自然返/两流关。原线程/latch由finally放门并同thread join，未反射改状态/interrupt/kill/注入永久阻塞；输入/最终JAR/签名文件结束hash不变。

45有限typed/政策组含：scopeAll唯一准入及十直接case拒；十历史界/不可变并发快照/部分失败不丢历史/UTF8界/所有pending-final emission累计；SDK4/native3/actual1、跨case copy/hash/seek/reopen/control共享界、EOF/unknown不退款、output short/unknown含copy累计、实际limit显示及并发原子预扣；raw/mux typed keeper在分配前登记，ALLOCATE/CALL/CLOSE在途都阻止提前归还/二close，异常原对象与allocationIntent保留；ADD_TRACK/SAMPLE/EMPTY_EOS错误后Sink已关仍不证明mux返回；同步真实E13 listener尾段未返无marker、单调deadline-1/等号/+1与晚观察不改变原事实、signal失败记录先于marker。

1个真实签名组核四APK（FIX02最终2+准确recovery01最终2），固定官方apksig9.3.3先核metadata SHA，全部verified/v2=true/同单cert5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。生产JAR在前，OriginalOwner/ScopeMeter/ScopeJournal/CompletionPoint/E13ReturnEvents逐CodeSource打印准确最终JAR；不加载ExperimentJob/Android Os/实际Media3 parser或mature muxer。不把45typed组加四个签名文件算成49个独立功能用例。

## 五项集中裁定

'''+ftext+'''

## 全scope与M2A01–48边界

唯一scopeAll十case/同Job/同worker/60秒保持。输入同ScopeMeter SDK readAt请求+copy/control/directEOF8MiB预扣；native attempt/actual/EOF/unknown独立，源调用点由已准入请求覆盖。nativeAttempt公开记录方法本身不是独立8MiB守门，结论依赖已审job/provider路径，不扩大为任意调用此记录器均安全。short3预声明Reader/readAt最多4、native chunk3，是该实际边界requested，不冒未观测的库上层requested。output request与attempt各16MiB含copy/controlled4/mux，partial continuation额外attempt也计，不拿extent代attempt，不退款/换factory重置。

known registered nativeFD峰值/active与asset-stream owner/source lease分开，原descriptor slot/keeper在open前登记，返回采用和关闭事实分开；AssetManager内部/全内核FD计数仍API_UNPROVEN。无FileOutputStream(fd) post-open平台包装/别名closer窗口；原Os原生返回未测，官方API参考只作类型/保守调用合同。muxer keeper先挂Job，再真实allocate/addTrack/sample/EOS/单close；cleanup/resourcesReturned都查原owner，不再让外Sink成功替原mux close。失败构造/close未知保管原意图/对象，不重建/二close。

MC-B01同grant/一次REOPEN/原writer-response-observer未返不sticky且不耗检查的旧修保持，TemporaryOutput仅新增phase薄传递；未重跑ContainerPendingOrderCheck或旧host大套。真实Media3 CSD实际数组/AnnexB20、sample规范化1340/hash/PTS/raw flags政策保持，hostraw1360不混；独立DTS仍UNPROVEN，不填PTS。六payload+空EOS4/1200000与fragment3000/copying仍源意图，真实SeekMap/TrackOutput重开duration必须证明，未实际执行不补绿。

independent-m2a01-m2a48-results.json对48原oracle给本B有限证据/平台NOT_RUN及前B备注，旧A的PREPARED_NOT_RUN不改。finalizer owner-at-receipt1与平台super.finish外返回、同原capture两流关分列；typed marker不等OS退出。全部真实格式/seek/时间戳/FDsync/原mux/fMP4/cancel各阶段/外finish仍需之后准确范围实证。

## 计划算术、未绑定与停止

准确6逻辑操作：fingerprint1、本APP/TEST存在性各1、准确新双APK各install1不-r、scopeAll instrumentation1。binary合计**7629605B**；命令每op4096/总24576，logical outbound**7654181B**；preflight786432/install131072/instrumentation所有pending-final两流1048576/controllerproof1048576，总logical inbound**3014656B**；receipt单status262144/全emission1048576/content196608。独立算术核对通过，没有把逻辑payload当ADB精确wire。

scope body60秒/outer wholewall90秒观察提案存在；观察到期只停后继/保管原worker/FD/capture，不kill/强关流/二close。scopeId、serial、freshIdle、captureTool仍null，真实transport/framing与具体工具预算需后续负责人绑定。清理只可在原返回后处理准确新自有文件，当前不自动删目录/uninstall/clear或重试。持续平板授权保持，无需重复向用户询问通用许可；本B仅离线，设备/ADB/5037/占用/安装/生成编码解码播放0，不能自行进入实机批。

## 过程与交接

三处tester静态审计准备修正已记录：首次shell引号使准备命令未执行；旧审计适配替换顺序把对照目录临时指向自身，声明差异校验立即拒；DEX断言沿旧已移除reserveInput/createNew名称，更新为真实ScopeMeter/RawWrite实现。都未改候选或产生JVM重跑，正式自有helper仅一次编译/一次JVM且通过。有限hash/ZIP/AXML/DEX/class/APK签名读取确实包含opaque媒体字节，不声称载荷零读取；无MP4/AVC/Media3解析，也不倒灌旧资格/未来设备8MiB账。apksig内部实际读量未单独计，不伪填0或精确总量。

完整报告、五门有限关闭、全48矩阵、874/JAR/DEX/消费/原返回、typed版本差异、自有helper原源class/流/owner/预算与旧保全一起冻结。发送收据在证据目录外，发送后不改。全部集中交负责人，不逐问题派修，不自动后续测试；没有自动审批拒绝或需要用户重复授权的动作。
'''
REPORT.write_text(text,encoding='utf-8');manifest={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall':'PASS_LIMITED_OFFLINE_FIVE_SOURCE_FIXES_ANDROID_NOT_RUN','report':REPORT.relative_to(R).as_posix(),'reportBytes':REPORT.stat().st_size,'reportSha256':sha(REPORT),'evidenceFiles':[pin(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json'],'fiveFindingClosure':'LIMITED_SOURCE_AND_FINAL_TYPED_GATES_ONLY','newConfirmedSourceBlockers':0,'independentGroups':46,'actualAndroidRuntime':0,'deviceOperations':0,'oldUnknownActions':0};save('review-evidence-manifest.json',manifest);print(json.dumps({'reportBytes':manifest['reportBytes'],'reportSha256':manifest['reportSha256'],'manifestSha256':sha(E/'review-evidence-manifest.json'),'evidenceFiles':len(manifest['evidenceFiles']),'overall':manifest['overall']}))
