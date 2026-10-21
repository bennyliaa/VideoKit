from pathlib import Path
import json
root=Path(__file__).resolve().parents[4];base=root/'docs/coder/d1c14';e=base/'evidence'
assert not (e/'freeze-summary.json').exists()
r=json.loads((e/'candidate-self-review.json').read_text(encoding='utf-8'));plan=json.loads((base/'tools/device_plan.json').read_text(encoding='utf-8'));integrity=json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))
def save(name,text):(root/'docs/coder'/name).write_text(text,encoding='utf-8')
artifacts='\n'.join('| '+a['file']+' | '+str(a['bytes'])+' | `'+a['sha256']+'` |' for a in r['artifacts'])
save('D1_DELIVERY_D1-20261016-C14.md',f'''# D1-20261016-C14 整批交付

2026-10-16。READY_FOR_COORDINATED_DEVICE_TEST / D1_NOT_PASSED。本机实现、自检、NDK/Android集中构建与静态审计完成，设备NOT_RUN，无ADB。git_commit=null，以实际源ZIP/逐文件SHA/冻结摘要识别。D1未通过，不进入M0。

## 具体结果与证据限界

C13正式输入：平板52 PASS/3 FAIL/14 BLOCKED，手机69 ENVIRONMENT_BLOCKED，无在途。两正例停在OMX.qcom.video.encoder.avc configure，received/input/sample/verified均0；-38/0x80001001不足以唯一归因颜色/profile/权限。旧host成功不能代替新管线。C14没有假称已在设备解决该错误，交可验证新候选。

已实现有界公开AVC协商：保存硬件/软件/vendor属性及尺寸/率/码率/对齐/颜色/profile范围，最多两个不同codec、每个最多两个标准格式，交错≤4提案/创建，12秒协商且受总60秒预算限制。颜色21/19/Flexible只从声明成员选择，variant1最小默认profile、variant2不同标准颜色并仅声明支持时加Baseline；不写C13可选level/maxB/color键。逐格式实际isFormatSupported并独立核对几何/颜色，公开能力只是假设，实际create/configure/start结果另列。

每失败候选须实际release、Image/creating/owner calls清零才下一，close未知或create未返回对象不重选并保留单许可；取消/预算截止也不跨线程强制release。配置成功前不启动Source producer或输出writer；运行期输入/输出/MUX/验证错误不回到选择环。只有创建之前无支持格式记CAPABILITY_BLOCKED，已选configure/start失败及运行期输入不兼容保持失败，未释放仍PENDING。

新增分阶段类型诊断ENUMERATE/CAPABILITY/CREATE/CONFIGURE/START/INPUT/OUTPUT/MUX/VALIDATION/CLOSE，保存CodecException公开errorCode/诊断标识/recoverable/transient、有限数值format键和第一次尝试错误；后续选中不会抹掉已失败历史。无路径/凭据/任意message入日志，原通用REDACTED不是此路径诊断替代。cleanup与首因分列，无运行期自动恢复成成功。

原六真实源snapshot→不可变queue→系统AVC/既有Media3 fMP4→隔离CPU完整六帧EOF保持。PTS≤1ms、luma≤24、源差异≥4/输出≥2及错误映射拒绝不改，不换合成帧、不宿主解压缩源。CPU2/encoder1/queue2/consumer1与8份可达RGBA1179648B＋YUV55296B保持；新增queued/offers、保留CPU任务、codec/Image/转换数组和owner calls账本。它是逻辑所有权/静态保守预算，非ART堆/RSS峰值或设备质量通过。

## 本机实际验证

{r['pure_assertions']} JVM＋{r['script_assertions']}脚本＝{r['total_local_assertions']}断言通过，实际日志重算；其中新增51条共享有限协商反例。fake Driver只证明规则，不证明Android codec。脚本还阻止两个未改变的CPU信号方法进入调度，保持其NOT_RUN事实。

完整离线assembleDebug/AndroidTest/Release/legacy-worker集中构建、API31 ARM64 CPU/lease JNI、APK manifest/DEX/native来源/符号/JNI descriptors/签名/ZIP与ELF、源码-class-产物绑定审计通过。保留首次及审查构建日志；未clean、未运行connected/managed/ADB。审查补充成功CLOSE记录和运行期失败分类后最终产物重新审计。Release字节与历史相同，无C14 class/service/native/notice。

C01–C13共{len(integrity['frozen_files'])}条不可变记录和45项原始媒体hash核验PASS；源码/产物/证据与样本未改。五FFmpeg/allocator库、quota.c及CPU/退出采集算法不变，JNI仅身份相对C13重编。Media3 1.9.3锁不变；完整FFmpeg8.0.3源、签名/公钥/既有准入、配置/266对象/608依赖/特别NOTICE/SBOM保留，不声称本批重跑GPG/上游构建/全面安全扫描。

| 产物 | 字节 | SHA256 |
|---|---:|---|
{artifacts}

产物目录docs/coder/d1c14/artifacts/D1-20261016-C14。源码、构建配置及pre-freeze证据实际同入源ZIP，另逐文件hash；evidence/freeze-summary.json和freeze-identities.txt给出完整身份（收据在freeze之外避免自引用）。tools/verify_c14.py D:/CodexProjects/VideoKit --working-tree独立核验实际ZIP每entry/源/证据/产物/日志计数与调度/未重跑清单。

## 设备计划及未完成范围

35 CPU＋7 host＋8 legacy＋17 pipeline＋6 encoder＝73可调度方法/合格设备，另2项CPU信号方法编译保留但明确NOT_RUN_UNCHANGED_PLATFORM_LIMIT，指定记录合计75。原14个BLOCKED反例全部保留，正常六帧正例成功后执行依赖；不计纯断言为设备PASS。没有自行交tester，只由负责人整批安排。

C13-T02 self App系统signal0保持严格FAIL，trace缺失/ordinary UNKNOWN OPEN，独立双槽OS11结果另列；退出采集未变，不为新身份重跑这两项，不用raw11/清理补信号，不新crash handler。legacy既有实际编码/Sink故障回归不用于CPU App信号结论，不扩大campaign。手机禁用独立阻断，不换包/卸载清数据/强启或反复找缺失按钮。

设计/缺陷/计划见：[编码协商](D1_C14_ENCODER_NEGOTIATION_DESIGN_V1.0.md)、[缺陷矩阵](D1_C14_DEFECT_MATRIX_V1.0.md)、[边界](D1_C14_PIPELINE_BOUNDARY_DESIGN_V1.0.md)、[框架](D1_C14_FRAMEWORK_MAPPING_V1.0.md)、[许可](D1_C14_LICENSE_BUILD_ADMISSION_V1.0.md)、[设备附录](D1_C14_DEVICE_APPENDIX_V1.0.md)、[十二项剩余门禁](D1_C14_REMAINING_GATE_REVIEW_V1.0.md)。内部com.videokit/com.videokit.<module>/com.videokit.app已定，不撤销；正式artifact/version兼容待验。

正式Flutter＋独立Kit/AAR/C ABI、多宿主与全部P0保持，未开发M0/Browser业务或Apple/Windows实现。新管线实际设备成功、完整危险链/宿主JNI/旧host验证/显示/PCM/字幕/图片/跟踪遮罩、真实权重/人物/训练与再分发权利/人工标签、热/质量/最低设备及发行条件均未完成。跟踪复用C13固定文字与真实标注0帧事实，未下载权重/媒体/新依赖或伪造标签。D1未通过。

本机子任务结束，不存在本批启动的设备操作；跨窗口通知不重试，由最终完成事件收取整批结果。
''')
rows=[];i=0
for group,methods in plan['groups'].items():
 for method in methods:i+=1;rows.append(f'| {i} | {group} | `{method}` |')
skipped='\n'.join('| `'+x['method']+'` | '+x['state']+' |' for x in plan['not_run_unchanged_platform_limit'])
save('D1_C14_DEVICE_APPENDIX_V1.0.md','''# C14 设备附录 V1.0

2026-10-16，仅编译后计划，所有本批设备NOT_RUN。73可调度＋2不重跑的信号门禁，不能把后者当PASS或环境阻断。coder无ADB、不自行交tester；负责人统一安排。

## 调度与依赖

环境只读预检实际App/component/service enabled；手机禁用仍ENVIRONMENT_BLOCKED，UNKNOWN另列，不安装绕过/换包名/卸载清数据/强启。冻结身份和可读旧cache/旧APK由tester按正式要求保留，fixtures/basic.mp4与subtitle.avi只读，不修改原媒体或旧capture。

先环境、公开能力快照、CPU正常MP4/AVI基线，再pipeline MP4/AVI两正例；两正例必须六真实源/六输入/六样本/六独立完整EOF，原时基与相对PTS≤1ms对应，luma≤24、源差异≥4/输出≥2及映射拒绝不改，无音频明确。未成立时后续14个原负例依赖BLOCKED而非编造通过。OwnerRecovery只依赖环境/lease。host7双轨/故障/恢复、legacy8实际编码/Sink/恢复在真实remote终态后回归；不增新crash方法。

Encoder six：PublicCapabilitySnapshot记录实际inventory/四提案上限，没有可用encoder也只证明快照完成；CapabilityDenial人为拒绝能力，预期0 create/0 Source/0 writer/无token且实际资源归还，不是实际设备无能力结论。RejectedConfigurationReleasesBeforeNext在真实configure返回后注入首次拒绝，须先实际release再下一，最终真实六帧READY、attempt2–4、firstAttemptError CONFIGURE仍在；若有限候选不能满足，保留真实FAIL，不无限重跑。AllRejected在每个实际configure后注入拒绝，首CONFIGURE失败、1–4次、无Source/输出writer/READY。

CancelDuringNegotiation在真实configure返回后的owner闸门持有时主线程cancel，pendingOwnerCalls1、单许可保留且无Source/writer，解闸后实际release才ABORTED；这是owner操作闸门，不冒充被卡住的vendor JNI。CloseAckUnproven在实际release正常返回后保守扣住ACK，PENDING/attempt1/codec_released=false/许可1且不重选；只有测试明确确认该实际返回后recover归还。它不制造真实硬件release失败；真实release不确定仍quarantine，不可用测试确认接口绕过未知底层状态。

所有原17 pipeline方法保留：跨代/迟到在复制前拒绝，queue满必须见2帧及blocked offer>500ms，消费者失联/编码输入拒绝/运行错误不READY；Sink write/flush注入命中实际writer，截断只改自己的临时输出并由隔离CPU拒绝，READY丢响应同exportId query/reconcile同token。取消时consumer租约1要立即PENDING，另一真实CPU继续并resume得到帧，第二encoder创建前拒绝。owner-drop恢复不是新管线实际宿主SIGKILL；原legacy真实host death方法仍分开。

## 原始证据与有限预算

保存PIPE_ENCODER_CAPABILITY/PLAN/DIAGNOSTIC/OPEN/OUTPUT_FORMAT及PIPE_SOURCE_FRAME/ENCODE_INPUT/SAMPLE、CPU_OUTPUT_FRAME/FULL_EOF、CONTENT/VISUAL_CHECK和PIPE_LEDGER。每个候选name/canonical/hardware/software/vendor、范围/对齐/color/profile、actual isFormatSupported、配置keys/phase/公开错误码/诊断标识/首错/关闭均核对；支持声明不是配置成功，软件选中不说硬编保证。close未证、creating或owner call未归还必须停止重选/保留PENDING；实际失败不可改为能力skip。

最多128系统info、16 AVC能力、32types、64colors/64profile-level、标识128字符、4提案/创建、12秒协商且总60秒；原生调用超时不强制释放。CPU2、encoder/output1、queue2/consumer1/producer1，8份可达RGBA1179648B＋YUV55296B，codec/Image/转换数组及queue/offers/保留CPU任务分别记账；不是整堆/RSS峰值。六snapshot逐次实际关闭源后推进，Source pending/死亡/绑定/两槽证据独立。

单输出含头≤2MiB，d1_c14_pipeline_outputs最多24 journals/累计4MiB，创建前预留2MiB；host＋pipeline整批新输出≤8MiB且task/journal按正式tester总预算，日志/文本≤32MiB、剩余空间足够。保留历史数据，不删除凑预算；fixture不计新输出，但磁盘需容纳736803758B只读basic/subtitle。新6方法产生自己的失败journal，事前预估73项总量，接近目录24或4MiB时停调度交负责人，不清历史。源/旧capture完整hash前后核对，SRT存在不等字幕时序/显示通过。

run_device_c14.py默认PLAN_ONLY。执行需serial/group/method、review、docs/tester内独占attempt-dir及per-device log-budget-root；每次日志流限额，失败/能力阻断/环境阻断/UNKNOWN非零，停止依赖链。两个不重跑CPU方法会在ADB预检之前被require_planned明确拒绝。客户端超时/退出不证明远端结束，先实际核在途/服务/进程、保留全部尝试和错误，由负责人决定独立项，不重复跑求理想signal。

结束复核真实每方法资源账本、Source/codec/Image/FD/lease/owner/callback/帧、预算和旧数据hash；末尾ps空只证明结束状态。C13-T02原FAIL与trace/ordinary限制不关闭。D1未通过，不进入M0。

## 明确未重跑的两项（编译保留）

| 方法 | C14计划状态 |
|---|---|
'''+skipped+'''

两项采集代码/判定没有改变；引用正式C13报告self系统0 FAIL和独立双槽系统11 PASS及各自实际释放事实，不外部raw回填，不将C12历史成功写为C14成功。

## 73个可调度方法

| 顺序 | 组 | 方法 |
|---:|---|---|
'''+ '\n'.join(rows)+'\n')
print('C14 delivery/appendix generated: 73 scheduled + 2 unchanged-signal NOT_RUN')
