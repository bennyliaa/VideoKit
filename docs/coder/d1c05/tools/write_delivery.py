"""Generate C05 documents from audited identities; no Android execution."""
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c05';e=base/'evidence';docs=root/'docs/coder'
rows=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks']
table='| 冻结文件 | 字节 | SHA-256 |\n| --- | ---: | --- |\n'+'\n'.join('| '+Path(r['path']).name+' | '+str(r['bytes'])+' | '+r['sha256']+' |' for r in rows)
methods={n:re.findall(r'@Test public void (\w+)\(', (base/'device/com/videokit/spike/c05'/n).read_text(encoding='utf-8')) for n in ['C05DeviceTests.java','C05IsolatedDeviceTests.java']}
delivery="""# D1-20261005-C05 开发交付

日期：2026-10-05；状态：BLOCKED / NOT_READY。本轮C05所有设备项目NOT_RUN，没有ADB、设备操作、安装或M0发布。依据D1_C05_CODER_REQUIREMENTS_V1.0.md；C04平板23入口20PASS/3FAIL仅是旧候选的限定证据，不移作C05通过。

## 三项缺陷矩阵

| 需求 | 根因事实与代码处理 | 当前状态 |
| --- | --- | --- |
| TABLET-C04-01 普通broker SIGSEGV/HANG | 旧SIGSEGV分支sendSignal后立即return true，RPC成功和死亡竞态静态明确；改为自有JNI解除当前线程SIGSEGV屏蔽、同步raise并永不返回RPC，保留Android crash handler，不用SIGKILL兜底。ENTERED与ARMED/WAIT_BEGIN分别同步ACK；SIGSEGV需PID/isolated UID/开始时间匹配的OS signal11证据。HANG和SIGSEGV各自独立方法并带NORMAL前置，不再相互遮蔽。finally无论断言成败均核对Binder death与实际Source排空 | 实现/23条本机反例准备完成；实际native信号与超时设备NOT_RUN，未关闭 |
| TABLET-C04-02 ordinary codec无原因死亡 | C04宿主UID过滤日志缺isolated死亡cause，根因未知。C05 lease/create/release阶段经task/epoch/UID/PID认证并同步ACK。Java codec调用异常与协议ACK异常严格分开；Java失败记录类型与原cause。native死亡仅实际CREATE_BEGIN、匹配OS SIGABRT、匹配PID/UID的tombstone allowlist具体原因才归类NATIVE_ABORT_WITH_CAUSE，不称codec权限拒绝。无法解释的WORKER_DIED仍FAIL。finally独立检查死亡、Source、真实FD/lease与abort，无论分类失败都留最终状态；未知保留quarantine | 原平台根因BLOCKED；C05只是更准确的诊断/判定与释放路径，设备NOT_RUN，不把新增日志当修复通过 |
| TABLET-C04-03 AVI10秒空帧 | C04AVI retriever视频尺寸null、scaled/unscaled空，而MP4控制与Media3 AVI播放正常，支持平台容器取帧缺口推断但未证明具体native原因。增加现有已审查Media3 Transformer对原AVI 9～12秒片段实际转H264/AAC 256×144/3秒；同T01全验证后在所得MP4请求1秒OPTION_CLOSEST，对应请求原AVI10秒。直接AVI路径仍先执行；仅稳定空帧错误触发fallback，不吞native超时/资源未知。无新依赖或0秒/空Bitmap替代 | 新AVI实际管线设备NOT_RUN；绝对source frame PTS UNKNOWN，转码可能有损，检测质量NOT_RUN；若实际转换/取帧失败继续BLOCKED |

普通broker不持有输出Writer FD，其lease是宿主Source真实账本；实际媒体worker的Linux flock输出lease门禁独立保留。仅进入mode、任意IOException或测试cleanup kill不足证明指定SIGSEGV。系统历史退出记录可能不可用/丢失，此时保守失败，不伪造。

## 验证与保留

C05新增23条本机断言PASS：匹配/错误PID与UID、未知abort原因、截断/超限protobuf、阶段顺序/重复、无原因死亡拒绝及10秒时间映射/溢出。Android native信号、历史退出API与AVI取帧均未运行。现有47合同+24恢复+12验证+7控制+6传输（96条）复用C04冻结证据，未重跑；来源hash和11项源/门禁身份比较见c04-evidence-reuse.json。既有不同UID companion实际sample后SIGSEGV与普通broker实验是不同路径。

正常宿主导出/T01/T02、即刻cancel/账本恢复与全部8项companion实际sample/FD/并行/跨owner测试源除C05命名空间外保持一致；AuthorizedSink、FdOutputMuxer、AndroidOutputValidator、OutputValidationRules、FencedTask一致，gate-preservation.json仅静态确认。严格两轨、PTS、解码、注入stage/hits/cause不放宽。

最终离线strict构建PASS：Debug、AndroidTest、实验worker Debug、unsigned Release、testDebugUnitTest。见c05-final-build.log；前一集中构建也通过，最终重建原因是防止把ACK失败误分类为codec异常。最终测试包另由c05-final-test-apk-build.log验证PID/UID及cancel-return诊断措辞，所有冻结件取最后复制件。任务成功不等于设备覆盖。配置help探针预期拒绝受限connected/UTP请求，无设备动作。JNI仅自有Android ARM64/API31 signal/flock适配，静态符号与APK strip来源可核对，实际运行NOT_RUN。

App346/worker95个锁定坐标无新增；已审查供应图、OSV47个advisory及16个匹配组件的工具限制沿用，不是重新扫描或已修补。不引入GPL、FFmpeg或未知模型。闭源替代许可/单App独立Kit/P0方案仍参照冻结D1_C04_ISOLATION_AND_AC3_OPTIONS_V1.0.md；companion仅D1实验，不批准产品额外安装。C05片段取帧仅host Debug可行性路径，不是已隔离的最终检测/遮罩流水线。

"""+table+"""

固定目录docs/coder/d1c05/artifacts/D1-20261005-C05，源码ZIP、source-manifest.json与freeze-summary.json列出全部源/证据/产物hash；git_commit=null。为避免循环身份不在报告内嵌自身或ZIP hash，以冻结清单为准。verify_freeze.py只读核对源码ZIP和当前文件。C01-C04冻结候选与45个源媒体hash一致；可变根配置切到C05不修改旧快照。

25入口集中补测见D1_C05_DEVICE_APPENDIX_V1.0.md；技术依据/限制见D1_C05_DIAGNOSIS_AND_LIMITS_V1.0.md。三项均未按编译成功关闭。手机AVI/SRT、无声和Windows传输工具设备验证仍待后续同机补测；平板人工有声不推断手机能力。模型权利、标注质量、平台/NAS能力、native OOM/并发及完整P0未闭合，不进入M0。
"""
appendix="""# D1 C05 设备追加批次 V1.0

candidateId：D1-20261005-C05；16+9=25入口准备完成，全部C05设备NOT_RUN。由负责人整体选定候选后tester集中执行。Coder本轮不接触ADB/设备。保留C03/C04已有包、fixture、账本、lease、输出及电脑恢复备份；先确认实际安装候选、同签名、设备/API/ABI/serial、可用空间和现有数据用途，未知数据不覆盖。不自动卸载/清数据/恢复旧版本，不用Gradle connected/UTP/managed设备路径。ARM64/API31+。

"""+table+"""

只用冻结复制件，三份debug APK同签名；unsigned release不安装。worker是额外不同普通UID的D1实验，不是单App产品方案。签名/manifest/ABI见apk-audit.json及各APK证据。

## 源与复制

C05读取files/d1_c05_fixtures的固定别名basic.mp4、subtitle.avi、subtitle.srt、large.mkv。电脑源45项保持hash，FIXTURES在transfer_fixtures.py和media-inventory.json；SRT为1445 cues/GB18030兼容GBK，源不重写。

可由tester在数据审查后复用已有C04副本：先重新核验可信源长度/SHA，再复制到新C05私有目录并核验目标，不修改C04目录；此路径不能算Windows传输工具设备通过。若测试Windows路径，transfer_fixtures.py默认PLAN_ONLY；实际执行需显式serial、--execute、--device-and-installed-c05-reviewed、--overwrite-c05-fixtures-reviewed、docs/tester内--result-file；仅固定aliases。未知目录、空间不足（请求总量+最大单文件+256MiB）、长度/hash不符均停止。32KiB shell-v2 raw流先.c05-part再核验提交，不用exec-in/tee；工具不管理server/安装/清理。电脑>2GiB协议证据为复用，不代替实际设备复制。

## 批次顺序与证据

1. 先realEncoderOutput和isolatedActualEncodeAndReadyRecovery正常前置，再完整T01/T02及全部实际sample恢复批次；不能用普通探针失败跳过已通过实际管线复验。T01 H264256×144/AAC、各轨独立非零样本、3秒±150ms、严格PTS、完整视频decoder/EOS/帧数/末PTS。T02 write/flush指定stage、hits=1、ExportException精确D1_INJECTED_OUTPUT_WRITE/FLUSH，flush已有字节；validate编码/fsync后非零字节与精确OUTPUT_VALIDATION_FAILED。无关codec/source失败不算注入PASS。READY丢响应同task/token查询；abort保留READY。
2. 普通isolatedWorkerDeathAndTimeout本轮只测NORMAL/PRESSURE/EXIT。isolatedBrokerSigsegvIndependently和isolatedBrokerHangIndependently各自先NORMAL，再独立目标模式；即使一项失败也继续执行另一项并单列结果。ENTERED hits=1加对应SIGSEGV_ARMED/HANG_WAIT_BEGIN/EXIT_ARMED同步ACK，非宿主UID/PID。SIGSEGV不能返回普通RPC，必须实际Binder death及匹配OS退出signal11；cleanup SIGKILL、无历史记录或错误PID/UID均不PASS。HANG必须实际WAIT_BEGIN、精确WORKER_TIMEOUT、有界等待和实际死亡/Source账本排空。记录finally实际状态；普通broker不证明真实媒体输出lease。
3. ordinaryIsolatedCodecOutcomeDoesNotReady替代旧Denial方法。记录实际task/epoch、HELLO UID/PID、LEASE_ACQUIRED/CREATE_BEGIN/END、typed Java cause或native死亡、RELEASE_BEGIN/END/FAILED。仅Java codec调用异常且对应同步阶段，或CREATE_BEGIN后具体匹配tombstone cause的SIGABRT，才能记“调用失败/native abort事实”；不能称已证codec权限拒绝。AVAILABLE、RELEASE_UNKNOWN、ACK/bind失败和未解释WORKER_DIED均FAIL。即使断言失败仍执行finally：death、Source实际released、FencedTask独占lease可取后abort、无token；释放未知quarantine，不清除材料。
4. 系统退出记录在App内查询；若trace缺失/超256KiB/不匹配/无allowlist原因，保持UNKNOWN失败。不得用宿主UID-only日志解释isolated native死因。tester按当前方法、PID、isolated UID及阶段有界保存所需crash/协议日志，排除旧同UID记录。OS循环历史记录可能丢失，不能捏造权限原因或用其他进程tombstone。原native trace含路径，App只保留SHA与固定cause；需更广原因分析由tester保留原始证据，下一整批审查，不扩大当前allowlist。
5. offlinePlatformFaceFeasibility先MP4 2秒控制，再原AVI10秒scaled/unscaled；仅FRAME_AT_REQUESTED_TIME_UNAVAILABLE允许转现有Media3 AVI 9～12秒片段，经T01完整双轨/decode/fsync/READY门禁后请求转换MP4的1秒OPTION_CLOSEST。不能换原片0秒、空Bitmap或仅MP4结果。记录source AVI、clip_start/end、requested_source=10000000、requested_clip=1000000、actual_source_frame_pts=UNKNOWN；非空才检测，quality=NOT_RUN。转码可能有损，不代表精确源帧/检测质量验收。若转换或取帧失败保留完整cause/账本，记FAIL/BLOCKED。
6. 取帧/转换分别20秒/90秒、主线程5秒、输入排空10秒；单次native无法硬停时保留资源事实。frame片段输出和.task均保留证据，不自动删除；最多两份缓存记录，达到预算FRAME_CLIP_CACHE_BUDGET_REVIEW_REQUIRED，由负责人审查后处理，不清未知文件。graphics释放未知或Source未排空均不算通过。原AVI源不得修改；新cache输出不是额外fixture替代。
7. companion sample后cancel/EXIT/SIGSEGV、第二槽存活、实际host死亡与跨owner恢复、native dup-close均保留：实际H264 sample后故障、确定死亡/Writer lease释放后才删未READY、第二输出完整验证/READY、同task/token恢复，未知lease隔离。普通broker与companion SIGSEGV单列，不相互代替。
8. 完整MP4/AVI无SRT/AVI SRT/MKV ASS播放及手机追加保留C04门禁：prepare/Extractor/字幕/main/seek有界诊断，Source真实排空，5次seek/字幕开关。自动静音只验结构；同一手机MP4/MKV手动volume=1、轨道支持/选择/renderer/session/focus及人工听音才判声音；平板有声不关闭手机。字形/同步/ASS全样式、实际frame PTS和检测质量未证据则NOT_RUN。

## 全部入口
"""
for name,items in methods.items():appendix+='\n### '+name+'\n\n| 方法 | C05执行 |\n| --- | --- |\n'+'\n'.join('| '+x+' | NOT_RUN |' for x in items)+'\n'
appendix+='\n记录候选hash、serial/API、fixture hash、时间、实际stage/hits/cause、Source/FD/lease最终状态与逐项PASS/FAIL/BLOCKED/NOT_RUN，写docs/tester自身目录。不得据C04的20PASS移作C05成功，不自动停止后续独立方法；依赖前置失败单列BLOCKED。整批结束统一报告，保留失败材料，无M0验收。\n'
for name,text in [('D1_DELIVERY_D1-20261005-C05.md',delivery),('D1_C05_DEVICE_APPENDIX_V1.0.md',appendix)]: (docs/name).write_text(text,encoding='utf-8')
print('two C05 documents', {n:len(v) for n,v in methods.items()})
