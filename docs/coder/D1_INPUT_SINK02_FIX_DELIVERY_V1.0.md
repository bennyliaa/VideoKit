# INPUT_SINK02 集中修复交付 V1.0

2026-10-21；候选 **D1-20261021-INPUT-SINK02**；范围 INPUT_SINK02_FIX。B02/P1、B01/P2 已集中修复并完成 coder 有限离线验证，整包冻结后交独立复核。**新候选独立结论仍待 tester；D1 NOT_PASSED，M0 NOT_STARTED。** 旧 INPUT_SINK01 的失败结论和原始失败证据保留。

依据 [正式要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK02_FIX_CODER_REQUIREMENTS_V1.0.md) 和 [阶段B报告](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md)，后者 SHA-256 为 `dc6271e9ed151e0779740c98a63e543830f5a506ea34d641d46ba8702a09c575`。

## 修复结果

**B01：未准入不消耗一次进入资格。** `flushAttempted`、`closeAttempted` 等标记在前序真实归还门通过、即将调用原动作时才改变。write 的 ACK 已到但同原线程尾段仍活着时，flush 和 close 都保持 NOT_ADMITTED；准确同原线程 join 后可合法继续，flush 一次、close 一次，firstFailure 保持空。已经实际调用、ACK_PENDING、调用是否发生 UNKNOWN、明确失败分别保留，不通过重试掩盖历史结果。

**B02：writer 归还与完整 owner 归还分开。** 除 writer 外，reopen、独立 validator、READY、显式 COMMIT、ABORT、QUERY、reopen 读回的原 registry/worker、原 SinkCoordinator callback/executor/thread 均纳入资格。validator 与 COMMIT 端口增加同原任务归还证明，Android authority 也必须证明其原宿主任务返回。无法证明、证明抛错或原任务未返均保留 owner，禁止 READY/COMMIT 等后继动作。

READY、COMMIT 的真实 ACK 是业务事实，不能当作资源归还证明，也不会因超时或尾段未返而抹掉。直接原 stage、返回值和同一 authority 被保留；READY/ABORT/QUERY 的缓存 view 只观察同一次原调用，不是替代执行或归还证明。COMMIT 前和最终释放前均等待原 coordinator 线程实际退出。

本批同时修复同类问题：reopen ACK 后不得越过原尾段读回/验证；READY 早 ACK 不得越过原尾段进入 COMMIT；ABORT/QUERY 不重复原宿主调用；write UNKNOWN 预算每个原调用只登记一次；公共修改操作串行准入，防止释放与显式 COMMIT 竞争；READY 后已释放的对象如获显式 COMMIT 请求，先重新取得原 owner 预算再调用。未新增 executor、资源 ledger、诊断框架或设备路径。

源码差异集中在 TemporaryOutput、HostOutput、AndroidGrantedStream、候选副本 SinkCoordinator；原20组测试 helper 只适配明确的 validator/commit 归还端口，新加原尾段检查。HostInputFactory、HostDataSource、其余输入/桥/registry、原成熟 muxer 绑定及依赖均未改。[差异清单与补丁](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/source-differences.json)。临时接口有源兼容变更，不代表 M0 公共 API 定版。

## 验证与证据

| 检查 | 本批结果与边界 |
|---|---|
| 原 tester 五场景 | 原 tester 源码及旧 production JAR 优先加载，重新复现 B01/B02；原日志永久保留。新检查按相同五场景的安全断言回归，并加强为实际原 host 动作线程和独立端口 authority；这是 coder 回归，未冒称 tester 独立复核。 |
| 原20语义组 | 最终 local-003 全过；构建 production JAR 优先加载的 production-core-001 再次20组全过。 |
| 原任务返回边界 | 最终 return-002（源码编译）及 return-003（production JAR 优先）各17场景通过。尾段在同一实际 host 动作线程内阻塞，日志保留相同 thread ID、isAlive、ACK、keeper、状态，最终均 join 同原线程、source/output keeper 为0。 |
| A01 | 同 Provider 跨 factory 限制、原 epoch 归还后新 range、alien URI 拒绝、单源单读/queue0 和双源预算保持。 |
| A02 | 先 ACK3，再实际写7后失败，总实际10；ACK 下界3、caller position3、UNKNOWN 保留，无重发/回退/退款。attempt/reservation 并非实际字节。 |
| 实际接口与严格构建 | build-main-001 一次必要构建成功，33 tasks executed。真实 Android/Media3 1.9.3 ABI；offline、strict verification、verify-metadata、LockMode.STRICT，不写锁。 |
| 依赖 | 15 runtime 坐标与旧包一致。实际验证296项：121 binary、35 module、140 POM；metadata XML 和两份锁逐字节不变；无新 pin、版本或 binary 下载。 |
| 历史保留 | 原 INPUT_SINK01 334项及此前1699项，共2033冻结文件逐项 SHA-256 一致；各原 seal 与 ZIP 均未改。 |

17场景包括 tester 原五场景语义，加独立 validator authority、FLUSH/CLOSE ACK尾段、REOPEN/READY早ACK、FLUSH/CLOSE/VALIDATE/READY/COMMIT超时后同原晚ACK、ABORT/QUERY尾段。受影响19项逐项保留旧判定并列新 coder 判定；S03/S06 为修复后有限本地通过待独立复核，S05 实际平台路径仍 NOT_RUN。

证据入口：

- [旧五场景复现](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/old-five-scenarios/reproduce.stdout)
- [production JAR 的17场景完整日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/return-003/run.stdout) 与 [运行身份](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/return-003/run.json)
- [production JAR 的20组日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/production-core-001/run.stdout)
- [逐阶段状态证据](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/original-phase-observations.json)、[19项映射](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/independent-regression-map.json)
- [构建记录](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/build-main-001/receipt.json)、[实际依赖验证](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/actual-consumption/summary.json)、[依赖许可差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/dependency-license-difference.json)
- [历史保留核对](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/frozen-baseline-preservation.json)、[最终源码/依赖身份](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/final-source-dependency-inputs.json)

原 datasource/database/exif 三依赖的本有限离线身份和许可准入沿用 tester 阶段B通过结论，旧官方 POM/module/Apache 证据保留于 reference 和 licenses；不扩大为设备、release 或新修复独立准入。原20组保留的 deprecated API 编译提示不是测试失败，原 stderr 原样留存。

## 交付身份

| 文件 | 字节 | SHA-256 |
|---|---:|---|
| [production classes JAR](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/artifacts/input-sink02-classes.jar) | 84773 | `a98ec7f34139dcd08db611280256774af4a4897f20f8c3d2fa39beae87248bc0` |
| [compile probe APK](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/artifacts/input-sink02-compile-probe-debug.apk) | 6300791 | `25898fe613f845a1ba7dbbd5f5e4d85a7b0875b473099c06ba587eff6df3e08e` |

APK 包名 `com.videokit.d1input`，versionCode2，versionName D1-INPUT-SINK02，min31/target36。无权限、组件或 native libraries，无测试 helper/platform ports；仅编译探针，未安装。用本地固定 apksig/JDK 公开验签 v2=true，证书 SHA-256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。[产物审计](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/artifact-audit.json)。

完整 [源码/证据 ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261021-INPUT-SINK02-source.zip) 和 [冻结 seal](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/input-sink02-freeze.json) 为最终入口；seal 记录所有交付文件及 ZIP 的字节、哈希。为避免循环哈希，seal 自身哈希在负责人交接消息中提供。ZIP 排除本地417MB镜像、Gradle缓存和编译中间目录，包含真实 JVM依赖、源码、完整实际 metadata、产物和原始证据。

## 未完成范围

实际 Android FD/fsync、codec/muxer、媒体容器验证、设备行为和真实宿主业务发布均 **NOT_RUN**。受控 validator/COMMIT、4B生成文件、生产 JAR/JVM 检查不能证明这些效果。SDK/ADB/5037/设备/占用/旧 handle 查询均0，未启 native/外部 host 构建，未产生执行许可。继承的 UNKNOWN/P0、危险链与 FFmpeg/release/model/media许可等未结项继续保留；本批不代表项目完成或正式产品交付。

下一步仅请负责人按整包派发 tester 离线独立复核 B01/B02、同类生命周期分支及冻结身份。修复源码不再原地变更；后续问题另建新候选。
