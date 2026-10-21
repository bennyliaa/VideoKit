# D1 测试准备

版本：V1.0；日期：2026-10-05；角色：VideoKit tester。

状态：准备完成，等待负责人确认完整候选后派发正式测试。本文件不是验收报告，所有正式用例当前均为 NOT_RUN，无产品 PASS/FAIL 结论。不推进 M0。

## 1. 依据和范围

- [协调规则](../MILESTONE_COORDINATION_V1.0.md)
- [最新项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)
- [D1 测试需求](../milestones/D1_TESTER_REQUIREMENTS_V1.0.md)
- [D1 开发需求](../milestones/D1_CODER_REQUIREMENTS_V1.0.md)
- [公共契约](../PUBLIC_API_CONTRACT_V1.0.md)、[测试验收计划](../TEST_AND_ACCEPTANCE_PLAN_V1.0.md)

最新范围优先：当前只实测 Android API31+ 手机/平板；Apple/Windows 仅审阅兼容性分析，实现测试记 NOT_RUN，不因缺少其环境阻断 Android。D1 是高风险技术验证，不代替后续完整功能验收。

本轮仅阅读文档、manifest 和来源说明、枚举文件长度、编写准备文档。未运行 Gradle、安装 APK、连接或操作设备、探测解码媒体、执行产品测试或修改源码。test_media 保持只读，媒体不上传、不打包。来源与许可信息仅记录本地清单声明，不作为独立核实后的许可结论。

## 2. 候选接收检查

负责人确认整包交接后，先检查 docs/coder/D1_DELIVERY_<candidateId>.md：

1. 唯一 candidateId，以及 D1 七项开发范围 DONE/NOT_DONE 矩阵。
2. 源码/配置标识与 SHA-256 manifest；无 Git 时不使用虚构 commit。
3. APK/AAR 或适用实验产物路径、SHA-256、对应构建任务及自检日志；不适用产物说明原因。
4. 锁定依赖/模型版本、权重 hash、许可和传递依赖资料、实际集成组件列表。
5. 样本相对路径、长度、hash、真实探测结果、轨道/动画/来源及人工标注清单。
6. readAt、Sink、跟踪、资源/崩溃隔离实验入口、故障注入方式、清理方法和证据。
7. 设备条件、已知问题、性能/取消指标决定或待冻结清单。

缺项记录具体拒收理由，交负责人处理，不用反复测试半成品代替完整交接。当前未做候选接收审计，不据此断言 coder 尚未产出文件。

测试期间冻结候选源码/产物，双方不并发运行 Gradle 或操作设备。优先复用候选产物和已有同版本构建证据；独立构建要求或证据不足时才安排必要集中构建。修复结束后使用新 candidateId，执行缺陷验证与受影响回归。

## 3. 已核查样本清单

以下只确认文件存在/长度及清单内容，未独立计算媒体 hash 或验证真实解码。

| 路径（相对 test_media） | 存在/长度观察 | 清单声明与用途 | 未确认覆盖 |
| --- | --- | --- | --- |
| imgs_and_videos/videos/sample.{mp4,mkv,mov,m4v,ts} | 五个文件存在，长度分别为 349102、347331、349129、349090、405892 字节 | manifest 声明 H.264/AAC，约 8 秒，320×180；TS 为 188 字节包 | Android 解码、Seek、完整轨道明细、hash |
| imgs_and_videos/videos/sample.avi | 571412 字节 | 声明 MPEG-4 Part 2/MP3 | Android 能力与错误映射 |
| imgs_and_videos/videos/sample.webm | 217094 字节 | 声明 VP9/Opus | Android 能力与错误映射 |
| imgs_and_videos/videos/sample.m2ts | 522240 字节 | 声明 H.264/AC-3，192 字节包 | Android 音视频能力与错误映射 |
| imgs_and_videos/images/sample.* | jpg/jpeg/png/webp/heic/heif/avif/bmp/gif 九个文件存在；枚举长度与清单一致 | 声明 640×424；GIF 单帧静态；WebP 为 VP8 静态图声明；HEIC/HEIF 为同字节 HEVC，JPG/JPEG 同字节 | 真实 Android 解码、独立 hash、动画与大图覆盖 |
| 03_large_files/large_video_over_2GiB.mkv | 3212959911 字节，大于 2GiB | 大偏移候选 | 实际容器/编码、有效时长、可读取的大偏移有效内容与 hash |
| 04_corrupted_files/corrupted_video.mp4 | 4096 字节 | 损坏样本候选 | 实际损坏类型及预期稳定错误 |
| 04_corrupted_files/empty_video.mkv | 0 字节 | 空输入候选 | 产品错误与资源释放 |
| 02_videos/{cat,dog,fish,lion}.mp4 | 分别 326938034、183479327、332168392、177706639 字节 | 较大视频/物体跟踪候选，名称不证明内容 | 编码、轨道、目标/遮挡等场景与人工标注 |
| 01_images/*.jpg | 12 个文件存在，299～879394 字节 | 普通/异常图片候选，文件名不证明透明或有效图像 | 真实尺寸、EXIF、透明、损坏类型与来源记录 |

视频 manifest 声明素材为 Big Buck Bunny 片段衍生，CC BY 3.0；图片 manifest 声明 hato 摄影衍生，CC BY-SA 4.0。仅限授权测试，不进入产品资源或再分发。manifest 内 decode_validation/full_decode 的 PASS 是已有清单声明，不计 tester 或 Android PASS。

已知缺口：此 GIF 不能覆盖动态 GIF；没有已证明的动态 WebP。没有已证明的字幕/双音轨、无音频、VFR、方向元数据、高分辨率、大图/长图、真人多脸/遮挡/相似物体及人工标注样本。需由候选清单补证或负责人安排补充；未覆盖子项保留 NOT_RUN。D1 不要求提前完成后续全部样本矩阵，但不能以小样本推断对应能力已通过。

## 4. 待执行用例和证据

所有子项执行时独立记录，组级结果不能掩盖未执行或失败子项。

| 用例 / 需求关联 | 步骤和预期 | 最小证据 | 当前结果 |
| --- | --- | --- | --- |
| TC-D1-01 / §5、26.2–26.3 | 对照 manifest，核对长度/hash，再用可信探测与候选实际后端核查容器、编码、轨道、动画；差异明确记录；缺样本子项 NOT_RUN | 样本 hash、探测工具版本/输出、后端实际结果、来源记录 | NOT_RUN |
| TC-D1-02 / §13–14、21、26.1 | readAt 覆盖 >2GiB offset、短读、EOF、零长度、未知长度、负值/越界/溢出、断线、并发能力和在途取消；验证字节准确、稳定错误、取消完成后才复用缓冲、无主线程等待及完整下载 | 注入参数、期望/实际字节、线程/读取日志、调用时序、网络/文件观察、取消耗时 | NOT_RUN |
| TC-D1-03 / §6、8、14、26.2 | Seek 0/25/50/90%及末尾与快速 Seek；切换 generation、取消、重复 release；旧结果不得覆盖新绑定，释放完成后旧 generation 无新访问，在途操作结束且资源归零 | 命令/事件序列、实际读取与画面位置、关闭计数、Surface/解码器/句柄报告 | NOT_RUN |
| TC-D1-04 / §11、17、26.5、27 | preflight 拒绝不足 Sink；注入满盘、write/flush/close 失败、取消及 markReady 竞态/结果未知；失败关闭并幂等 abort，不 ready；成功输出重新打开并验证，ready 不等于业务提交 | Sink 调用时序、输出 hash/元数据/解码结果、源前后 hash/路径、注入和清理记录 | NOT_RUN |
| TC-D1-05 / §10.5–10.7、20、23、26.6 | 审查代码/权重/训练来源权利；离线运行并观察网络/落盘；人工标注对比目标覆盖，纠正后重算，LOST/AMBIGUOUS 可见；缺权利不能认可集成，缺标注/阈值不宣称可靠 | model manifest、标注/hash、覆盖帧/ID switch/丢失统计、纠正证据、网络/文件观察 | NOT_RUN |
| TC-D1-06 / §8、19、21、26.4、27 | 核对预算预留与有界失败；分别注入普通异常、worker 退出、原生崩溃、OOM/死锁/取消失效适用实验；宿主与其他任务保持可用、资源回收；记录峰值和恢复边界 | 进程/任务边界、注入日志、宿主/其他任务存活、资源峰值及释放、取消测量；Apple/Windows 分析单列 | NOT_RUN |
| TC-D1-07 / §25–26、29 | 对齐候选源码/依赖/配置与产物 hash、集中构建和自检证据；提炼 M0 输入/Sink/命令/资源可冻结建议及悬而未决项 | 候选 manifest、构建任务/版本/日志、完成矩阵、接口建议与未决清单 | NOT_RUN |

正式证据逐项包含 requirementId → caseId/子项 → candidateId → 环境/样本 hash → 预期 → 实际 → 日志/截图路径。Fake/注入与真实引擎/设备结果分栏，普通异常不替代原生崩溃。安全约束立即生效；未冻结数值只报告测量条件/分布，不判性能达标。

## 5. 环境与待解决事项

| 事项 | 当前已知 / 下一步 | 对正式执行的影响 |
| --- | --- | --- |
| 完整候选和负责人派发 | 等待完整交接，当前不运行接收测试 | 正式测试尚未启动 |
| Android12 手机和平板 | 用户拥有设备；由负责人在需要时通知开启调试及授权连接 | 真机项在连接后执行；当前未检查设备，不断言不可用 |
| 样本补证 | 字幕/双音轨/动图/跟踪标注覆盖待补；现有非 manifest 文件待探测/hash | 缺少对应样本时子项 NOT_RUN |
| 模型权利与版本 | 等候选 model/dependency manifest | 若无法提供有效权利证据，对应集成/验收 BLOCKED |
| 性能/取消/质量阈值 | 依正式决定；未冻结项先测量提建议 | 不据未冻结阈值出具达标结论 |
| 安全临时输出及注入入口 | 交接包应指定授权目标、配额/故障模拟和清理方式 | 不能满足 Sink/源安全条件时相应用例 BLOCKED |
| Apple/Windows | 当前仅分析，平台实现测试 NOT_RUN | 不阻断 Android 阶段 |

以上是准备阶段的待解决条件，不是已执行测试后的缺陷或正式 BLOCKED 判定。收到候选后才能核实并给出具体阻断原因、已尝试方法和可执行下一步。

## 6. 正式报告和退出判断

正式报告写入 docs/tester/D1_TEST_REPORT_<candidateId>.md，包含候选/环境、逐子项结果、样本与证据、测量值/阈值、缺陷严重度及复现、未执行/阻断原因、修复与回归范围、M0 冻结建议和禁止冻结事项。

源改变、错误 ready、隐私上传、宿主崩溃等关键安全问题立即通知负责人并阻断；其余问题同批汇总。D1 退出由负责人依据完整实验包和独立报告决定，tester 不自动派发 M0。关键 NOT_RUN/BLOCKED 未关闭时不宣称阶段全通过。
