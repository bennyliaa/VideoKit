# INPUT_SINK03 异常边界集中修复交付 V1.0

2026-10-21；候选 **D1-20261021-INPUT-SINK03**；正式任务 INPUT_SINK03_FIX。B03/P2、B04/P2 及同类阶段异常已集中修复，coder 有限离线检查通过。新包独立复核仍 **PENDING**；INPUT_SINK01/02 历史 FAIL 保留；**D1 NOT_PASSED，M0 NOT_STARTED**。

依据 [开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK03_FIX_CODER_REQUIREMENTS_V1.0.md) 和 [完整独立报告](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_FIX_REVIEW_REPORT_V1.0.md)，后者 SHA-256 `c176949cf1c68978bf600ee62997e53360234835f09679ad816fd785db3db71f`。原 B01/B02 指定修复的有限独立通过保留，不扩写为整个新包通过。

## 修复内容

**B03：原取消结果消费一次、稳定脱敏。** 直接原 stage 首次等待和晚结果观察均捕获 CancellationException，与 ExecutionException 一样进入原终局失败消费路径，清除已消费 pending，保留稳定首错，不向调用方传私有 message/cause。WRITE 已进入但无有效字节 ACK 时登记 UNKNOWN reservation 一次；先前 timeout 和 UNKNOWN 不因晚取消/晚成功或清理而退款。SDK没有主动 cancel 宿主原 future。

九阶段 WRITE、FLUSH、CLOSE、REOPEN、VALIDATE、READY、COMMIT、ABORT、QUERY 一并审查。直接阶段用既有 Failures 映射，READY/ABORT/QUERY 原观察回调也在转发原终局结果之前登记稳定失败，保留同一次调用结果，不靠新 RPC 补绿。非法 reopen/validation 结果同样转为稳定失败事实，避免已消费终局结果因类型问题反复悬挂。

**B04：cleanup 首错与正确终态并存。** ABORT/QUERY 已实际进入后的超时或失败立即登记 firstFailure；原 ABORT/QUERY 的晚 ACK、准确 QUERY 证明的 ABORTED、原线程真实返回可更新终态，但不清失败历史。准入前被同原尾段挡住仍是短暂 pending，不伪造业务失败。实际已进入的宿主调用不重发。

本批复查还修复 deadline 边界：若原等待已抛超时，晚 ACK 恰在 catch 处理前完成，不能仅凭 view 当前已完成就漏记历史。现在结合本次实际超时异常和对应原动作准入事实判定；正常 ACK、未发出的 QUERY 不因此误记失败。

**业务 UNKNOWN 收敛与物理返回分开。** 失败/取消的 COMMIT 不等于未执行、已回滚或已成功。原端口可用非阻塞 `Commit.originalOutcome(task, token)` 给出该准确原 COMMIT、相同 task/token 的权威事实；默认 UNKNOWN，继续持有。确认 COMMITTED 与 COMMIT ACK 字段分列，确认 NOT_APPLIED 也不抹掉已发生的 READY 或首错。该方法不能执行/重试 RPC，不能用线程返回、取消或无 ACK 推断业务结果。

同理，已进入 QUERY 的 ACK 失败后，宿主可通过 `HostOutput.originalTerminalStatus(task)` 提供该原任务原仲裁/原查询的准确终态；默认 UNKNOWN。只在全部同原任务物理返回后接纳权威事实。Android authority 同样明确此可选契约。测试使用真正执行受控 COMMIT 和其原宿主查询的原线程，查询 ACK 早到、查询尾段未返时仍不收敛或释放。未提供有效权威证明则继续保管，不假装泄漏已消除。没有增加 executor、资源 ledger、诊断框架或自动查询/重试机制；这些仍是临时候选接口，非 M0 定版。

生产改动仅 TemporaryOutput、HostOutput、AndroidGrantedStream；原 SinkCoordinator、输入适配、桥/registry、成熟 muxer、依赖/native/外部 host 均未改。[源码差异与补丁](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/source-differences.json)。

## 实际验证

| 套件 | 最终源码路径 / production JAR 优先路径 |
|---|---|
| 原20语义组 | 两条路径均通过；A01/A02及原输入/输出正常分支保持。 |
| 原17尾段场景 | 两条路径均通过；保留 B01/B02 和同原 keeper/thread 实际返回门。 |
| tester原23场景 | 两条路径均通过修复后的安全断言：12项原独立检查和1项读回 registry 检查原样复用；6阶段即时取消、1项晚取消、3项失败历史按新安全断言回归。原十个失败日志和原复现源码另存 reference，未改写。 |
| 阶段异常矩阵 | 两条路径各63项：9阶段×7种结果。每阶段包括正常ACK、ExecutionException、直接CancellationException、timeout后晚成功/晚失败/晚取消、调用内直接抛取消。实际原动作线程、ACK、尾段、抛错的归还 authority、业务UNKNOWN和最终真实清理分别核验。 |
| 输入受影响回归 | 两条路径各5项：open/read取消、权限错误脱敏、原close取消失败保管与显式原API恢复、cancel后同原晚取消不写caller。输入生产代码未改。 |

以上套件存在有意重叠，不相加冒充新增独立场景；源码和 JAR 双执行也不当作新增场景。新结果仍为 coder 回归，不能代替 tester 独立判断。

最终源码编译 **local-005**、完整源码套件 **suites-004**；最终 JAR 优先套件 **suites-005**。每个原 JVM exit、argv、stdout/stderr、源 pins、生产 JAR SHA、classpath 优先顺序留存；关键套件输出实际 ORIGIN。全部有限 gate 释放、同原线程 join、source/output keeper 最终归0；测试异常清理同样检查准确 owner，不靠退出 JVM 假装归还。受控 COMMIT UNKNOWN 在准确原 authority 给出结果前保持 retained，原查询线程尾段未返也继续持有。

原 A01：同 Provider 跨 factory 门、旧 epoch 原归还后新 range、单源读峰值1/queue0、双源总预算保持。A02：先 ACK3，再实际写7后失败，physical10/ACK下界3/callerPos3、private block、首错和 UNKNOWN 保持，不重发/回退/退款。晚取消矩阵实际写4而 ACK下界0/callerPos0/UNKNOWN4，不能把失败 ACK 当作实际0B。

[最终源码套件](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/suites-004/matrix.stdout)、[最终生产套件](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/suites-005/matrix.stdout)、[完整验证索引](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/batch-validation.json)、[阶段异常矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/phase-exception-matrix.json)、[原状态观察](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/original-phase-observations.json)、[19项映射](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/independent-regression-map.json)。S01/S03/S04/S06的新 coder 有限修复结果待独立复核，S05实际平台路径仍 NOT_RUN。

## 构建、依赖与历史

严格离线实际 Android/Media3 1.9.3 ABI 构建最终 **build-main-002** 成功，33 tasks：4 executed、29 up-to-date。最初 build-main-001 也成功（33 executed），随后同类 deadline 竞态修正使其成为非最终记录；保留 superseded.json、原日志/原产物哈希，再以最终源码必要重建，没有用旧构建冒充新源码产物。锁/metadata未写入新值。

15 runtime 坐标、两锁文件、verification XML、实际 JVM deps 与旧包逐字节一致；strict verification、verify-metadata=true、LockMode.STRICT 保持。最终296实际验证项：121 binary、35 module、140 POM，无新 pin/版本/binary 下载。三依赖原有限离线身份/Apache许可准入沿用 tester 旧结论，不扩大到 release、平台或本新修复独立准入。原官方 metadata/许可材料保留于 reference/licenses。

INPUT_SINK02 316项及此前2033项，共 **2349旧冻结文件** 和各原 seal/ZIP 逐项哈希不变。旧报告、旧失败和 UNKNOWN 没有删除或改成通过。

[最终构建](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/build-main-002/receipt.json)、[实际依赖](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/actual-consumption/summary.json)、[依赖许可差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/dependency-license-difference.json)、[历史保全](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/frozen-baseline-preservation.json)、[最终源码/依赖输入](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/final-source-dependency-inputs.json)。原 deprecated API 提示保留在编译 stderr，不冒称零提示。

## 冻结身份

| 文件 | 字节 | SHA-256 |
|---|---:|---|
| [production JAR](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/artifacts/input-sink03-classes.jar) | 87238 | `f053ad930c2f5cdaadc60cfe9157d190212e1f0b2620d0f04631af06382d00ab` |
| [compile probe APK](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/artifacts/input-sink03-compile-probe-debug.apk) | 6396874 | `aab5754708e29f58ed0c1452db71895bf655eb0e9c363020a985271636bd3a20` |

APK为 com.videokit.d1input/versionCode3/versionName D1-INPUT-SINK03/min31/target36；无权限、组件/native/test helpers；未安装。固定本地 apksig/JDK v2 验签通过，证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。[产物审计](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/artifact-audit.json)。

[完整 ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261021-INPUT-SINK03-source.zip) 与 [seal](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/input-sink03-freeze.json) 为最终交接入口；seal记录全部文件和ZIP的字节/hash，seal自身hash在负责人交接消息提供，避免循环。ZIP排除镜像/Gradle缓存/JDK/SDK/编译classes，包含实际 JVM依赖、全部实际 metadata、源码、完整原日志、状态模型和产物。

## 未结范围

真实 Android FD/fsync/codec/muxer、媒体容器/内容/timeline验证、宿主真实 COMMIT/发布仍 **NOT_RUN**。受控4B文件、JVM异常和临时host authority不能代替实际平台效果。SDK/ADB/5037/设备/占用/旧handle查询0，无native或外部host构建，未生成或启用执行许可。历史 P0/J11危险链、UNKNOWN、C13 FAIL、FFmpeg/release/model/media许可等裁定不变。

请负责人仅据完整冻结新包派发 tester 集中独立复核；不逐问题交接、不自动下一批/M0，不在冻结包原地修补。独立入口见配套 [复核计划](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK03_INDEPENDENT_CHECK_PLAN_V1.0.md) 和 [异常状态模型](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK03_EXCEPTION_MODEL_V1.0.md)。
