# D1 E4A 集中修复独立复审报告 V1.0

日期：2026-10-17 08:10。角色：tester。依据：D1_E4A_TESTER_REQUIREMENTS_V1.0.md 及四份 E4A 正式交付文档。

**结论：SUPPORTED_FOR_CONDITIONED_FINITE_DEVICE_HANDOFF。原 E4-F01/F02/F03 在本轮静态代码及已有有界本机证据范围内均有修复支持，未发现阻止有限设备交接的新问题。实际 Android/MediaCodec/Binder/故障及资源回收验收全部 NOT_RUN；本报告不代表设备通过。D1 未通过，M0 未启动，全部既有 P0 保持开放。**

## 1. 冻结身份与执行范围

| 项目 | 核验结果 |
|---|---|
| 候选 | D1-20261017-E4A |
| 外部冻结 SHA-256 | a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d |
| 源码 ZIP SHA-256 | d28c91ffd35e6cdd2e7976dea6b4d1dc44bb1f3d1b0300740fd9f33275aa04cf |
| 只读 verify_e4 | PASS，201 源文件、207 不可变文件；ZIP 精确成员及内容、来源、签名记录、最终构建输入一致 |
| tester 独立哈希检查 | PASS，207 项全部一致；派生映射中 15 项字节相同、14 项发生变化 |
| 最终 app APK | 10,597,168 B；e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f |
| 最终 androidTest APK | 2,712,637 B；1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be |
| 签名证书 SHA-256 | 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f |

安装目标只能来自 `docs/coder/d1e4a/artifacts/D1-20261017-E4A/final`；根目录 MAIN 产物仅作历史证据。MAIN 与 repair-001 两次离线构建记录均成功，最终修复后 44 项构建输入绑定已核。只读 verifier 的物理读取 143,609,441 B/261 文件，归档逻辑读取 50,264,052 B，无递归展开、媒体读取为零。

tester 本轮仅阅读源码、文档、已有日志与归档并生成报告；Gradle、JVM 自检重跑、ADB、设备、媒体及 native fault 执行均为零。独立证据见 `D1_E4A_EVIDENCE/identity-audit.json` 和 `audit.py`。

## 2. 原问题修复复核

| 原问题 | 结论 | 实际生产调用链与证据 |
|---|---|---|
| E4-F01：失败产物被删，目录存量预算可退款 | SUPPORTED，限本轮范围 | E4Session:163–165 调用 E4FencedTask.abortRetaining；ABORT_PENDING 持久化、原 worker lease 排他 fencing、ABORTED 持久化后保留原文件，没有删除输出。Sink:283–286 在分配任务 guard/输出 FD 前先完成持久预算 R。E4OutputBudget 使用固定 app 私有目录、独立 anchor 与 append SHA 链，R 预留 2 MiB，S 记录 READY/ABORTED 的实际长度与摘要；消耗由历史账本累加，删除文件不会减账。 |
| E4-F02：初始化及 close 双失败丢失实际 owner | SUPPORTED，限本轮范围 | E4Session:126 先保存 Sink 再 open；:285 先赋值纯构造 task 再 initialize。E4FencedTask 构造无 IO，预注册 owner；AndroidLease.exclusiveInto 先将纯 Guard 放入外部 E4Owned，再在 initialize 中保存实际 PFD、获取锁。E4Owned 对初始化失败保留 original、原始异常和 suppressed close 异常，UNKNOWN/CLOSING 不计作返回、不重试 close。预算 Handle 先入 holder 再存 RAF/锁；marker/anchor channel、anchor 读取流、journal 流、目录枚举、identity 流、摘要流均有打开前外部 holder；目录 sync 的原始 FD 保存在 Sink。失败时 opening/holder/预算 marker 共同阻止许可回收。 |
| E4-F03：取消只看一次不可变报告，CONTROL 晚返回导致误判 | SUPPORTED，限本轮范围 | E4Session:169–215 使用生产 E4ReturnGate；被接纳 CONTROL 的计数在实际调用 finally 才扣除，owner 与最后 CONTROL 均尝试唯一 claimFinish。baseReleased 仍需原 source/sink/callback/remote 等全部已证实返回，finishOwnership 完成实际摘要与预算 S 后才可回收许可。query 只观察同一 session，不执行预算 IO，不替代原 owner。E4DeviceTests:126–132 从首次取消起固定 30 秒，在原 await 剩余时间内有界 query，覆盖 CONTROL 已为零而预算结算仍未返回的 PENDING；不续期、不重跑。 |

UNKNOWN 的处理仍是保留：预算初始化、追加、sync 或 close 未证实时保留 operation.pending；原 session 未 drain 不执行 S，新 host 不能重建旧 ticket 结算。anchor 存在而 ledger 缺失、链损坏、另一 pending、容量不足均拒绝。正常结算仅释放未使用预留，已记录的实际字节永不退款。预算累计 4 MiB、单次预留/输出 2 MiB、128 输出记录/256 事件、ledger 128 KiB；输出目录另有 128 文件及元数据 128 KiB 上限。

已有 repair-001 JVM 原返回为 66 条 + 独立新 JVM 恢复 2 条，共 68 条；MAIN 65 条和旧 E4 89 条均不叠加。自检直接使用四个生产核心类，覆盖 7 B 失败文件长度/摘要保留，两个 1 MiB+1 B 消耗后即使删除独立自有 dummy 也拒绝新整额预留，11 B 跨 JVM 恢复，以及 guard 初始化/close 双失败和真实线程返回屏障。它们没有执行 AndroidLease、Android Sink、Binder 或 MediaCodec；预算/目录/摘要等 Android 双失败实际注入仍缺设备证据，不能从通用 holder 自检外推这些路径已经运行通过。

## 3. 架构回归与依赖

E4Broker、E4Protocol、E4CpuAdapter、CodecService/Sink/Wire、Encoder、能力协商及 manifests 均与原冻结对应文件字节相同。六帧 256×144 RGBA、原输入隔离读取、服务 encoder、隔离输出 EOF/PTS/luma/摘要验证和 host 唯一 READY 链未被绕开。原始身份、授权 FD、同步 metadata callback ACK、原 callback/native/lease 实际返回证据仍有效；死亡与 close 未证实不回收许可。另一 CPU 任务的 READ 在死亡前已接纳、实际底层读取在释放屏障后完成的证据边界保留。

`:e4_codec` 同 UID 仅提供崩溃边界，不能声称权限或 RCE 隔离；host lease JNI 以及本轮 Java 文件锁/fsync 的阻塞风险保留。队列 2、consumer/encoder 各 1、CPU slots 2，16 份可达 RGBA 2,359,296 B 加 YUV 55,296 B 是对象估算，不能当作 RSS/驱动池峰值。

最终 APK 七个 native 库与 C14 对应库相同，无 native 重建。E4→E4A 锁文件相同，35 个坐标无增删及配置变更；相对 C14 的 14 个依赖族版本差异仍存在。Media3 1.9.3 与 FFmpeg 8.0.3 的既有范围未扩展。SBOM/签名核验不是漏洞清零或分发许可批准，许可证/SCA 发布门仍开放。

## 4. 有限设备交接条件与未验证项

1. 负责人另行正式派发设备批次，绑定本报告的最终 APK、设备身份、稳定 e4BudgetIdentity、batch、唯一方法、预算与现场状态。本轮不启动设备，也不确认设备当前连接情况。
2. 正常 MP4/AVI、能力拒绝、Binder 拒绝、取消共五项先按条件安排；依赖正常结果的方法必须引用同设备已独立复核的正常报告摘要，APK 只检查摘要语法不能代替外部验收。缺前置、预算不足或未知 owner 时阻塞后续依赖项。
3. 三个 quarantine 方法为三个备选的末尾单用例分支。首个产生 UNKNOWN/PENDING 后，其余保持 BLOCKED；重启 host、改 batch/UUID、换目录、清数据或删除旧产物均不能作为继续测试的办法。本轮不批准重置或自动恢复。八项计划不代表可以在同一未知现场连续执行八项。
4. 记录实际 codec/硬件或软件实现、Image/plane 资源、原身份、回调/CONTROL 返回、source/lease/FD 关闭、预算 R/S/marker、输出 task/长度/SHA 和 OS 资源证据。固定协商 4 次/12 秒、pipeline 60 秒、取消 30 秒；等待超时只能记 PENDING，不能强制回收。输出每次最多三次完整 hash 共 6 MiB，fixture 全八项单次规划前后 hash 共 1,477,098,536 B，不能当作本轮实际读取。
5. 自杀/native-segv 仅测试本 App 控制入口；原始 OS reason/status/trace 独立取证，status=0 或缺失仍 UNKNOWN/FAIL，不能从 App WORKER_DIED 推断信号验收通过。C14 平板功能仍为零，历史 73 项和两个平台限制 NOT_RUN 原样保留。

真实 codec、跨进程取消竞态、FD 转移/close 双失败、系统死亡信号、设备峰值均未验证。Kit/AAR、多 host/Flutter、Surface/音频/图片/字幕/GL 接入及原 J01–J11/P0 门槛没有因此关闭。旧 E4/C14 冻结哈希与既有 FAIL 未修改。本轮无在途执行；后续结论以正式设备原始返回为准。
