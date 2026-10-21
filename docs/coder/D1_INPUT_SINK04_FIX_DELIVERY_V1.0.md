# INPUT_SINK04 宿主结果边界集中修复交付 V1.0

2026-10-21；候选 **D1-20261021-INPUT-SINK04**；任务 INPUT_SINK04_FIX。B05/P2、C01/P3及同类宿主返回边界已集中修复，coder有限离线验证通过；新包独立复核 **PENDING**。旧INPUT_SINK01/02/03整包FAIL、原B01–B04与A01/A02有限独立通过及历史UNKNOWN保留；**D1 NOT_PASSED，M0 NOT_STARTED**。

依据 [开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK04_FIX_CODER_REQUIREMENTS_V1.0.md) 和 [完整复审报告](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_FIX_REVIEW_REPORT_V1.0.md)，后者SHA256 `dfd9266819457f5d153d1a1d0c4d34fa65e7ee19e06b5e3cd027ad3d2172b5f3`。本批一次性交接完整包，不把正常自测或依赖通过当作独立关闭。

## 修复结果

**B05：先校验同原结果，再更新业务事实。** QUERY结果必须是非null Status、合法非null状态、相符状态/token组合。READY token须是非空、不全为Character.isWhitespace空白、无ISO控制字符的String；其他状态不得携带token。已经确认的READY token不能被替换，READY/ABORTED不能相互覆盖或倒退成WRITING；UNKNOWN只表示缺少新证明，不清既有事实。

非法QUERY不再抛原始NPE，不发布空token的READY，也不据其释放owner。它被同原缓存view以稳定 `OUTPUT_INVALID_HOST_RESULT` 失败消费，firstFailure保留，实际副作用仍可能未知；没有准确同原业务事实和真实原任务归还就继续保管，不重QUERY/ABORT求绿。已发生的正确ACK/业务终态不会被伪回滚。

同时防御候选SinkCoordinator副本：共享纯状态/token谓词，READY/ABORT/QUERY结果先检查实际类型/值；null结果、错类型或直接取消均转稳定错误。未新增executor、释放ledger、验证计数或资源框架。

**同类边界集中处理。** WRITE ACK仅接受1..原请求count的Integer，非法ACK不更新SDK确认下界或caller position，UNKNOWN只按同原请求登记一次。FLUSH/CLOSE/COMMIT/ABORT的Void成功必须为null；错误类型不能借泛型桥转换成悬挂或假成功。REOPEN和validator继续校验句柄/长度/完整读回/摘要，以及本契约已有task/bytes/hash/kind/structural字段；非法receipt在消费时拒绝。constructor在owner准入前校验授权元数据并脱敏getter异常；原task只捕获一次，后续动作不能因宿主getter改变而静默改绑。

readonly terminal authority使用相同状态/token与转换规则；COMMIT readonly outcome的null/异常不成为成功，默认UNKNOWN继续保管。已确认COMMIT/NOT_APPLIED仍须准确同原task/token、原authority及物理返回；ACK、业务事实、首错、字节UNKNOWN分别保留。

**C01：复核目录由当前候选推导。** `local_check.py`根据 `d1input-sinkNN` 推导本批 `D1_INPUT_SINKNN_REVIEW_EVIDENCE`，使用规范化路径的子目录关系判断；仅允许同本地盘、正确新根内的新子目录，拒绝旧根、候选内路径、伪前缀、越界/相对路径、根目录本身和重用目录。目标拒绝时不创建文件；不改旧冻结工具。冻结模式还逐项核验所编译源码的seal身份。

新增 `review_all.py --output <新目录>` 直接调用该真实入口并完成源码/production JAR双路径检查，输出原argv/退出回执。它沿用同样的新根限制，不复制修改冻结脚本、不临时绕过断言；冻结时先核完整seal文件身份。工具执行不是独立审查结论。

生产改动仅 TemporaryOutput、Failures、候选SinkCoordinator副本；HostOutput/AndroidGrantedStream、输入适配/原bridge与registry、成熟muxer/native/外部host和依赖未改。[源码差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/source-differences.json)、[复核入口差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/tool-differences.json)。

## 实测与身份绑定

旧B05的null/空READY QUERY在旧准确源码及旧production JAR优先两路径重新复现；C01旧入口对其文档新根拒绝也重新实测，目标未创建。旧源/日志和失败不改写。[原失败证据](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/input03-reproduction/null-production.stdout)。

| 检查 | 最终源码 / production JAR优先结果 |
|---|---|
| 原20语义组、17尾段、tester23、九阶段63异常、输入5 | 两路径全部通过；B01–B04、A01/A02、首错/私有块/UNKNOWN、原registry/线程keeper门保持。 |
| 本批宿主返回88项 | 两路径通过：九阶段适用null/错类型/非法值、句柄/长度/摘要、状态-token、早ACK原尾段/晚坏结果、readonly authority和原task snapshot。 |
| 本批转换/授权33项 | 两路径通过：已知token替换、READY/ABORTED矛盾与WRITING倒退、COMMIT三态/null/抛错、coordinator防御、授权元数据、合法未知长度正例。 |
| 原两项QUERY安全回归 | 两路径通过；稳定协议首错、ready=false、owner保管、RPC各一次；准确原ABORTED authority出现后才收尾。 |
| tester新增独立风格检查复用 | 原authority3及私有cause取消6源码原样复用，两路径通过。新执行仍是coder回归，不冒称tester裁定。 |
| C01实际输出门 | `local_check`实际新根编译+20组通过；7类错误路径拒绝且未创建目标。统一runner也实际跑通全套两路径并验证同7类拒绝。两接口路径条件有意重叠，不相加冒充独立场景。 |

最终本地编译 **local-005**，完整源码 **suites-003**，production **suites-004**；每个原JVM实际返回、stdout/stderr、argv、source pins、JAR SHA和ORIGIN保留。全部有限gate与准确原线程实际join，最终source/output keeper0；默认UNKNOWN阶段仍实际持有，直到准确原authority与物理返回，不靠退出JVM伪清理。套件有意重叠，双路径和重复入口执行不增加不同场景数。

A02仍是physical10/ACK下界3/callerPos3；坏或晚取消WRITE可实际4而ACK下界0/callerPos0/UNKNOWN4，不推导实际0B，不回退、重发或退款。坏响应只说明协议/证明失败；原writer返回并不证明发布业务成功或回滚。

证据入口：[批次索引](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/batch-validation.json)、[返回值与原状态矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/return-value-matrix.json)、[既有字段范围及未定义项](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/host-return-boundary-map.json)、[原19项](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/independent-regression-map.json)、[生产原日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/suites-004/results.stdout)、[工具正反例](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/tool-output-gate/summary.json)、[统一命令实测](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/review-runner-gate/summary.json)。源码冻结前的工具自检明确标记CODER_SELF_CHECK，不是独立复核。冻结后只读入口的外置执行回执随负责人交接另提供，候选本身不再写入。

## 构建、依赖和历史保全

一次必要严格离线实际Android/Media3 ABI构建 **build-main-001成功**，33tasks全部executed。15runtime坐标、两锁、verification XML、实际JVM依赖与旧包逐字节一致；strict verification、verify-metadata=true、LockMode.STRICT，无新版本/pin/binary下载。实际296验证项=121binary/35module/140POM，175份metadata副本与原pin绑定。三依赖原有限离线身份/Apache许可准入保持，不扩大为release/平台/本新包独立放行。

INPUT_SINK03的629项及此前2349项，共 **2978旧冻结文件** 与六个原seal/各原ZIP逐项不变。旧失败、UNKNOWN和tester原证据保留。[构建记录](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/build-main-001/receipt.json)、[实际依赖](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/actual-consumption/summary.json)、[历史核验](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/frozen-baseline-preservation.json)。原deprecated提示保留原stderr，未冒称零提示。

## 冻结产物

| 文件 | 字节 | SHA256 |
|---|---:|---|
| [production JAR](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/artifacts/input-sink04-classes.jar) | 88583 | `f241f2f256f261f696f1713b164d17f6ffe68a692e2cf3702acf9eb881ce2e95` |
| [compile probe APK](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/artifacts/input-sink04-compile-probe-debug.apk) | 6305359 | `24c6fdbed294771268a103200b19e5a3a8a099002d16dc392fe8d86f8c2d305b` |

APK com.videokit.d1input/versionCode4/versionName D1-INPUT-SINK04/min31/target36，无权限、组件/native/test helpers，未安装。固定本地apksig/JDK验v2通过；证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。[产物审计](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/artifact-audit.json)。

[完整ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261021-INPUT-SINK04-source.zip)、[seal](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/input-sink04-freeze.json)记录全部交付身份，seal自身hash随负责人交接提供避免循环。排除镜像/Gradle缓存/JDK/SDK/build/classes，保留真实JVM依赖、实际metadata、源码、原失败/通过日志、矩阵、工具证据和产物。

## 不能从本批推导的结论

Status没有返回task/output/授权ID，CommitOutcome没有返回task/token字段；SDK以准确捕获的task参数、相同原端口对象和原authority绑定，不凭空增加nonce/协议字段。Provider/Handle没有物理FD/source身份字段；既有能力、长度、完整内容/顺序摘要检查不能证明同一物理FD。token没有密码学、编码或到期协议，不新造JWT/ASCII格式或任意新长度阈值。真实宿主诚实实现原证明、持久化业务账本、随机输出最终期望摘要等未独立证明，详见边界文档。

实际Android FD/fsync/codec/muxer、媒体容器/内容/timeline、真实宿主COMMIT/发布仍NOT_RUN。SDK/ADB/5037/设备/占用/旧handle查询0，无native/外部host构建，未生成或启用执行许可。历史P0/J11危险链、C13 FAIL、UNKNOWN、FFmpeg/release/model/media许可等未结项不减。

完整包冻结后交tester集中复审，不原地改单点、不自动下一批或M0。配套 [返回边界说明](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK04_RETURN_BOUNDARIES_V1.0.md) 与 [可执行独立入口](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK04_INDEPENDENT_CHECK_PLAN_V1.0.md)。
