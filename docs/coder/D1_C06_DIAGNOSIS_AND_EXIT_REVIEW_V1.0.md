# C06 诊断、退出准则与限制评审 V1.0

候选：D1-20261005-C06；日期：2026-10-05。状态：方案已实现并完成本机构建，设备 NOT_RUN；正式验收 BLOCKED / NOT_READY。本文提供负责人可评审的退出方案，不代表方案获批或失败已关闭。

## ordinary native abort 与 App 可观测性

C05 原始证据匹配 task029c994a-3360-417e-991f-475f61e31cc1、PID5588、isolated UID99012、CREATE_BEGIN 同步确认以及 native SIGABRT(signal6)。外部 tombstone 的 codec2 枚举调用栈及 Hardware service manager 检查失败只证明该进程本次服务发现阶段 abort；不能推定全局服务停止、权限拒绝或产品隔离成立。App 自身 cause UNKNOWN、trace SHA 空，原严格测试 FAIL。finally 已证明 death/source_released/lease_clear，不应把已确认的释放重写为未知。原文件与哈希见 d1c06/evidence/prior-failure-analysis.json。

[AOSP NativeTombstoneManager 公开实现](https://android.googlesource.com/platform/frameworks/base/+/2d23f53029f06576ba2d7cc04b05e94ac4bffea3/services/core/java/com/android/server/os/NativeTombstoneManager.java) 对 UID 和 SELinux 标签的过滤可解释 isolated 进程 trace 缺失的机制，但未证明该 Lenovo 固件使用完全相同实现。ApplicationExitInfo trace 可缺失；公开证据不足时不能补写 cause。C06 traceStatus 区分缺失、读取失败、匹配失败与已匹配 proto，仍保留 UNKNOWN。没有扩展 TombstoneWitness allowlist、注入外部死因或引入权限绕行。

负责人待决方案：若公共 App API 持续无法取得匹配 trace，可将 ordinary 权限负探针退出为 D1 平台可行性观察，分别记录 App UNKNOWN、外部匹配死因和实际资源安全结果。前提是同步阶段、PID/UID/时间/信号、外部原始证据以及 death/source/FD/lease/noREADY 均可复核；外部证据不能成为 App 自动分类成功。此变更须负责人明确决定并由后续候选修改验收契约；C06 原严格分类方法不变，证据不足仍 FAIL。若完整 App 自主死因是硬性要求，则该平台能力继续 BLOCKED，不能用日志增量宣称修复，也不能反复同条件运行期待 UNKNOWN 自行变 PASS。

## AVI 请求时间采帧

C05 原 AVI 请求10秒，fallback片段9至12秒、片段内1秒；默认10秒无输出样本 watchdog 失败。原日志包含0偏移大量1字节读，取消栈出现 Mp3Extractor.peekEndOfStreamOrHeader，没有 muxer 建轨和输出样本。这支持格式探测/小异步读开销假设，尚不能确定完整根因，不能把取消行为或音轨格式当作唯一证明。

C06 用明确 AVI/MP4 路由选择对应已有 Media3 extractor，仍对实际输入执行 sniff；AVI 不替换为 MP4。采帧独立契约显式移除音频，VideoFrameSink 和 VideoCaptureOutputValidator 验证1视频0音频、H264 256×144、3秒时长、严格样本/PTS及全视频解码 EOS/帧数。该 sink 不实现正式 SinkCoordinator.Host，不发产品 READY/token。正式编辑导出仍要求视频和音频两轨，T01/T02及样本/释放/租约门禁保持；身份核对见 gate-preservation.json。

补测先运行新增 videoFrameCaptureMp4Control，同一独立采帧流水线必须通过，之后才执行原 AVI10秒方法。控制失败时 AVI 依赖项 BLOCKED，其他独立入口可继续。必须保存实际 sniff/init/seek/format/input sample/decoder 创建/muxer 首样本/fsync/validation/frame 的阶段证据，不以阶段日志替代成功。默认无样本 watchdog 仍为10秒；90秒外层、20秒取帧、5秒取消及10秒 source 释放预算见设备追加文档。超时必须保留实际释放和未知资源状态，不能加时、静默切素材或强行清除记录。

成功退出要求原 AVI、原10秒请求、3秒片段通过独立输出验证、片段内1秒取得非空帧，并证明取消/FD/source 状态。请求映射不等于实际原帧时间证明：retriever 实际 source frame PTS 仍 UNKNOWN，转码可能有损，检测质量 NOT_RUN，不能据此通过 P0。

若 C06 仍无样本，保留 BLOCKED 并按实际阶段决定下一方案：可评审已有 Media3 demux 加系统 decoder 的直接 Image/YUV 采帧，需新增实现、真实 PTS、内存上限、取消和资源验证；或评审 C04 条件准入的兼容商用/其他许可解码方案。两者当前均未实施、未准入，不能新增 GPL、权重或未经批准依赖，也不能作为 C06 已修复依据。

## 交接与边界

本机新增22条断言通过，119条历史证据按来源复用，未伪装重跑；26个设备入口均 NOT_RUN。交付报告、完整设备追加文档、本文、4 APK、源码 ZIP 和递归证据清单统一冻结，verify_freeze.py 只读验证。C01至C05和45个原媒体保持不变；不操作设备或删除遗留数据。

单 App/独立 Kit、完整隔离流水线、模型权利、手机回归、真实字幕/音频与复制、标注质量及最终 P0 仍未通过。额外 UID companion 仅 D1 实验。本轮可交接补测候选，不能进入 M0 或宣称正式验收通过。
