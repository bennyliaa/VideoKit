"""Write the requested four delivery documents and a non-executing review plan."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def load(n):return json.loads((B/'evidence'/n).read_text(encoding='utf-8'))
def write(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
def main():
 if (B/'evidence/e7-freeze.json').exists():raise RuntimeError('FROZEN')
 audit=load('apk-audit.json');checks=load('local-check-results.json');derivation=load('source-derivation.json')
 apk='\n'.join(f"- {a['role']}：`{a['path']}`，{a['bytes']} B，SHA256 `{a['sha256']}`。" for a in audit['apks'])
 changed='\n'.join('- `'+p+'`' for p in derivation['changedOrNew'])
 base='D:/CodexProjects/VideoKit/docs/coder/d1e7'
 delivery=f'''# D1 E7 交付 V1.0

2026-10-17。候选 D1-20261017-E7，versionCode9 / D1-E7。E6B-OBS-F01 保持 OPEN；本批交付实际生产死亡门的有界诊断、专用只读设备入口，以及明确停止在设计的持久协议。未声称长期新 host 准入已解决，未安排恢复写入或正常 AVI 重跑。

E6B_NORMAL 已独立审证平板 MP4：真实6源/6输入/6samples/isolated6、READY、PTS无漂移、双EOF、画面/缩略图、全部实际资源归还及唯一 S53567 通过，仅关闭 E5C-REG-F01 原平板 MP4 范围。AVI 新 host 在 Before WRITER_DEATH 阻断；能力与 cancel 未跑。原日志没有历史列表条数、匹配数或 reason，故具体淘汰/PID复用原因 UNKNOWN。

生产 requireRecoveryWriterDead 直接调用 E7WriterDeathGate；仍一次查询 max8，PID/UID/process/时间的匹配先计数，唯一且 reason>0 才查 /proc，只有 ENOENT 视为当前缺席。现在用查询前固定 now 作保守上限。错误码不放宽，观察/guard/fence/账本/文件 force 和实际 close/资源归还仍在原链路。新增报告有返回/匹配/各谓词拒绝数量、唯一匹配的 timestamp/reason/status、查询和 proc 实际状态；未查询/不可用用 NOT_COLLECTED，不补0。没有无关进程的身份/时间/错误正文。

持久死亡事实当前 DISABLED：旧 recovery.owner 只记 PID/UID/process/attempt/墙钟 began，没有 boot epoch 或 kernel process birth generation。已有成功日志无法补回可靠启动代次，也没有可证明的防回滚/篡改信任根；本批不实现持久文件格式、解析器、写入、迁移或 fallback。完整设计与风险矩阵见架构文档。每个新 host 仍必须通过当前原观察；历史成功文件不构成 live proof。

本地生产 gate {checks['productionGateCases']} 场景/{checks['assertions']} 断言通过；仅替换 Android history/proc port，直接调用同一生产谓词，未复制模型。测试不代表 Android API 实测。main-001 离线双 APK 一次构建成功（39秒，无修复/下载），原 guard/owner/观察/准入/资源/预算等10个关键文件逐字节保持。原 E6B 全191项只读复核通过。

{apk}

两个 APK 证书 SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。单 app、2个原非导出服务、无 INTERNET；app/test DEX 分别核新生产 gate 和只读入口。APK zipalign -P16 静态通过，7个 native 与 E6B 完全一致，非16KiB设备实测。35 Maven坐标、FFmpeg8.0.3/Media3 1.9.3、原native对应源/配置/许可材料保持；全部许可P0未关闭。

准确输入快照 `evidence/final-build-inputs.json` SHA256 `{hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()}`，绑定 build-results 最终通过尝试。SBOM/diff/逐文件来源/日志均归档。完整源码 ZIP 及包外 seal 位于 artifacts/D1-20261017-E7 和 evidence/e7-freeze.json；它们的最终 SHA 由独立包外 `docs/coder/D1_E7_READONLY_VERIFICATION_V1.0.json` 给出，避免自指。ZIP 不含私钥/local.properties/classes/cache/真实媒体；包含继承的完整 native 对应源容器。

相对 E6B 的全部构建输入变化：

{changed}

原稳定 budget 累计消费107218/reserved0、原N2归档/输出均按最后 tester 实证保留；本批没有设备访问，不能声称刚刚重新测得这些数。E3一次性许可已消耗不再复用。D1未过/M0未启，历史signal门与其余P0保持。本次无ADB/设备/媒体源/导出件/下载/新增恢复写操作。后续仅在独立静态复审及负责人正式派发后，执行附录的单个只读诊断；其结果也不是正常流程准入许可。
'''
 architecture='''# D1 E7 架构与威胁边界 V1.0

2026-10-17。结论：生产诊断已实现；持久死亡事实协议 DESIGN_BLOCKED_MISSING_TRUSTED_WRITER_GENERATION，没有可用持久准入实现。E6B-OBS-F01/P1未关闭。

现有证据精确区分三道门：首先原 App/独立空闲 host 身份，再 system exit history 的 PID/realUID/process/timestamp 匹配及正 reason，最后 /proc/PID 的 lstat。E6B AVI 的 E5A_RECOVERY_WRITER_DEATH_UNPROVEN 在第二道门，尚未到 proc；错误可以是非唯一匹配或非正 reason，旧日志无法区分。不能据此认定 API 淘汰或 PID 复用。

Android 官方说明此 API 是有限最近记录的环形历史，pid与maxNum为查询条件，不提供永久保存保证；本批没有设备证据证明这次条目被淘汰。[ActivityManager官方API](https://developer.android.com/reference/android/app/ActivityManager#getHistoricalProcessExitReasons(java.lang.String,int,int))。[ApplicationExitInfo官方API](https://developer.android.com/reference/android/app/ApplicationExitInfo) 的 UNKNOWN reason 为0，不能作为已证原因。setProcessStateSummary 针对调用进程，不能回写旧 writer 身份。

实际代码边界：E5N2RecoveryAndroid 只把 Android 行映射为最多8条纯字段，超过上限直接 OVER_BUDGET，不遍历更多条。E7WriterDeathGate 是唯一新生产谓词，直接用于原 requireRecoveryWriterDead；Report 不是 E5AAdmission.Proof，没有授予准入的方法或持久状态。一次查询，不自动重试，不改 maxNum，不读上次报告。查询前固定 now 较原逐行取 now 更保守；其余身份/时间包含边界、重复判断、reason>0、仅 ENOENT 允许等条件保持。原较早 N2 host/codec death()、同步目录 barrier、existingGuard 逐字节业务体保持。

结构诊断 schema1：history=NOT_REQUESTED/AVAILABLE/UNAVAILABLE/MALFORMED/OVER_BUDGET；returned 是真实API返回条数，只有已取得列表才有值；matches 是 PID/UID/process/时间全部满足的条数。rejectPid/rejectUid/rejectProcess/rejectBeforeOwner/rejectFuture 可重叠；reasonNonPositive 仅在身份/时间全匹配行计数，先算匹配数再考虑 reason。唯一匹配才输出其 timestamp/reason/status。没有无关行明细或异常正文。proc=NOT_REQUESTED/ABSENT/EXISTS/UNAVAILABLE，EXISTS只表示仍可见或可能复用，报告始终 pidReuse=NOT_PROVEN/reboot=NOT_PROVEN。报告最长按有限固定字段 <1400字符；旧证据最多2048字符，加固定expected owner字段总量低于4096。不可用/尚未查询的计数 NOT_COLLECTED，不能当0。未知 old owner 解析失败仍停在原WRITER_DEATH，不制造后续证据。

专用 E7WriterDeathDiagnosticTests 是单独测试类，不继承原 @Before 观察。固定只读 recovery.owner，逐级 lstat 目录、O_RDONLY/O_NOFOLLOW/O_NONBLOCK、fstat原文件UID/角色/大小/dev+inode、最多257B拒超256、精确固定owner原始字节、打开前后元数据比较，原 E4Owned 在 open 前保留。实际 close 返回才报 returned；原Job静态强保留，10秒只停止等待，不取消/重开/强制清理，在途保持PENDING并停止批次。只读会有操作系统读取访问时间等常规读副作用，不写业务状态。然后仅调用同一 requireRecoveryWriterDead：拒绝也可成为成功收集的诊断，但不是观察或产品成功。没有 observe、guard/账本改写、force、sync、媒体、CPU、service、READY或授权授予操作。

长期协议所缺的依据：旧 owner=attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f/PID4869/UID10221/com.videokit.app/began1792224193301，旧exit1792224193337/reason10/status0仅是已有历史观察。旧V1没有bootID/kernel start ticks/可验证创建代次；墙钟和PID可重复，nonce也没有绑定内核代次。当前/proc缺席不能补证此前未复用，记录不存在不能区分淘汰、重启或查询不可用。旧成功日志、receipt SHA、同UID签名、应用内自签/HMAC或本地标记本身都不是额外可信死亡来源，不能解决同UID篡改/回滚或旧记录缺失代次。

未来V2仅为设计约束，未实现任何可被读取的格式：必须在未来writer开始任何恢复写前，以受支持、实测可用且能验证的来源，将boot epoch、内核start代次、UID/process、attempt nonce精确绑定；同时绑定不可变task/epoch/generation/service/budget/guard的dev+inode和旧fence/账本原始承诺。证据获取者必须证明是这个启动代次的实际死亡，持久化的授权与完整性/单调防回滚信任边界须独立审定。只有原持久owner真正写入/force/close/目录屏障返回且读回一致才可能记录已提交事实，在途、缺ACK、部分写和不确定提交一律不能声称完成；事实只描述旧writer死亡，不代替新host资源归还。

若未来协议获准，每新host仍必须重新核当前原guard角色与精确dev/inode、独占lease实际获得、旧新fence、完整账本及文件绑定、预算无pending、所有相关原持有者实际close/同步返回；不得从持久事实推导旧sync或closeACK。当前V1 writer缺失代次的迁移需要独立可信外部证据或正式安全处置方案，不能在读取日志后补造V2。新设备只读诊断也未必能补足此缺口，因此不能承诺诊断后自动解锁。

风险与本批真实覆盖：

|风险|实际生产 gate / 测试结果或明确缺口|
|---|---|
|历史缺失/重复|0条/2条匹配均拒绝，重复中一条UNKNOWN仍拒绝；直接生产测试|
|UNKNOWN/负reason|唯一匹配reason<=0拒绝，不进入proc；直接生产测试|
|错PID/UID/进程/前于owner/未来时间|分别计数拒绝，无无关行泄露；直接生产测试|
|API不可用/null/损坏/超8|未取得计数NOT_COLLECTED，空列表与未知分开，拒绝且不查proc；直接生产测试|
|proc可见、不可用、异常、null|只有ABSENT通过；可见不能断言PID复用；直接生产port测试，非Android实测|
|PID复用后又死亡/跨重启|V1无法证明启动代次，报告NOT_PROVEN；未伪造Android复用/重启实验，持久准入禁用|
|旧成功在新host重放|上一Report不会被读取替代当前查询，下一次缺历史仍拒绝；直接生产测试|
|持久记录损坏/重复/过期/缺失/伪签/回滚|本批没有持久死亡事实读写入口，均不能触发任何grant；没有虚构解析器测试。未来须定长严格编码/唯一记录/完整性/精确代次及绑定/单调新鲜度策略全部验证，任何未知拒绝|
|持久提交或资源close在途|不实现/不消费该记录。未来PREPARED/部分写/无原owner实际返回不等于COMMITTED。原观察资源边界字节保持，专用只读FD在途保留；Android在途注入未执行|
|旧live proof/旧closeACK替代当前资源|E5AFinalObservation/E5AAdmission/Guard/Budget等保持原字节，只有其原当前host整链路可能准入；本批diagnostic没有grant|

本地27场景316断言只覆盖生产纯gate及端口返回值；不是对Android真实API、跨重启、持久协议、专用FD在途或设备资源归还的实测。原E6B/E6A已接受边界为继承未重跑，精确来源和输入可复核。所有native/许可/历史signal/原预算安全性质保持。
'''
 review='''# D1 E7 剩余门槛复审 V1.0

2026-10-17。请求独立静态复审整个批次后，由负责人决定是否正式派发只读设备诊断。当前不提供任何一次性真实执行许可，不复用已耗E3许可。

|项目|本批状态与依据|
|---|---|
|E6B-OBS-F01/P1 每新host持续可审准入|OPEN；结构诊断完成，可靠持久协议设计阻塞，未提供长期准入|
|实际生产诊断|本地27场景316断言PASS；唯一匹配/正reason/proc门保持；Android适配器与独立只读入口均编译，Android NOT_RUN|
|旧 E5C-REG-F01|仅E6B_NORMAL平板MP4真实6/6/6/6 READY/PTS0/双EOF/画面/全部资源/唯一S53567限定关闭；不扩大至AVI或其他设备|
|AVI正常|E6B Before WRITER_DEATH未证；根因谓词UNKNOWN；E7不重跑|
|能力拒绝与cancel|NOT_RUN，cancel前两正常完整同批独立审证条件尚未成立|
|原N2结算/安全性质|原guard/观察/准入/owner/账本/资源边界不放宽；最后tester消费107218/reserved0，所有原产物保留，未重新测量|
|构建与来源|一次39秒离线双APK、同原证书、version9；7native和35依赖不变；E6B191只读PASS；源码/diff/输入/SBOM/外seal/ZIP可核|
|D1/M0/历史signal/许可全P0|D1未过/M0未启，历史signal未改；所有既定许可/平台/设备/16KiB实测与余下P0继续保持，不以诊断通过替代|

tester应独立核对 production gate 确实从 Android requireRecoveryWriterDead 调用，原错误拒绝无绕过；API最多一次max8/无重试，计数未采集与0分明，无关process/异常正文不进入输出；匹配先于reason、仅ENOENT可通过。核对Report不是Proof、没有持久事实缓存/解析入口、原观察全链条及实际资源归还仍必要。

核对只读入口 class#method/参数、固定owner精确字节、路径UID/角色/noFollow/读界/原FD持有者/实际close/10秒PENDING保留；确认没有调用observe或任何新恢复写/CPU/服务/媒体。该方法的JUnit PASS只代表诊断被收集，可带BLOCKED_CURRENT_GATE；不等于当前历史证据合格，更不等于FRESH_OBSERVATION_ADMITTED。

精确审阅 source-derivation/diffs、输入与build关联、local-check-results原始日志、APK signer/aapt/zipalign/DEX、SBOM/native来源、reference原始AVI/MP4日志及独立报告、freeze和包外只读receipt。持久协议风险项明确为NOT_IMPLEMENTED/不能准入，不得登记为模拟通过。

需要负责人后续决策的实际缺口：能否取得旧writer精确启动代次及可信死亡来源、防回滚的外部保证；若无法取得，则必须正式设计旧V1安全迁移/处置，不能自动重写原档案。仅增加历史limit、同host重试、复用receipt、移除死亡门都不满足要求。现阶段仅可派发一次只读诊断，不串接正常/能力/cancel。
'''
 appendix='''# D1 E7 设备执行附录 V1.0

2026-10-17。本批coder未连接设备；下列是待独立复审后由负责人正式派发的计划，不是许可或已执行记录。所有正常/能力/cancel仍BLOCKED，不自动串行恢复。

仅原平板 HA1Q6WXR / user0 / App UID10221、test UID10222；独立核包外seal、源码ZIP、双APK hash/原证书、versionCode9/D1-E7。新只读入口编译在test APK中，若负责人正式派发，再由tester按保留数据的同签名 install-r 部署app/test；不得卸载/clear/降级/force-stop/删档/换budget。部署会更新应用包，故它也须纳入正式设备派发；当前未执行。

精确唯一方法 `com.videokit.spike.e4.E7WriterDeathDiagnosticTests#originalRecoveryWriterReadOnly`，runner `androidx.test.runner.AndroidJUnitRunner`，target test package `com.videokit.app.test`。参数 e7Case=originalRecoveryWriterReadOnly；e7Batch=D1-E7-WRITER-DIAG-TABLET-20261017；e7Scope=READ_ONLY_NO_ADMISSION。不选E4DeviceTests，不带e5aObservation，不运行任何@Before原观察，不增QUERY/ABORT/独立结算。

固定元数据 `files/e4a_output_budget/N2-e5-recovery/recovery.owner`，精确V1 owner tuple见架构文档；最多256B内容+1B超限哨兵。仅固定owner元数据和系统退出历史/proc，历史query一次max8；原FD在open前保留，NOFOLLOW/NONBLOCK/只读/逐级目录角色UID、文件dev/inode/大小/时间校验，实际close返回。新线程原owner最多等10秒，超时记录PENDING但不取消、重试或声称资源释放，立即停止批次保留现场。诊断metadata日志外部上限1MiB，不读取媒体源/失败导出/任何真实视频，不启动CPU/codec，不force/sync/改ledger/归档。

原稳定budget identity=730a73e1-50e1-4198-a515-047104f00e31、累计消费107218/reserved0与全部原产物按最后tester证据保留；tester可沿已批准只读元数据清单对账，不能读媒体体或新写恢复。原恢复batch D1-E5B-N2-RECOVERY-20261017不变，不重新使用旧执行许可。若UID、owner字节、身份、资源状态或任何记录不符，停止保留，不修改为预期值。

收集原instrumentation stdout/exitcode/精确单方法收据与结构化E7_READ_ONLY：history状态、limit、returned、matches、各reject计数、唯一匹配timestamp/reason/status、proc状态、ownerFdReturned、admission=NONE。不得将NOT_COLLECTED补0，不得把BLOCKED_CURRENT_GATE当产品失败已修复或把JUnit PASS当死亡证据通过。没有匹配时根因仍须按实际字段陈述；可见/proc未知都不能断言PID复用，缺历史也不能断言淘汰或重启。

本次诊断完成即归档交负责人，不启动normalAVI/能力/cancel，不重新跑已通过MP4，不以诊断Report替代下一host当前原观察。若结果提供足够新证据，也需独立复审新协议及精确设备计划后再派发；若仍缺启动代次/可信持久保证，继续设计阻塞。任何FAIL/PENDING/UNKNOWN不强制清理、不重试。

`tools/e7_package.py verify`为冻结包只读核验入口；`tools/run_gate_checks.py`默认INSPECT且冻结后拒绝测试写，`tools/build_local.ps1`默认INSPECT且冻结后拒绝构建。独立复现应从完整源码ZIP解至新目录，自备原已缓存SDK/JDK/依赖及签名环境，保持离线，不改冻结候选；ZIP不含设备/私钥/真实媒体/local.properties/build cache。
'''
 for suffix,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',review),('DEVICE_EXECUTION_APPENDIX',appendix)]:write(R/('docs/coder/D1_E7_'+suffix+'_V1.0.md'),text)
 plan=dict(schema=1,candidateId='D1-20261017-E7',state='STATIC_REVIEW_REQUIRED_NOT_EXECUTION_PERMISSION',serial='HA1Q6WXR',user=0,appUid=10221,testUid=10222,versionCode=9,versionName='D1-E7',apks=audit['apks'],deployment='ONLY_AFTER_NEW_FORMAL_DISPATCH_SAME_SIGNER_INSTALL_R_PRESERVE_DATA',runner='androidx.test.runner.AndroidJUnitRunner',testPackage='com.videokit.app.test',method='com.videokit.spike.e4.E7WriterDeathDiagnosticTests#originalRecoveryWriterReadOnly',arguments=dict(e7Case='originalRecoveryWriterReadOnly',e7Batch='D1-E7-WRITER-DIAG-TABLET-20261017',e7Scope='READ_ONLY_NO_ADMISSION'),historyCallsMax=1,historyLimit=8,ownerReadMaxBytes=257,hostAwaitSeconds=10,onTimeout='PENDING_RETAIN_ORIGINAL_OWNER_STOP_NO_CANCEL_NO_RETRY',logMaxBytes=1048576,mediaReads=0,recoveryWrites=0,admission='NONE',persistentProtocol='DISABLED_DESIGN_ONLY',afterDiagnostic='ARCHIVE_AND_REVIEW_STOP_NO_NORMAL_CHAIN',budgetIdentity='730a73e1-50e1-4198-a515-047104f00e31',lastTesterConsumption=107218,lastTesterReserved=0,newlyObservedBudget=False,E3Permit='CONSUMED_NEVER_REUSE',D1='NOT_PASSED',M0='NOT_STARTED')
 write(B/'tools/device_plan.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 consistency=dict(schema=1,status='PASS',claims=dict(localGateCases=checks['productionGateCases'],localAssertions=checks['assertions'],androidExecution='NOT_RUN',persistentProtocol='DISABLED_DESIGN_BLOCKED',E6B_OBS_F01='OPEN',MP4='PRIOR_E6B_NORMAL_TABLET_ONLY_PASS',AVI='BEFORE_WRITER_DEATH_UNPROVEN',capability='NOT_RUN',cancel='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',deviceCalls=0,mediaReads=0),apkRowsMatchAudit=True,plan='tools/device_plan.json',documents=4,sourceZipAndSeal='External receipt authoritative; no self-reference')
 write(B/'evidence/delivery-consistency.json',json.dumps(consistency,ensure_ascii=False,indent=2)+'\n')
 print('Written four E7 docs and review-only plan; no device execution')
if __name__=='__main__':main()
