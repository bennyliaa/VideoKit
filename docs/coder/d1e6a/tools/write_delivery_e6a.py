from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,text):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
a=load(B/'evidence/apk-audit.json');app,test=a['apks'];inputs=hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()
plan=load(R/'docs/coder/d1e6/tools/device_plan.json')
def convert(v):
 if isinstance(v,str):return v.replace('D1-20261017-E6','D1-20261017-E6A').replace('D1-E4A-E6-NORMAL','D1-E4A-E6A-NORMAL').replace('/d1e6/','/d1e6a/').replace('THIS_E6_TWO','THIS_E6A_TWO')
 if isinstance(v,list):return [convert(x) for x in v]
 if isinstance(v,dict):return {k:convert(x) for k,x in v.items()}
 return v
plan=convert(plan);plan['versionCode']=7;plan['versionName']='D1-E6A';plan['apks']=a['apks'];plan['state']='REVIEW_ONLY_NOT_DEVICE_PERMISSION'
plan['deployment']['argv']=[['-s','HA1Q6WXR','install','-r',app['path']],['-s','HA1Q6WXR','install','-r',test['path']]]
plan['requiredEvidence']+=['sourceNativeDiagnostic and validatorNativeDiagnostic have distinct scope/task/mode/phase. Source mode10 extraction counters are not output verifier mode11 counters. Source failure before verifier leaves validator exactly NOT_STARTED.','Known CREATE/TIMELINE/cancel-before-read failures explicitly start=NOT_STARTED; in-flight validation start=UNKNOWN until facts return. ENTERED is call entry, not process-start ACK.','A Java post-validation or stop/close failure keeps collected native snapshot as background. E6_NATIVE_OK alone never means overall READY; preserve original Java first error/type and separate cleanup.','Atomic first snapshot retained on duplicate/concurrent reject; no illegal pre-validation publication. Actual Android Binder behavior still needs execution, JVM boundary results are not a waiver.']
plan['nativeRebuild']=False;plan['diagnosticNativeSchema']='Unchanged E6 10ints+3longs; receiver publication/routing changed in Java only';plan['mediaOrExportReads']=0
put(B/'tools/device_plan.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
table='\n'.join('| '+x['role']+' | '+str(x['bytes'])+' | `'+x['sha256']+'` |' for x in a['apks'])
delivery=f'''# D1 E6A 完整交付 V1.0

2026-10-17。D1-20261017-E6A / versionCode7 / D1-E6A。集中修复E6-F01/F02/F03三个P2，实际共享生产边界20用例/112断言PASS、离线双APK构建与身份核验PASS。Android/JNI/Binder系统及正常回归NOT_RUN，不把本机结果当实机关闭问题。D1 NOT_PASSED、M0 NOT_STARTED、全P0及旧FAIL/框架许可保持。

## 三项修复

F01：E4CpuAdapter实际validate工作流在native await、stop、close、digest及实际PipelineValidationReceipt.prove/内容/thumbnail异常处，仍读取实际接收器首份snapshot并随E6AFailure携出。原Throwable作为primary/cause完整保留，cleanup按原顺序单列，不用native OK覆盖原Java错误。停止或close未实际返回时保留原verifier；不构造成功Verification，不做资源或预算信用重置。source同一所有权工作流也保原始异常和快照。

F02：source/validator分开task、role mode10/11、phase和专用报告字段。source.next失败只填sourceNativeDiagnostic，不再使用E6_VALIDATOR_REJECTED标签；validator尚未进入时严格NOT_STARTED。source成功也保实际source task/snapshot，validator成功保自身task/snapshot。已知CREATE/TIMELINE/BEFORE_READ失败明确start=NOT_STARTED，在途validation记录start=UNKNOWN；ENTERED只是开始调用相关入口，不是实际进程start ACK。源提取mode10的native accepted计数与mode11完整输出验收不混用。

F03：原Binder回调实际委托E6ADiagnosticInbox.receive完整接收边界，保原PID/UID/task/epoch/revoked/1024B鉴权、原数值schema、parse/end、stage与实际frame-count一致检查，全部完成后CAS原子发布首份合格snapshot。非法数据不占槽，重复/并发不能覆盖第一份；对象不可变、无reset接口，后续DONE/ERROR读同一首份。

## 有限本机证据

tools/E6ABoundarySelfCheck.java直接执行生产E4CpuAdapter.validate(ValidationOwner,...)和next(int,SourceOwner)共享工作流、真实PipelineValidationReceipt.prove/View及原PipelineRules内容/缩略图条件、完整生产receive及实际session scope路由组件。公开生产入口只封装真实CpuTaskClient平台操作并进入同一工作流；没有复制模型算法、test分支或成功豁免。测试只模拟start/stop/close/lifecycle事实与Context/Looper/Log基础API，不调用实际Android Binder/JNI或媒体。

20用例包括digest异常、实际receipt摘要不一致/未完成、真实内容及缩略图失败、stop false/throw、close throw、native首错+两cleanup、validator成功、实际source工作流失败→validator NOT_STARTED、已拥有资源的坏timeline/创建后取消窗口，以及完整receiver鉴权/size/revoked/字段/尾数据/stage/frame/重复/并发。16个并发receive仅1发布/15拒绝，首对象保留；非法首份后合法首份能占尚空的诊断槽。原协议对非法请求仍失败关闭，不表示容忍非法请求继续正常业务。最终20/112，记录evidence/local-check-results.json和boundary-run-005.log。

早期JVM001编译因自有Context shim缺少API签名停止；002通过18例，003补所有权窗口20/111，004补source成功归属20/112，005精确未启动状态20/112。全日志保留，未重跑旧E6的34或270/82历史套件，未重新读取E6媒体/回放件。不能把这些模拟平台事实当真实进程death/FD归还。

## 最终双APK与来源

| 角色 | 字节 | SHA-256 |
|---|---:|---|
{table}

仅用docs/coder/d1e6a/artifacts/D1-20261017-E6A/final。证书均 `{app['signerCertificateSha256']}`，原AppID、两私有服务及权限不变。sourceNativeDiagnostic/validatorNativeDiagnostic均确认进入最终app/test DEX，非源码空声明；本机test类不进APK。最终输入SHA `{inputs}`，repair-001绑定；main-001成功后最后核查补启动状态精确语义，必要一次修复也成功。首轮APK/签名/输入/理由/日志及build-results-before-repair-001保留冻结，最终只认final。

七native、native源码/header/config、JNI sender/schema、E6Muxer/E4CodecSink、原严格PipelineRules均逐字节同E6，本批native重建0、Maven35坐标锁不变/FFmpeg8.0.3/Media3 1.9.3不变、下载0。SBOM nativeDelta空、NOTICE-E6A及原E6/C14来源/完整对应源容器保留。最终ZIP16KiB对齐静态核验，不是Android16KiB实测或合规/漏洞放行。

## 冻结及下一步

开发原派发完整存docs/milestones/D1_E6A_CODER_REQUIREMENTS_V1.0.md，独立验收另存D1_E6A_TESTER_REQUIREMENTS_V1.0.md。四文档、精确diff/证据、SBOM/源码ZIP/freeze/只读verify整包交负责人复审；E6全部254不可变项只读复核PASS，无修改旧冻结。

本批设备/ADB/媒体源/导出件/新故障/下载均0。Guard/恢复/当前host实际观察/绝对deadline/原53651消费及失败输出保持。下一准确待审计划tools/device_plan.json：同签名保数据部署E6A→MP4→AVI→能力→仅本批两正常独立审证后条件cancel，稳定budget不变，不先部署E6，不新QUERY/ABORT。真实动作仍待正式派发。
'''
architecture='''# D1 E6A 架构及威胁边界 V1.0

2026-10-17。Java诊断所有权/归属/一次发布集中修复；native、封装、完整六帧/EOF/1000µs/画面及原资源门不改。

## F01：实际生产后置失败边界

E4CpuAdapter公开validate(Context,...)仍执行offMain/原timeline准入、原TrackedProvider及真实CpuTaskClient创建；平台适配器封装原verificationTimeline/start/awaitVerification(15000)/stopAndAwait(5000)/close、实际source归还检查及原retained verifier。随后进入同一package-private validate(ValidationOwner,...)完整生产工作流。该入口无测试模式判断，也没有可由Binder/Intent传入的Owner；外部公开入口固定真实平台适配器。

共享工作流顺序仍native→stop→close→digest→实际receipt/content，任何原第一错误保留，再尝试原收尾；首错phase保持，后续stop/close异常单列最多两份，原异常对象与cause不替换。stop false、stop throw或close未返回资格不完整时保留原verifier，不能因native OK构造成功结果。全部错误统一携带同一实际接收snapshot或NOT_COLLECTED；不会凭空补零。成功Verification只由原receipt严格证明构造。

PipelineValidationReceipt新增内部View适配，真实生产View仅转发原CpuTaskClient；证明体仍原verificationDone/orientation/death/source/slot/pendingCalls/stopPending/unresolvedWorkers/byte界/before-after摘要，以及真实PipelineRules.content、thumbnail长度/错误/帧映射/可辨识检查。测试通过有限平台View进入这个真实证明体，不以mock prove取代。接口均内部包级、没有新跨进程授权路径或产物READY豁免。

source.next同样共享实际所有权工作流，平台适配器保原真实解码/seek/像素/timebase/哈希/方向准入。创建后取消在已登记owner内拒绝并执行原收尾；坏timeline在已拥有validator时也必须收尾。source active/retained强保留原CPU对象；失败不会用替代close或重试UNKNOWN冒充归还。创建失败的原CpuTaskClient自身清理/隔离逻辑不变。

## F02：作用域与启动事实

E6AFailure包括scope、实际task或NOT_CREATED、role mode10/11、phase、原primary/cause、单列cleanup及实际snapshot引用。公开metadata只用本地安全短码/异常类型/固定字段，不泄露路径凭据；内部Throwable原对象仍保留。background里的E6_NATIVE_OK只说明native状态，不替代Java内容/收尾和session READY。

E4Session实际catch委托E6ADiagnosticState.failure，不再把任意含native的cause记到validator；SOURCE只填sourceNativeDiagnostic。每源frame成功也登记实际source task/snapshot；validator进入前严格NOT_STARTED，进入后尚无事实时start UNKNOWN，实际成功后本task/mode11/VERIFIED。CREATE/TIMELINE/BEFORE_READ是已知未进入native调用，明确start NOT_STARTED；其他ENTERED是该调用路径已进入，不能拿它当进程start ACK。全局session.first仍原compareAndSet，取消或更早全局错误不被模块背景替换；cleanupError原独立字段保持。

两个完整字段均通过原instrumentation HOST_DIAGNOSTICS白名单，实际最终app/test DEX有键。字段由有限模式/32hex task/phase、安全code/type、最多两cleanup与原有限native数值生成；保持原单字段1400/记录4096界。没有snapshot用NOT_COLLECTED，未启动用NOT_STARTED，不转成虚假零计数。

## F03：完整接收边界与原子性

原CpuTaskClient Binder最外层保原真实caller/task/epoch/revoked/parcel上限，分支再将真实caller/context/原parcel size/数值parse及CpuProtocol.end委托E6ADiagnosticInbox.receive。该生产方法自身再校验鉴权/size，随后创建同一E6NativeDiagnostic并检尾、stage与VERIFY帧数一致，最后AtomicReference.compareAndSet(null,d)。所有验证先于发布；错误首份不能占槽；只有第一份合格对象可发布，后续失败不覆盖。DTO仍不可变，接收器无清除/重置方法，getter及DONE/ERROR统一读首份。

原协议非法回调依然可触发业务失败/收尾；CAS空槽未被非法数据抢占不是业务继续许可。新增本机并发证据只证明同生产接收方法的内存发布/协议验证，不声称真实Android Binder线程调度已实测。

## 本机证明与未覆盖

20直接边界用例/112断言。F01真实validate/receipt内容和后置/收尾分支，F02真实next失败与实际session routing组件，F03完整receive（不是仅CAS helper）。16线程同时调用同一生产receive，1发布/15重复拒绝，第一对象保持；此前错PID/UID/task/epoch/size/revoked、非法字段、尾数据、阶段和帧数均不占槽。

平台start/stop/close/lifecycle、Context/Looper/Log由自有有限shim模拟；真实Android bind方法在shim中直接抛错，不能暗中伪造系统操作。生产纯规则及每个变化边界从E6A源重新编译，未改的Android支持类型只用既有E6 classes，未运行设备/JNI/真实Binder/媒体或导出件。单个模拟receipt/death事实不能对外充当实机验收；实际每host观察、真实FD/owner/slot/CPU死亡归还仍由原生产链取得。

E6Muxer和E4CodecSink、PipelineRules、guard/recovery/Admission/Lifecycle/Budget与相关native/schema保持字节。原2MiB输出/64MiB与8192readAt/六帧/1000us/完整EOF/thumb/内容/映射、60s/首次cancel30s/真实owner终局不变。无新native构建/依赖/权限/白名单；旧E6、旧FAIL/原N2 closeACKfalse、结算R/S0/53651消费均不动。
'''
gates='''# D1 E6A 剩余门复审 V1.0

2026-10-17。

| 项 | 本批结果 | 后续门 |
|---|---|---|
| E6-F01/P2 | 实际validate/receipt内容/thumbnail/stop/close错误保原首错、cleanup及已收native背景；直接本机边界支持 | 独立源码/证据审查，实际Android失败链仍未执行 |
| E6-F02/P2 | 来源及validator task/mode/phase/字段分开，未进入NOT_STARTED，在途UNKNOWN，真实next错误负例支持 | 实际回归核两个完整字段；不把source accepted0/EOF0当validator结果 |
| E6-F03/P2 | 原完整receiver先验证再CAS首份，非法不占槽；16调用1发布15拒绝/首份保留 | 实际Android/Binder仍待另派，协议失败不得豁免 |
| E5C-REG-F01/P1 | E6已支持的封装/严格验证修复原字节保持，未新运行媒体回放 | 新E6A正常MP4完整READY才可能实机关闭，旧FAIL不改 |
| native/依赖/16KiB | 7native及源/header/config/ABI/35Maven完全继承E6，无重建下载；ZIP静态核验 | 不作Android16KiB实际或许可/漏洞放行 |
| 原N2/53651预算/当前host观察 | 原结算及消费、失败产物、无pending事实沿旧报告保持 | 每新host实际观察和原资源/预算门，不新ABORT/清账/换UUID |
| 正常MP4→AVI→能力→条件cancel | 本批设备NOT_RUN | 独立复审后准确派发E6A；cancel需本批两正常独立报告SHA |
| 全P0/正式Flutter/独立Kit/框架许可/旧signal | 原未完成/未通过保持 | 原验收与许可不变 |
| D1/M0 | NOT_PASSED/NOT_STARTED | 不宣称debug包是项目正式交付完成 |

20项边界是模拟平台下直接生产Java方法证据；不能替代Android JNI/真实Binder/MediaCodec/真源/FD/owner实证，也不累计成已重跑原34/270/82项。源码/产物/数据不漂移测试。任何缺证、FAIL/PENDING/UNKNOWN、内容/EOF/资源/时限不符必须停止保留，不弱期望、延时、重试、删产物或预算信用重置。
'''
appendix='''# D1 E6A 设备执行附录 V1.0

2026-10-17。待负责人独立复审后正式派发；本文件及tools/device_plan.json不是设备执行许可。本次coder无ADB/设备/媒体源/导出件操作。

仅原HA1Q6WXR/user0、AppUID10221/test10222，同原证书。核E6A外seal/ZIP/最终双APK/hash/版本7，再app/test依次install-r保数据；不得先部署旧E6、不卸载/clear/降级/改账户/force-stop/重跑一次性G01根。原53651消费/失败输出、原N2结算及fixture连续性只按正式批次有限预检，不重读全部媒体hash。

准确四单方法/独立新host：com.videokit.spike.e4.E4DeviceTests#normalMp4SixRealFrames → #normalAviSixRealFrames → #capabilityDenialDoesNotOpenSource → 条件#cancelRejectsWrongEpochOversizeAndLateFrame。每次class#method与e4Case一致，不选整个fault类。e4Batch=D1-E4A-E6A-NORMAL-TABLET-20261017，e4BudgetIdentity=730a73e1-50e1-4198-a515-047104f00e31，e5aObservation=REVIEWED_ORIGINAL_N2_SETTLEMENT，e5aSettlementReceiptSha256=5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962。每个@Before仍实际执行当前host原最终观察，不能用旧live proof/报告代替；原recoveryBatch保持D1-E5B-N2-RECOVERY-20261017，无新QUERY/ABORT/独立OBSERVE。

正常需真实6源/6输入/6samples/完整isolated6输出、原timeline/1000us/EOF/thumbnail/content/mapping/READY、实际CPU/源/codec/FD/slot/CONTROL/owner终局和唯一R/S/无pending。完整validatorNativeDiagnostic必须scope VALIDATOR、本validator task、mode11、phaseVERIFIED及原E6_NATIVE_OK/site0/accepted6/双EOF1/drain1/真实readAt与字节；sourceNativeDiagnostic是另一个source task/mode10/frame阶段，其提取计数不混为完整输出验证。源错误前validator NOT_STARTED；创建/坏timeline/读前取消是已知start NOT_STARTED，在途UNKNOWN不冒actual started ACK。

任何Java后置/收尾失败仍记录原primary/type和cleanup，已收native snapshot仅背景，即使E6_NATIVE_OK也不能判READY。NOT_COLLECTED不是零；源诊断不得填验证器拒绝。协议非法/重复/并发错误仍按失败停止，首份保留不表示继续业务许可。

MP4失败即停AVI/后续，AVI失败即停后续；条件cancel仅本批同设备两正常完整结果独立审证后，e4NormalReceiptSha256占位符替换为该新报告准确SHA，不能用旧正常/交付SHA或任意64字串。能力拒绝仍不读源且实际归还；失败不自动重试/后续/新故障。

原产品60s/首次cancel30s、原协商12s/STARTED15s、每CPU8192readAt/64MiB、每输出2MiB/至多3digest合计6MiB、每方法4MiB日志及原累计budget界保持。53651旧消费与失败产物不删，pending或额度不足是停止理由，不能清账/换UUID。无Gradle/设备/媒体并发。完成集中报告，不自动M0。

交审应先读四文档、reference需求/原E6审查、source-derivation精确diff、local-check-results及005原日志、integration-static-check、native-and-strict-logic-inheritance、SBOM差异、build/APK审计及包外readonly回执。tools/e6a_package.py verify只读核当前候选，不运行测试/媒体；本机boundary runner显式运行且冻结后拒绝变更。完整ZIP含E6A源/config/native/来源/原完整C14对应源容器/证据，无私钥、local.properties、构建缓存、class或媒体；自备既有SDK/缓存可按原Gradle配方在独立工作副本构建，不重建/篡改已冻结候选。
'''
for suffix,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',gates),('DEVICE_EXECUTION_APPENDIX',appendix)]:put(R/f'docs/coder/D1_E6A_{suffix}_V1.0.md',text)
print('E6A four documents and exact review-only next normal plan written')
