from pathlib import Path
import json
root=Path(__file__).resolve().parents[4];base=root/'docs/coder/d1c13';e=base/'evidence'
assert not (e/'freeze-summary.json').exists()
review=json.loads((e/'candidate-self-review.json').read_text(encoding='utf-8'));plan=json.loads((base/'tools/device_plan.json').read_text(encoding='utf-8'));integrity=json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))
def save(name,text):(root/'docs/coder'/name).write_text(text,encoding='utf-8')
table='\n'.join('| '+r['file']+' | '+str(r['bytes'])+' | `'+r['sha256']+'` |' for r in review['artifacts'])
save('D1_DELIVERY_D1-20261016-C13.md',f'''# D1-20261016-C13 整批交付

2026-10-16。READY_FOR_COORDINATED_DEVICE_TEST / D1_NOT_PASSED。仅本机实现、自审、NDK/Android编译及静态审计；设备执行NOT_RUN，无ADB。无Git仓库，git_commit=null，以本批源ZIP、逐文件SHA和freeze-summary识别；D1未通过，不进入M0。

## 实际交付

在独立c13 Debug包实现六个顺序隔离CPU真实snapshot→受控不可变RGBA队列→公开系统AVC→Media3既有fMP4封装→独立隔离CPU六帧完整EOF验证。每帧记录task/epoch/内核PID/UID/原时基/实际PTS/摘要，编码时间为首帧相对实际PTS；验证唯一视频轨、无音频、实际尺寸/方向、输出PTS与16×9 luma内容合理误差及画面可区分性。不是连续实时帧流、正式H264/AAC双轨导出或宿主源解码回退。

复用C12两CPU槽及Source/STOP/代次/退出账本，新增独立单encoder/output许可、queue2/consumer1、输出含容器头2MiB硬限额、有限目录。仅真正死亡/Source关闭/回调完成/codec与writer归还/帧租约清空后释放；超时或异常保留PENDING与quarantine。取消/慢消费者/失联/跨代/迟到/解码失败/编码拒绝与错误/Sink写flush验证失败/READY丢响应/owner恢复均有反例。新owner-drop恢复没有冒充实际新管线宿主进程死亡实测；既有真实host-death回归保留。

新增75条纯规则/队列反例，真实管线Android效果仍需设备验证。实现没有以合成图案替代真实源；单元测试合成数组仅验证规则，明确不能充当接续证据。若设备缺公开输入能力记CAPABILITY_BLOCKED，不能转PASS或偷偷回退。

设计/风险：[边界设计](D1_C13_PIPELINE_BOUNDARY_DESIGN_V1.0.md)、[剩余十二项门禁](D1_C13_REMAINING_GATE_REVIEW_V1.0.md)、[跟踪权利和标签](D1_C13_TRACKING_EVIDENCE_V1.0.md)、[框架映射](D1_C13_FRAMEWORK_MAPPING_V1.0.md)、[许可准入](D1_C13_LICENSE_BUILD_ADMISSION_V1.0.md)、[设备附录](D1_C13_DEVICE_APPENDIX_V1.0.md)。原始全需求和C13正式需求纳入源归档，C12报告原文随evidence留存。

## 实际本机证据

{review['pure_assertions']} JVM＋{review['script_assertions']}脚本＝{review['total_local_assertions']}条断言通过，计数由日志重算。完整离线Debug/test/legacy-worker/Release集中构建成功，API31 ARM64 CPU/lease JNI编译通过；保留初次及最终构建日志。最终构建包含审查补充的实际解码尺寸拒绝与回调关闭账本，不clean、不运行设备。局部规则和Windows/JVM锁测试不证明Android并发、实际编码、听音/显示/跟踪质量。

APK manifest/DEX/native来源/符号/签名/zipalign/ELF及源码-class绑定审计通过。Release SHA保持`71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e`，不含C13实验组件。五个FFmpeg/配额库与C12不变；JNI新增验证胶水的实际差异和callback descriptors另留，不能称仅改包名。app依赖锁与冻结C12源ZIP逐字节核对。静态16KiB对齐不是16KiB设备通过。

C01–C12 {len(integrity['frozen_files'])}条不可变记录、45项原始媒体hash核验PASS；没有修改旧候选或原样本、下载模型/媒体、增加依赖/权限/companion产品或crash handler。NOTICE/SBOM、完整FFmpeg8.0.3源/签名/配置与266对象/608依赖映射保留；许可只准本地Debug，不是外发/商店/专利/替换材料闭合。

| 产物 | 字节 | SHA256 |
|---|---:|---|
{table}

产物目录docs/coder/d1c13/artifacts/D1-20261016-C13。冻结摘要evidence/freeze-summary.json，源ZIP及摘要hash见freeze-identities.txt；该身份收据和验证输出放在freeze之外避免自引用。tools/verify_c13.py D:/CodexProjects/VideoKit --working-tree独立逐entry验证实际ZIP/源/证据/产物/动态计数。

## 交接范围与未证结论

设备计划37 CPU＋7 host＋8 legacy＋17 pipeline＝69方法/合格设备。C12完整52项按源码除身份重命名保留，不删难项；新增两正例与生命周期反例依赖实际前置成功。具体方法/依赖/预算见附录和device_plan.json，全部本批NOT_RUN，未派tester。手机系统禁用独立阻断，不绕过或机械要求寻找不存在按钮；只由负责人安排整批。

C12平板52 PASS/手机52 ENVIRONMENT_BLOCKED保持；当前两SIGSEGV OS11 PASS不改历史status0/ordinary UNKNOWN，App trace缺失OPEN，不同条件证据不混算。新输出验证视频专用，旧host双轨验证仍在宿主；MediaCodec JNI/系统vendor服务、字幕/图片/跟踪遮罩/显示/PCM危险链、模型权利/真实标签、最低设备/热/质量/多宿主Kit/AAR/C ABI/Flutter与全P0均未完成。完整§29和M0–M8路线保留，Apple/Windows不实现，VideoKit不引Browser业务。

结束时本机所有构建/审计子任务已结束，无设备任务被启动；不能据此推导设备释放或运行成功。跨窗口完成消息不重试，本任务完成事件由负责人收取。
''')
rows=[];i=0
for group,methods in plan['groups'].items():
 for method in methods:i+=1;rows.append(f'| {i} | {group} | `{method}` |')
save('D1_C13_DEVICE_APPENDIX_V1.0.md','''# C13 设备附录 V1.0

2026-10-16。仅计划与已编译方法，设备NOT_RUN，coder不调用ADB，不自行派tester。37 CPU/7 host/8 legacy沿用C12完整52方法，新pipeline17，共69/合格设备；方法清单由实际源码及DEX核对。两种真实源basic.mp4/subtitle.avi只读，原文件与旧capture保留；外挂SRT存在不构成字幕成功。

## 顺序与依赖

1. 由负责人确认冻结身份及空间/旧证据，tester只读查询实际app/component/service enabled。手机被禁用维持ENVIRONMENT_BLOCKED；未知状态另记UNKNOWN，不换包名/卸载/清数据/强启或要求找已确认不存在的按钮。
2. CPU环境、MP4/AVI真实帧基线及完整52回归。新pipeline依赖对应CPU源基线、实际编码能力及MP4/AVI两正例；正例不成立，编码/输出依赖项标BLOCKED而不拿纯测试补成功。ownerRecovery只依赖环境/lease，不依赖编码成功。
3. 每次只一个方法，独占attempt目录，保留所有日志与失败尝试。已有真实SIGSEGV两项随52回归，不加新故障campaign；ordinary UNKNOWN历史不重跑求理想信号。host7/legacy8在实际remote无在途后回归，不代替单APK管线或完整隔离。
4. 默认run_device_c13.py PLAN_ONLY；执行需serial/method/group=cpu|host|legacy|pipeline、review及docs/tester内独占attempt-dir/log-budget-root。失败、能力阻断、环境阻断和执行UNKNOWN非零退出，外层停止依赖链。客户端超时/结束不证明remote停止，先核查真实在途与负责人决定独立项。

## 新方法预期与原始证据

两正例必须6个真实源帧/编码输入/实际样本/隔离解码输出均为6，READY且同一token、audio=false；源task/epoch/PID/UID/raw timebase/实际PTS/hash逐帧对应。查看PIPE_SOURCE_FRAME、PIPE_ENCODE_INPUT、PIPE_ENCODE_SAMPLE、CPU_OUTPUT_FRAME_VERIFIED、CPU_OUTPUT_FULL_EOF_VERIFIED、PIPE_CONTENT_FRAME、PIPE_VISUAL_CHECK。输出PTS匹配源相对时间≤1ms，luma MAE≤24、源至少两画面差异≥4、输出差异≥2及错误映射拒绝；真实片段不具可区分性应FAIL/未证，不降低阈值或换合成图案。

CrossEpoch在额外复制前PIPE_FRAME_IDENTITY；LateFrame为PIPE_FRAME_ORDER；QueueSaturation实际queue2/blocked offer>500ms触发PIPE_FRAME_QUEUE_FULL；ConsumerLost、encoder-reject/error各保留对应首因。Sink write/flush有实际注入计数，验证反例先写真实输出再截断自己的临时文件，由隔离CPU解析/解码拒绝；所有负例token为空且不READY。ReadyResponse持久READY后故意丢应答，query/reconcile同exportId同token，恢复abort不能撤销READY。

CancelInFlight在真实consumer租约闸门持有时主线程cancel，立即PENDING/consumer1/encoder许可仍1；解闸后实际关闭才ABORTED和全部归还。IndependentCpu在第二真实WAIT_FRAME任务活着时让管线失败，第二任务不得死亡，resume后得到真实结果。RejectsSecondEncoder在第一真实在途时第二许可申请应在codec/输出创建前拒绝。OwnerRecovery验证live owner不可替换、实际关闭后重获WRITING并幂等abort；不是新管线宿主SIGKILL证明，真实host死亡仍看旧8项。

每方法保存PIPE_LEDGER及CPU逐代次death/source/binding/pending/slot账本，资源released须source、codec/Image、writer/FD/共享lease/owner、queue/consumer和callback实际归还。timeout返回PENDING不算已释放；原始错误与cleanup分开，未归还引用保持quarantine，禁止反复新建任务绕预算。source真实hash前后不变；producer后续可能打开句柄前不得移动/删除授权源。

## 预算与终结

CPU进程内2槽、pipeline encoder/output1槽；queue2+consumer1+producer候选1，固定RGBA147456B，保守8个宿主可达数组1179648B（不是RSS上限）与YUV55296B，缩略小记录；无Surface/AudioTrack。原FFmpeg配额/白名单不扩。单输出含容器头≤2MiB；专用d1_c13_pipeline_outputs最多24 journals/累计4MiB，进入前预留完整2MiB。监测host与pipeline合计新输出≤8MiB；旧目录不删除凑预算。每设备日志/文本≤32MiB，工具读写时限额，执行前检查剩余空间；fixtures不计输出预算但须充足磁盘。六快照每次实际释放后下一次，实验deadline60秒，await/cleanup另有有限等待，超时保留PENDING。

结束检查素材/旧capture hash、预算、真实在途/服务/进程与每方法账本；末尾ps空只证明结束快照，不补方法成功。当前两受控SIGSEGV原OS11与trace缺失分栏保留，status0不能借App trace补11；不自动关闭历史ordinary UNKNOWN。编码能力不支持明确CAPABILITY_BLOCKED，新管线不是正式双轨、显示/声音或跟踪P0。D1未通过，不进入M0。

## 69个具体方法

| 顺序 | 组 | 方法 |
|---:|---|---|
'''+ '\n'.join(rows)+'\n')
print('C13 delivery and 69-method appendix generated from actual review')
