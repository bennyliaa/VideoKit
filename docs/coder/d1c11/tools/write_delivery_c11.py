from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parents[4];base=root/'docs/coder/d1c11';e=base/'evidence'
assert not (e/'freeze-summary.json').exists(),'Frozen documents cannot be regenerated'
review=json.loads((e/'candidate-self-review.json').read_text(encoding='utf-8'));plan=json.loads((base/'tools/device_plan.json').read_text(encoding='utf-8'))
apks=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks'];integrity=json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))
def save(name,text):(root/'docs/coder'/name).write_text(text,encoding='utf-8')
table='\n'.join('| '+r['file']+' | '+str(r['bytes'])+' | `'+r['sha256']+'` |' for r in apks)
save('D1_DELIVERY_D1-20261016-C11.md',f'''# D1-20261016-C11 整批交付

2026-10-16。状态：READY_FOR_COORDINATED_DEVICE_TEST / D1_NOT_PASSED。无Git仓库，git_commit=null；源ZIP、逐文件SHA256与冻结摘要是本批身份。只完成本机修复、编译和自审，未执行设备/ADB。D1未通过，不进入M0。

## 修复与验收边界

正式输入为 D1_C11_CODER_REQUIREMENTS_V1.0 和 D1_C10_TEST_REPORT_V1.0，原文保存在 evidence/input-*。对齐 C10-T01（status0退出取证缺口）、C10-T02（重连身份/死亡混用）、C10-ENV01（手机系统禁用）。C10原两项FAIL和平板38/2、手机40环境阻断不改写。

- C10-T02：首次Binder/PID/UID固定；每worker独立代次、HELLO、STOP及死亡状态。onBind在发布Binder前登记内核PID/UID和端点，捕获被系统重建但连接回调被解绑丢弃的端点。终态不重新START，旧death不能给新端点证明死亡；额外端点只认证/撤销，持有原槽直到实际死亡和全部调用返回。首次死亡尽早异步解除原自动创建绑定；unbind从未当作死亡证明。
- CPU仍最多2个解码任务。MAX_WORKERS=4仅为每task历史/异常控制端点记录上限，额外端点没有START、broker、Source token或FFmpeg配额；超限永久quarantine，不允许2×4解码。逐代次、全局未知worker及槽预算另记账。
- C10-T01：status0也采集App trace，原始系统reason/status与trace身份/信号/来源/读取/匹配/最终判定分栏。CPU进程名来自首次HELLO；trace还验证原任务时间窗。最多3条流、262144字节上限；主线程拒绝，阻塞保持真实pending，关闭失败保留流及采集容量。**系统signal0始终UNKNOWN/FAIL，即使trace声明11；不引入外部raw或ARMED作为产品证明。**
- 原输出验证、Source bridge、Media3、FFmpeg8.0.3、白名单与配额行为不变。legacy共享退出取证变得更保守；冲突/错身份/坏trace不能放行。没有把companion改成产品方案，正式Flutter/独立Kit方向不变。

实现及未证限制见 [取证设计](D1_C11_EXIT_EVIDENCE_DESIGN_V1.0.md)、[缺陷矩阵](D1_C11_DEFECT_MATRIX_V1.0.md)、[设备附录](D1_C11_DEVICE_APPENDIX_V1.0.md)、[许可准入](D1_C11_LICENSE_BUILD_ADMISSION_V1.0.md)。真实Binder竞态、系统重建和OEM trace可见性仍未实测；不能把模型测试当设备闭合。

## 本机结果

{review['jvm_assertions']} JVM断言（含代次163、共享trace实际输入流42及原有293）＋{review['script_assertions']}脚本断言，共{review['total_local_assertions']}，全部通过；计数从本批实际日志生成。JVM进程/锁及模型不证明Android行为。12个JVM入口、2个脚本守卫入口见local-check-results及candidate-self-review。

NDK/API31 CPU/lease JNI编译、完整Android主/测试/legacy-worker/Release集中编译通过。构建仅assemble任务，未connected/managed/ADB。初始NDK临时目录与Gradle缓存锁遇本机沙箱限制，前者改用本候选outputs临时目录，后者经工具审批执行离线构建；未改权限/依赖/设备门禁。源码/实际class时间与hash绑定见build-source-binding.json。

APK manifest/DEX/JNI descriptor/签名/zipalign/ELF/源码等价校验通过；三Debug同证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。七项自有原生库与打包内容一致，继承四ABI AndroidX库独立核对；16KiB静态对齐不是16KiB设备运行。Release仍与C07/C10对照逐字节一致，无C11类/服务/库/notice。

| 产物 | 字节 | SHA256 |
|---|---:|---|
{table}

全部产物：`docs/coder/d1c11/artifacts/D1-20261016-C11/`。正式source ZIP另在freeze-summary中给出hash；避免自引用，冻结摘要与ZIP身份回执在freeze-identities.txt。运行 `tools/verify_c11.py D:/CodexProjects/VideoKit --working-tree` 校验实际ZIP每个entry、冻结源/证据/产物及动态计数。

## 完整性与下一步

C01–C10的{len(integrity['frozen_files'])}条冻结记录、{len(integrity['samples'])}个素材完整性PASS，不修改历史候选或素材。完整官方签名FFmpeg8.0.3源档（9893上游文件）、配置/来源/许可证/依赖映射随本批保留，不以省略源码换小归档。

一次交tester，按冻结device_plan串行执行每个合格设备{plan['total_per_eligible_device']}项：CPU {plan['counts']['cpu']}、host {plan['counts']['host']}、legacy {plan['counts']['legacy']}。不得自动重跑相同signal0条件；若平台证据仍不可得，保留FAIL/BLOCKED并提交完整报告。手机禁用保持独立环境阻断，不enable/卸载/清数据。源码本机PASS不等于D1/Kit/AAR/Flutter/模型权利/发行或全P0通过。
''')
new=['cpuDuplicateConnectionKeepsOriginalIdentity','cpuCancelDuringHelloCannotStartOrRevive','cpuRejectedExtraWorkerRetainsSlotAndSecondTask','cpuLateWorkerCannotBorrowOriginalDeath','cpuExitCollectionRejectsMainThread']
rows='\n'.join('| '+str(i)+' | '+g+' | '+name+' |' for i,(g,name) in enumerate([(g,n) for g,ns in plan['groups'].items() for n in ns],1))
save('D1_C11_DEVICE_APPENDIX_V1.0.md',f'''# C11 手机/平板统一设备附录

2026-10-16。coder设备执行NOT_RUN。整批冻结后由负责人一次交tester，不逐功能换包。实际包hash/证书及环境、空间、数据、旧包备份须现场独立核验，不能从连接/安装成功推断Service可用。

## 前置与预算

ARM64/API31+；保存真实API/ABI/页大小与当前serial。历史平板HA1Q6WXR/TB138FC可用，手机U4999DLBNRR89DOR/PDYM20被com.oplus.athena禁用，这些历史不替代当前预检。只读installed/enabled/component/Service检查失败立即停止相关组并记ENVIRONMENT_BLOCKED/UNKNOWN；不enable、卸载、清数据或绕过系统限制。CPU每方法及每start都有App内预检，assumption不能算PASS。

核对冻结main/test APK；CPU不用companion。legacy阶段才核对worker APK，原私有数据/旧包/cache和capture保留。新files/d1_c11_fixtures仅basic.mp4、subtitle.avi，合计736803758字节；源hash见transfer_fixtures，实际传输身份独立核验，不覆盖旧候选目录。保留总fixture＋最大单文件＋256MiB余量。每设备日志总32MiB，legacy新终态输出建议≤32项/8MiB，CPU不落持久帧/READY。

run_device_c11.py默认PLAN_ONLY，只有显式serial/method/group、独占attempt-dir、设备预算根及候选/数据复核才执行单方法；本批只允许device_plan.json的入口。日志读取时硬限额，失败非零退出、停止外层调度。超时/本机子进程结束不证明远端已停或资源释放；必须核查在途和残留，不能自动调下一项。记录每次尝试，不覆盖、不重复相同signal0条件。

## 验证与门槛

每个合格设备{plan['total_per_eligible_device']}项，CPU {plan['counts']['cpu']}、host {plan['counts']['host']}、legacy {plan['counts']['legacy']}。APK另编入的历史ordinary UNKNOWN/播放/模型入口不在本批调度范围；不要按整个JUnit类批跑。正常MP4/AVI及finally资源门禁先过，再按依赖运行独立反例。

新增五项：{', '.join(new)}。额外worker测试是真实独立隔离进程，只有HELLO/STOP控制，故意挂起STOP；不发送START/broker/source/媒体。须看到旧worker已死而额外worker未死时slot不释放、第三任务被拒、第二任务继续真实解码；finally经认证解除闸门、解绑额外连接并核对所有实际死亡。旧death重放只允许已有真实DeathRecipient的原端点，不能用调试调用制造第一次死亡证明。

保存原始task/epoch、首次PID/UID/process身份、generation注册/HELLO/死亡、每代次STOP attempts/pending/ACK/result、binding_closed、全局unproven/reserved_cpu_slots、Source实际operations/consumers/failedCloses/close、所有pending_calls和最终slot。MAX_WORKERS=4是历史/异常端点记录上限，不是并发CPU许可；溢出/未知/在途保留quarantine。

**严格判失败条件**：首次身份被改写，原帧/旧death归到新代次，终态重新START，未知/额外worker仅凭unbind或旧death释放，binding_closed后新未知进程或登记，仍在途时slot放行。若出现，停止调度、保留原账本与原始进程证据，不能拿末尾ps空补成期限内通过。framework/系统创建竞态未实测，不预写通过。

两个SIGSEGV入口仍需真实帧→ARMED→cleanup前实际death，精确匹配原任务PID/isolated UID/时间/进程的raw单独保存。EXIT_EVIDENCE.signal是原OS status，trace_signal另列；**status0无论trace声明什么都UNKNOWN/FAIL**。不得以STOP的SIGKILL、isolated-not-needed、清理或测试预期替代目标signal11。不因本批读取trace而批准新P0依据。

主线程取证拒绝测试应返回明确状态且不启动采集。真实采集最多3次打开流，3秒轮询/调用方4秒等待；PENDING/关闭失败要保留采集器隔离，禁止超时清零。legacy共享ExitEvidence和parser变化，坏/冲突trace只能保守失败；原codec abort原因白名单不扩。host仍要求H264/AAC双轨各自非零、真实PTS和full decode，以及ready/abort/reconcile安全门禁。

## 明确单方法清单

| 顺序 | 组 | 方法 |
|---:|---|---|
{rows}

每设备按实际结果区分PASS、TEST_FAILED、ENVIRONMENT_BLOCKED、PREPARATION_FAILED/UNKNOWN、EXECUTION_UNKNOWN；不能把断言FAIL改为环境阻断，也不能以历史C10 PASS代替C11。方法断言通过之后还需独立审账本/raw。整批结束核查无在途/残留、素材hash和日志/输出预算，提交完整集中报告。D1未通过，不进入M0。
''')
save('D1_C11_LICENSE_BUILD_ADMISSION_V1.0.md','''# C11 许可、来源和构建准入

2026-10-16。DEBUG_EXPERIMENT_ADMITTED；正式SDK/产品外发、专利、商店和全P0未准入。

继承冻结C10，摘要SHA256 `4b728a9b5694e096e0374cd8d2e5bb77ce53afb173e512d0308d8f9ca4e0deec`。FFmpeg仍官方签名8.0.3，完整源档SHA256 `6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818`，11407656字节、9893上游文件；签名/公钥/C09的VALIDSIG回执随继承证据保留。C11没有再次运行GPG或重建FFmpeg，TRUST_UNDEFINED不声称Web of Trust。

libavformat/libavcodec/libavutil/libswscale/libvideokit_alloc五项原始库与C10逐字节相同，quota.c相同；仅CPU/lease JNI包名c10→c11重编译。CPU算法与同一C09源比较仍仅包身份变化，NDK30.0.16248370/API31，完整NDK/工具链NOTICE保留。266对象、608依赖与配置/许可映射在evidence/inherited-c09，按C10已修正266的实际数组继承；旧冻结未修改。32/64位边界、MPEG4/H264输入白名单、H263必要传递编译与输入拒绝、16MiB单次/64MiB累计请求/4096记录、packet/read/像素预算均保持。VMS上限与FFmpeg申请额度不冒充全进程RSS证明。

GPL/NONFREE/VERSION3/NETWORK仍0，无encoder/muxer/protocol/hwaccel扩入。许可仍LGPL-2.1-or-later及IJG/ISC/MIT/Zlib特别归属，三项IJG和六项特别声明/完整LICENSE/COPYING真实进入Debug APK。完整许可文本包含可选GPL条款不代表编入GPL组件。所有特别许可和NDK NOTICE按实际APK逐项核对。C09既有8.0→8.0.3维护差异、安全patch精确条件/源码映射仅作为继承证据，不声称C11重新全面漏洞扫描或利用验证。

Media3 1.9.3及app/worker依赖锁不变，锁与C10源ZIP核对。新增WorkerGenerations、ExitTraceRules、ExitTraceCapture、registrar与控制适配为项目自编Java胶水，无新外部依赖、模型或crash handler。解析器按固定AOSP Android12公开tombstone schema字段独立实现，来源链接在EXIT_EVIDENCE_DESIGN；安装SDK文档摘录与hash在本批证据。AOSP schema没有作为新的protobuf runtime打包。

SBOM在evidence/c11-sbom.cdx.json；实际包的native库、ABI/SONAME/NEEDED/符号/hash/ZIP_STORED/16KiB偏移和ELF LOAD、JNI描述符、manifest及签名报告在apk-audit及关联文本。七项自有库与原始输入相符，继承AndroidX graphics path四ABI与C07基线相符。Release与C07/C10对照逐字节一致，无C11类/服务/库/notice；这是静态包证据，不是Android加载或16KiB设备执行。

完整压缩上游源档、已核验头文件来源/生成配置、源和对象许可/依赖映射、构建脚本与原始动态库均保留。参考FFmpeg重建脚本默认不执行，需显式启用并先展开源/构建同源quota；不将历史参考脚本当作本批已重新执行。动态链接也不能自动关闭外部分发的替换/再链接/EULA/商店义务。

正式方向维持Flutter宿主＋独立Kit/AAR；本批为单APK普通隔离Debug胶水，companion仅legacy回归。未引入新权重、AI SDK或产品授权。硬件/系统codec/真实Binder行为待集中设备回归。D1未通过，不进入M0。
''')
print('C11 delivery, device appendix and license admission generated from actual review/plan/artifact identities')
