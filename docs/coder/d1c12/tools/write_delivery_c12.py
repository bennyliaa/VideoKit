from pathlib import Path
import json
root=Path(__file__).resolve().parents[4];base=root/'docs/coder/d1c12';e=base/'evidence'
assert not (e/'freeze-summary.json').exists(),'Frozen documents cannot be regenerated'
review=json.loads((e/'candidate-self-review.json').read_text(encoding='utf-8'));plan=json.loads((base/'tools/device_plan.json').read_text(encoding='utf-8'));apks=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks'];integrity=json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))
def save(name,text):(root/'docs/coder'/name).write_text(text,encoding='utf-8')
table='\n'.join('| '+r['file']+' | '+str(r['bytes'])+' | `'+r['sha256']+'` |' for r in apks)
save('D1_DELIVERY_D1-20261016-C12.md',f'''# D1-20261016-C12 整批交付

2026-10-16。READY_FOR_COORDINATED_DEVICE_TEST / D1_NOT_PASSED。无Git仓库，git_commit=null，源ZIP/逐文件SHA256/冻结摘要识别本批。仅本机实现、自审、编译和打包；无设备/ADB。D1未通过，不进入M0。

## 输入与修复

正式输入D1_C12_CODER_REQUIREMENTS及D1_C11_TEST_REPORT原文保存在evidence/input-*。C11平板20 PASS/2 FAIL/23 BLOCKED、手机45环境阻断保持，不回写历史结果。

- C11-T01：registrar按ONEWAY位判断同步，兼容框架metadata；descriptor/code/kernel PID/UID/session/endpoint/长度和尾随数据仍严格校验。16字节固定primitive ACK/错误枚举，记录实际caller/flags/输入字节/结果；合法致命失败回报保留具体REGISTER首错，未证设备flags不写成根因。
- C11-T02：独立BindingRevocation及UNBINDS执行器，cancel、迟到bind返回、未知连接/HELLO失败可安排撤销自动重建绑定；Context IPC不持有client/workers锁。start改一次性原子门禁，不在等待期间持锁拖延清理。解绑成功不清零未知worker，不产生死亡/未创建/slot释放证明；真实在途/失败继续quarantine，显式恢复最多3次，不以重复cancel自动重试失败。
- C11-ENV01：只读环境硬门禁保持，手机系统禁用独立阻断。用户已在正确设置页且没有启用按钮，不再机械要求寻找该按钮，不绕过系统控制。
- C11固定首次Binder/PID/UID/逐代次death、全局2 CPU槽、异常端点无START/source/解码许可保持。MAX_WORKERS=4是历史/异常记录上限，溢出不放行。共享ExitEvidence/TraceCapture/解析器除包名外与C11一致，原系统signal0仍UNKNOWN/FAIL，即使App trace声明11；外部raw/ARMED不充当产品取证源。

设计和未证限制见 [握手/撤销设计](D1_C12_HANDSHAKE_BINDING_DESIGN_V1.0.md)、[缺陷矩阵](D1_C12_DEFECT_MATRIX_V1.0.md)、[框架映射](D1_C12_FRAMEWORK_MAPPING_V1.0.md)、[设备附录](D1_C12_DEVICE_APPENDIX_V1.0.md)、[许可准入](D1_C12_LICENSE_BUILD_ADMISSION_V1.0.md)。C11 trace原设计保留，不申请改变P0判定依据。正式Flutter＋独立Kit/AAR方向不变，companion仅legacy回归；无新权限/组件/模型/codec实现。

## 本机证据

{review['pure_assertions']} JVM断言＋{review['script_assertions']}脚本断言，共{review['total_local_assertions']}通过，计数由本批实际日志生成。包括注册同步flags/身份/固定reply、绑定迟到返回/未知保留/解绑失败恢复及既有代次/trace/host规则；纯模型/JVM进程锁不证明Android并发。实际Android测试方法只编译，运行NOT_RUN。

完整离线Android集中构建主Debug/test/legacy-worker/Release及NDK API31 CPU/lease JNI通过；仅assemble，不connected/managed/ADB，不clean。Gradle写用户缓存经工具审批，NDK临时文件位于本候选outputs；没有绕过设备工具门禁。JNI callback descriptor与实际class核对，源码/class时间及hash和产物绑定在build-source-binding.json。

APK manifest/DEX/native来源/签名/zipalign/ELF审计通过；三个Debug同证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。Release与C07/C11对照逐字节相同，无C12类/服务/库/notice。16KiB静态对齐不是16KiB页设备运行通过。

| 产物 | 字节 | SHA256 |
|---|---:|---|
{table}

产物目录docs/coder/d1c12/artifacts/D1-20261016-C12。源ZIP与冻结摘要完整身份见freeze-summary.json及freeze-identities.txt，避免自引用。tools/verify_c12.py D:/CodexProjects/VideoKit --working-tree 实际核验ZIP每个entry、源/证据/产物和动态计数。

C01–C11的{len(integrity['frozen_files'])}条冻结记录、{len(integrity['samples'])}个素材完整性PASS，未改历史候选或素材。完整官方签名FFmpeg8.0.3源档（9893文件）、配置/来源/许可/266对象/608依赖及原库随本批保留，Media3及配额不变。

一次交tester，冻结计划每合格设备{plan['total_per_eligible_device']}项：CPU {plan['counts']['cpu']}、host {plan['counts']['host']}、legacy {plan['counts']['legacy']}。先实际正常注册/MP4/AVI前置；依赖失败阻断，不重复相同signal0条件碰运气。新实际flags/拒绝分支/解绑和death/未知预算证据仍待设备，不能以本机PASS宣布C11根因或D1闭合。
''')
rows='\n'.join('| '+str(i)+' | '+group+' | '+method+' |' for i,(group,method) in enumerate([(g,m) for g,ms in plan['groups'].items() for m in ms],1))
save('D1_C12_DEVICE_APPENDIX_V1.0.md',f'''# C12 手机/平板统一设备附录

2026-10-16。coder设备NOT_RUN；负责人一次整包交tester，逐方法串行，不与构建争用。冻结device_plan.json为唯一调度清单；APK另编入的历史ordinary UNKNOWN/播放/模型入口不自动运行，不按整个JUnit类批跑。

## 前置、数据及停止规则

实际核验serial/API31+/ARM64/页大小、已装包hash/签名/用途、installed/enabled/component/Service及空间；连接/安装成功或历史设备型号不是就绪证明。历史手机U4999DLBNRR89DOR/PDYM20系统禁用，用户正确设置页无启用按钮；环境未变则ENVIRONMENT_BLOCKED，不重复要求找按钮，不enable、卸载、清数据或绕过系统。平板历史HA1Q6WXR/TB138FC需现场重新核验。

CPU只用主/测试APK；legacy阶段才核对worker APK。新files/d1_c12_fixtures仅basic.mp4和subtitle.avi，736803758字节，hash见transfer工具；保留旧包/数据/cache、旧capture及fixture，不覆盖原素材或旧候选目录。空间沿用fixture总量＋最大单文件＋256MiB余量；每设备日志32MiB，legacy新终态建议≤32项/8MiB，CPU不持久落帧或READY。

工具默认PLAN_ONLY，执行需明确serial/method/group、独占attempt目录、设备预算根及候选/数据复核。每次命令读写时限额，失败非零退出、停止外层调度。真实断言FAIL、环境阻断、执行UNKNOWN分开。超时或本机ADB客户端结束不证明远端已停；须核查实际在途/进程/Service并由负责人决定独立项。保留全部尝试，禁止同条件重跑求理想信号。

环境预检后先正常MP4/AVI，必须见REGISTER/HELLO/真实帧及finally完整门禁，再调度解码依赖。无绑定资源/首错、未知空长度、LocalHostIdentity和主线程取证拒绝等独立项可另判；host7/legacy8需实际远端结束后独立回归。原C10/C11未进入的代次/trace在前置恢复后单次验证，不能引用旧PASS/FAIL改写本批。

## 新证据重点

- cpuRegistrarSynchronousMetadataAndRejects：真实isolated→host注册事务，覆盖同步0/metadata组合、oneway组合、code/descriptor/session/endpoint/尾随拒绝；保存接收端真实flags/caller PID/UID/result，不能把发送端参数当接收实测值。重复登记应同一代次，只链接一次死亡，无额外START。
- cpuRegistrarLocalHostIdentityRejected：Android本地Binder的非隔离host身份拒绝，仅为本地负例，不冒充远端kernel身份错误已测。
- BadMagic/TrailingReply：只在Debug测试破坏REGISTER reply，worker须分开记录固定原因并经认证FAILURE回报；host首错为对应CPU_REG_REPLY_*且phase REGISTER，cleanup独立，不得降为generic CONNECT timeout。不得发送START或解码预算。
- CancelBeforeRegistration/BeforeBindReturn：真实注册在途闸门、迟到返回与主线程cancel；解绑不等登记/死亡，须见closed=true时未知/在途/两槽仍保留且第三任务拒绝，另一任务继续完成。解除闸门后晚到端点只撤销，实际death/Source/全部pending回收后才释放。
- UnbindFailureRequiresExplicitRecovery：第一次解绑故意失败，重复cancel不自动重试/放行；显式recover第二次真实解绑，仍需实际death。最多3次，失败保留quarantine。
- 原STOP_STALL/ACK-loss方法增加显式Debug解绑闸门，保留原响应/在途反例窗口，finally必释放；生产cancel没有该闸门。闸门超时不能伪释放。

记录CPU_REGISTRATION_DIAG、worker CPU_REGISTRATION_REPLY/FAILED、CPU_DIAGNOSIS、逐代次ledger，以及CPU_UNBIND_LEDGER issued/accepted/uncertain/in_flight/requested/attempts/pending/closed/result（issued由实际绑定阶段另核对），Source及全部pending/slots/global未知预算。binding_closed、actual_death、no_worker_proven、slot_released四种事实分别审核；未知accepted绑定即使解绑后计数仍≥1。绑定失败/超时/解绑成功/系统finished-inst或末尾ps空不能作未创建或期限内死亡证明。

C11首次Binder/身份、旧death隔离、额外端点无START/source、两CPU槽/MAX_WORKERS异常记录上限继续验证。若binding_closed后出现未知新进程/登记、终态重新START、旧death给新worker释放或unknown借解绑清零，保留FAIL并停调度。

严格SIGSEGV入口仍须真实帧→ARMED→cleanup前death，原任务PID/isolated UID/时间/进程的raw独立保存。EXIT_EVIDENCE.signal是OS原始status，trace_signal另列；signal0无论trace声明什么都UNKNOWN/FAIL。外部raw、STOP的SIG9、测试预期和清理不替代目标11。C11取证器3条流/字节限制及pending/close隔离不变。

host维持真实H264/AAC双轨各自非零、PTS/full decode和READY/abort/reconcile门禁；legacy8仅历史companion回归，不证明CPU trace已通过。整批结束复核无在途/残留、素材hash、旧capture及日志/输出预算，集中报告。D1未通过，不进入M0。

## 单方法清单：{plan['total_per_eligible_device']}项

| 顺序 | 组 | 方法 |
|---:|---|---|
{rows}
''')
save('D1_C12_LICENSE_BUILD_ADMISSION_V1.0.md','''# C12 许可、来源和构建准入

2026-10-16。DEBUG_EXPERIMENT_ADMITTED；正式SDK/产品外发、商店、专利和全P0未准入。

继承冻结C11，摘要bfe33794c0ac606fef0e5fb498672e3a9e33b8390b0e21fe153eb86877306138。官方签名FFmpeg8.0.3完整源档SHA256 6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818，11407656字节、9893文件；签名/公钥/C09 VALIDSIG和配置/生成头文件/来源/许可映射随继承证据保留。未声称C12重跑GPG、重建FFmpeg或全面扫描漏洞；TRUST_UNDEFINED不当作Web of Trust。

libavformat/libavcodec/libavutil/libswscale/libvideokit_alloc五原库与C11逐字节一致，quota.c一致；CPU/lease JNI仅包身份c11→c12重编译，CPU算法与同一C09来源比较仍仅JNI身份变化。266对象/608依赖、已审维护差异/安全patch精确条件映射、LGPL-2.1-or-later及IJG/ISC/MIT/Zlib特别归属原样继承。完整许可/三项IJG与六项特别声明和NDK/工具链NOTICE按实际Debug APK核对；许可文本可选GPL条款不代表编入GPL。GPL/NONFREE/VERSION3/NETWORK仍0，不扩codec输入/encoder/muxer/protocol/hwaccel。

NDK30.0.16248370/API31；16MiB单次、64MiB累计请求/4096记录、读取/packet/像素预算不改，不能冒充全进程RSS证明。原始动态库、完整压缩上游源、配置/构建脚本/依赖及特别许可保留。参考FFmpeg重建脚本默认不执行，不将历史脚本当本批重跑；动态链接不自动关闭外发替换/再链接/EULA/商店义务。

Media3 1.9.3及app/worker依赖锁保持，app锁与C11源ZIP核验。新增RegistrationProtocol/BindingRevocation及必要Android协议/生命周期适配为自编Java胶水；无新权限/组件、外部依赖、protobuf runtime、模型、crash handler或codec实现。Binder API来源映射见D1_C12_FRAMEWORK_MAPPING，SDK摘录仅兼容参考，不当设备flags证据。C11退出取证/白名单/Source bridge和输出双轨逻辑保持。

SBOM、实际APK manifest/DEX/native来源/ABI/SONAME/NEEDED/JNI符号及描述符、hash、签名/ZIP_STORED/16KiB偏移与ELF LOAD报告在evidence。七项自有库与原始库一致，继承AndroidX graphics path四ABI与C07核对；Release与C07/C11对照逐字节一致，无C12类/服务/库/notice。静态对齐不代表16KiB设备运行。

正式Flutter＋独立Kit/AAR方向保持；本批单APK普通隔离Debug胶水，companion仅legacy回归。有限Debug准入不代表产品Kit、多宿主、模型权利或发行闭合；D1未通过，不进入M0。
''')
print('C12 delivery/appendix/license generated from actual review, plan and APK identities')
