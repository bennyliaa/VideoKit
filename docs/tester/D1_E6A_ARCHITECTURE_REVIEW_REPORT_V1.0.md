# D1 E6A 独立静态复审报告 V1.0

日期：2026-10-17。Tester。依据 `docs/milestones/D1_E6A_TESTER_REQUIREMENTS_V1.0.md`，审查完整冻结候选 D1-20261017-E6A。

## 结论

**REVIEW_WITH_P2_NOTE。发现 1 项 P2：E6A-F01。** E6-F01、E6-F03 的修复得到源码及已记录的直接生产边界有限证据支持；E6-F02 的来源/验证器归属修复得到支持，但公开验证入口的创建前异常仍有一处未启动状态遗漏，不作三项全部关闭。

正常回归在技术上可按原严格门另行正式派发，并附上述 P2；本报告不启动设备。若负责人仍要求三项集中修复全部完成后再部署，应先处理 E6A-F01、冻结新候选再复审。E5C-REG-F01/P1 仍待 Android 正常 MP4 完整 READY 证据，原 FAIL 不改。D1 NOT_PASSED、M0 NOT_STARTED；全 P0、框架许可及旧未完成项保持。

本轮 Tester ADB/设备/安装 0，原媒体及导出件读取 0 字节，Gradle/native/Java 模型重跑 0。无在途设备任务，未修改 coder 冻结、旧报告、账本或设备数据。

## E6A-F01：公开验证入口的时间线预检未归入已知未启动诊断

优先级 P2，属于 E6-F02 的剩余缺口。静态定位：

- `android/com/videokit/spike/c14/E4CpuAdapter.java` 的公开 `validate(Context,...)` 先执行 `offMain(); PipelineRules.timeline(timeline)`，随后才进入创建 CpuTaskClient 的 try/catch；预检异常没有包装成 E6AFailure。
- `android/com/videokit/spike/e4/E4Session.java` 在调用该入口前执行 `nativeDiagnostics.validatorEnter()`，把字段设为 `phase=VALIDATION_ENTERED start=UNKNOWN`。
- `src/com/videokit/spike/e4/E6ADiagnosticState.java` 的 failure 仅在 cause 链发现 E6AFailure 时覆盖字段。原始 `PIPE_OUTPUT_TIMELINE` IOException 不满足此条件，因此公开入口的坏 timeline 路径保留 UNKNOWN，而事实是尚未创建/启动验证器；也缺少准确 TIMELINE/NOT_CREATED 归属。

已有 `F01_INVALID_TIMELINE_OWNED_RESOURCE_CLEANUP` 用例直接调用内部 `validate(ValidationOwner,...)`，能验证已拥有资源时的清理和 TIMELINE/NOT_STARTED，但没有经过上述公开预检。它不能证明公开路径的状态精度。

建议将公开入口已知创建前的校验错误也携出准确 VALIDATOR/mode11/TIMELINE/NOT_CREATED/start=NOT_STARTED 诊断，保留原始首错，并增加直接经过该公开边界的有限负例，证明未创建/未启动。不要为取 task 而提前创建资源。

本项仅由源码控制流确认，没有新执行模型或 Android 复现。正常 E4Session 在该调用前还执行原 E4Protocol.timeline；固定正常样本未发现因此新增的运行失败或验收放宽，不升级成正常回归阻塞故障。

## 三项修复的逐项审查

| 原问题 | 本次审查 | 证据与限制 |
|---|---|---|
| E6-F01：后置 Java/cleanup 失败丢 native 背景 | STATIC_FIX_AND_RECORDED_BOUNDARY_SUPPORTED | 实际共享 validate 流程在 native、stop、close、digest、真实 receipt/content/thumbnail 失败时从实际接收器取 snapshot；E6AFailure 保存原 Throwable/cause、按序 cleanup/suppressed，未返回成功 Verification。stop/close 未返回则保留 verifier。已有直接生产边界负例支持；Android 失败链 NOT_RUN。 |
| E6-F02：源错误误填 validator | PARTIAL_FIX_SUPPORTED，剩余 E6A-F01 | 实际 next 失败包装 SOURCE/task/mode10；session 专用路由分别更新 source/validator，源失败时 validator 保持 NOT_STARTED。成功分别携出自身 task/snapshot，创建失败准确 NOT_CREATED。公开入口创建前 timeline 异常例外如上。 |
| E6-F03：并发首份发布非原子 | STATIC_FIX_AND_RECORDED_BOUNDARY_SUPPORTED | 实际 Binder 分支传真实调用者及 Parcel 数据给完整 receive；PID/UID/task/epoch/revoked/size、schema/尾数据/stage/frame 一致检查完成后才 CAS。不可变首份、无 reset，DONE/ERROR 读取同一接收器。已有 16 并发调用 1 发布/15 拒绝，首对象保留；Android Binder NOT_RUN。 |

source 的 mode10 提取计数不作 mode11 完整输出验收。native OK 仅背景，不替代 Java 首错、清理或 READY。ENTERED 只描述进入相关调用，不作真实进程 STARTED ACK；在途状态 UNKNOWN 与已知创建前 NOT_STARTED 应分开。

## 有限执行证据的适用范围

核对 `evidence/local-check-results.json` 的输入大小/hash、两条命令及原始日志，最终 `boundary-run-005.log` 为 **20 用例、112 断言**，没有重跑。001 为 Context shim API 缺失编译失败；002 为 18 例；003 为 20/111；004、005 为 20/112。历史结果不叠加为本批新通过数量。

工具直接执行生产 E4CpuAdapter 的共享 next/validate、真实 PipelineValidationReceipt.prove/View、原 PipelineRules 内容和缩略图规则、完整 E6ADiagnosticInbox.receive、实际 E6ADiagnosticState 路由组件。公开生产包装使用真实 CpuTaskClient，未发现测试分支或复制成功算法。digest/receipt/content/thumbnail、stop false/throw、close throw、native 首错与两项 cleanup、正常 validator、源错误、所有权窗口、非法首份及并发首份均有对应原始记录。

替身模拟 start/stop/close/lifecycle 与 Context/Looper/Log；有限检查使用旧 E6 支持类，但本次边界及纯生产规则按列明输入重新编译。未执行完整 E4Session/Android Parcel/Binder/JNI/MediaCodec，替身中的死亡、FD/slot 归还不能作真实系统事实。session 接线和最终双 APK DEX 字段以静态核对补足，不能把它算成完整 session 运行。公开预检未覆盖的缺口单列，不受 20/112 掩盖。

## 冻结、构建和来源核验

Tester 独立核验脚本及结果：`docs/tester/D1_E6A_EVIDENCE/audit.py`、`identity-and-recorded-static-audit.json`。读取元数据、源码、包和已有日志，不读取媒体、不运行候选代码。

| 项目 | 结果 |
|---|---|
| 包外 seal | SHA-256 `520f980b0523e1c70c6841747ed0170b28a31363874a9b54f66e8684e21411e7` |
| 源码 ZIP | 18,579,419 字节；SHA-256 `702a3e560fa659a5d960e8bfe4ef60fb8fd3914ee24e2ec42dd48e71d139a8d6`；222 项有序成员逐项大小/hash 一致 |
| 冻结项 | 228 项大小/hash 全通过；原 E6 254 项仍一致 |
| 最终构建输入 | SHA-256 `1d4f86663e8e016b3c175ea7df1cbb9f1a1f64b6b0e77a810000ab7fd073ace0`；绑定 repair-001；main-001、repair-001 原离线日志均 BUILD SUCCESSFUL |
| app-debug | 10,726,269 字节；SHA-256 `3d1ab7b287a089217d22be43184cc5d3f94b1a136d6c80ef192a92026ee1a134` |
| androidTest | 2,718,669 字节；SHA-256 `ea3c95bc774204651bc8defc5084890694a192e8273e543ea37e040f6a9a9d69` |
| 版本及签名 | versionCode7/D1-E6A；两原始签名核验记录均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；本轮只复核记录，不重跑签名工具 |
| 集成 | 双最终 APK DEX 均含 sourceNativeDiagnostic/validatorNativeDiagnostic；本机 E6ABoundarySelfCheck 未入包；测试改动仅增加 source 字段采证，原断言未放宽 |
| 原生与依赖 | 七 native 与 E6 APK/来源文件逐字节相同；源码/header/config 一致；35 Maven 坐标锁无变化，Media3 1.9.3/FFmpeg 8.0.3 保持；本批无 native 重建 |
| 严格门 | E6Muxer、E4CodecSink、PipelineRules、guard/recovery/final observation/生命周期/稳定账本代码逐字节继承；六帧、1000us、完整 EOF、画面与绝对 deadline 不变 |
| 对齐 | 独立解析七 ELF PT_LOAD 及 APK 本地文件偏移，静态 16KiB 条件通过；不作 Android 16KiB 实测结论 |

四文档、完整来源、SBOM/NOTICE、精确 diff、修复前后输入和构建记录齐备。E6 封装修复及其旧 Media3 回放仅继承既有证据，本轮没有重新读取失败输出或回放媒体；许可、安全扫描与正式框架交付不在此静态结论内。

## 设备与账本边界、下一步

本报告没有新增设备事实。原 N2 已结算 ABORTED/0 字节并归档，旧 close ACK=false、原无帧原因 UNKNOWN 不改；后续 E5C 失败输出 53,651 字节已计入稳定预算 `730a73e1-50e1-4198-a515-047104f00e31`，不得清账、删除产物或更换预算身份。当前无 pending 的事实沿上份设备报告，本轮不读取设备重新证明。

已审 E6A 待派计划为 HA1Q6WXR/user0、同签名保数据部署精确 final 双 APK，然后按 MP4 → AVI → 能力拒绝 → 条件 cancel 单方法/独立新 host。每新 host 仍实际执行原最终观察；不得先部署 E6，不新 QUERY/ABORT/独立 OBSERVE，不重跑一次性 fixture。稳定预算、原 53,651 消费、原 N2 归档和测试源连续性保留。任一失败即停，不自动重试或进入后项。

条件 cancel 的占位符必须由本批同设备两个正常完整结果独立审证后的新报告 SHA 替换；不能使用旧正常、交付或本静态报告 SHA。两正常需真实六源/六输入/六 samples/完整六输出、PTS/EOF/内容/缩略图/READY，以及实际源、CPU、codec、FD、slot、CONTROL、owner 归还和唯一 R/S/无 pending。新正常设备结果及剩余 P2 的处置由负责人正式派发，本轮不自动进入。
