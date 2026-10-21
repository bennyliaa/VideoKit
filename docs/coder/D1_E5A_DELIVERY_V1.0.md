# D1 E5A 完整交付 V1.0

2026-10-17。D1-20261017-E5A / docs/coder/d1e5a。仅本机关键路径与离线构建通过，等待独立复审。Android/设备/真实媒体/恢复QUERY/ABORT/最终观察均NOT_RUN；没有安装、下载或新fault。D1未通过、M0未启动、全部P0/JNI和旧signal/N2 FAIL保留。

## 批次与结果

按 [E5A集中需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E5A_CODER_REQUIREMENTS_V1.0.md) 修 [E5独立复审](D:/CodexProjects/VideoKit/docs/tester/D1_E5_ARCHITECTURE_REVIEW_REPORT_V1.0.md) 的F01/P1、F02/P1。新候选封存；旧E5及旧候选/工具/报告/设备现场只读。提交的是完整两项修复、集中证据和可审下一阶段计划，不将本机通过外推Android。

F01：原稳定N2预算永久要求本进程真实操作的活准入证明，完成文件/归档存在不提供正向许可。新host默认拒绝，即使恢复标记条目都缺失仍不能凭原预算身份追加R。完全实际返回的原恢复可仅在本进程准入；跨host需另正式派发独立最终观察，核确切恢复writer身份与实际死亡，重核原ABORT/S/保留产物，执行本次独立force/读回/实际关闭及目录同步，全部返回后才发本进程证明。旧force/close未知和旧FAIL不回填成功；不递归增加最后自证文件。

F02：生产Session接入统一E5ALifecycle。失败初轮返回后同原owner至多一次排队接续，不先完成Future；真实source/codec/Image/mux/FD/callback/CONTROL/预算归还且最后owner回调返回，或首次取消30秒绝对截止，才允许仪器结束。截止仍未知报告PENDING而不扣在途、不清账；首错保留、失败不改READY。正向、negative、cancel、await超时/异常、资源close及JUnit @After共用终局门。向外Future视图被取消不影响内部终局。

## 集中本机证据

最终JVM repair-006：Core89＋E5主路径48＋旧close未知3＋旧早期durability未知2＋E5A128＝270项顶层/既有断言。E5A父检查含子进程退出/结果核验；子JVM内部断言另保日志，不再叠加求数量。八个晚期场景为正常全返以及completion force异常、close异常/未返、最终dir force异常/未返、dir close异常/未返。完成内容均确实完整可见；全新JVM直接生产reserve均拒绝且无新R；未返时原真实FileChannel仍open、原operation强引用。实际writer退出后另做独立新观察、当前文件force/close，才可当前进程reserve。OS退出不被计为旧closeACK或旧操作成功。

生命周期用真正单线程owner队列、原FileChannel关闭、原E4ReturnGate和生产E4OutputBudget结算，虚拟单调时钟只驱动60/30秒事件。覆盖初轮PENDING后原窗口内迟到返回、绝对截止仍UNKNOWN、原CONTROL迟到、计时任务调度迟到、取消外部Future视图、真实中断等待线程。初轮不会先结束仪器；原S唯一，原首错不变；截止后受控归还不升级原PENDING；延迟派发截止事件也不能准入迟到完成。Android Handler/Binder/目录fsync/native未执行。共享E5ADirectoryBarrier在本机以自有文件FD代替Android目录FD，仅证明所有权/异常/返回分支，不声称Windows证明Android持久化或掉电保证。

本机main/repair-001/002/003通过；repair-004因同host拒绝优先级变更而旧断言预期不符失败，原日志保留；repair-005仅修此预期后通过，cold-host严格拒绝检查保持；绝对截止调度迟到资格补强后repair-006通过。最终Gradle main-001成功，稳定预算准入补强后的repair-001再次离线成功，绝对截止资格补强后repair-002最终通过，采用最后一次源码与APK；原main输入/成功结果完整保留。未并发Gradle。

[最终JVM结果与输入](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/local-check-results.json)；[最终离线构建](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/build-results.json)；[构建沿革](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/build-input-lineage.json)；[最终build输入](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/final-build-inputs.json)，SHA256 `10d7f7eb36b2c685620b2f214148d1bdc9ec4c0ff4b1b41bcd1402d1be8cb76d`。

## 精确双APK

| 角色 | 字节 | SHA-256 | 文件 |
|---|---:|---|---|
| app-debug | 10726780 | `d490b9abcbc5f47074ff2e20e8163f26ab0c200b452a8c187524a6caf98eca33` | [APK](D:/CodexProjects/VideoKit/docs/coder/d1e5a/artifacts/D1-20261017-E5A/final/app-debug.apk) |
| androidTest | 2757370 | `4b088c49ce864d029555c664208b60bb0a04fdaf19d095a7465b3a98b3ce324e` | [APK](D:/CodexProjects/VideoKit/docs/coder/d1e5a/artifacts/D1-20261017-E5A/final/app-debug-androidTest.apk) |

两包证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，与E5/E4A一致；com.videokit.app / test、versionCode3/D1-E5A、两个非导出服务和原权限保持，无INTERNET/companion。[原签名/Manifest/七native审计](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/apk-audit.json)。真实六帧、普通isolated EOF/PTS/缩略图复核、E5 flags/STARTED实际ACK/阶段诊断保持；同UID codec只是故障边界。

## 来源、依赖与封存

Media3 1.9.3 / FFmpeg 8.0.3，35个Maven坐标、七native字节与E5/E4A差异0，无新依赖。完整C14对应native源码容器、NOTICE和许可映射保留；非漏洞/许可/发布放行。[SBOM](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/sbom.json)、[差异](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/sbom-difference.json)、[E5衍生关系](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/source-derivation.json)、[C14映射](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/upstream-copy-map.json)。

[完整源码ZIP](D:/CodexProjects/VideoKit/docs/coder/d1e5a/artifacts/D1-20261017-E5A/D1-20261017-E5A-source.zip) 收入全部候选源码、工具、原日志和自有模型文件、四文档、基线证据与完整C14对应源码容器；排除local.properties、私钥、build/classes/Gradle缓存、真实媒体。双APK独立列为immutable。[外部freeze](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/e5a-freeze.json) 绑定ZIP/manifest/逐文件及双APK。ZIP大小/SHA与freeze自身SHA由集中交接外给，避免自身ZIP哈希循环。只读核验：Python -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1e5a/tools/e5_package.py verify。

旧E5 452、E4A207、T6 54、MPREP165共878个immutable只读验证，原seal一致。[旧冻结只读结果](D:/CodexProjects/VideoKit/docs/coder/d1e5a/evidence/external-readonly-verification.json)。原fixture/设备缓存/预算/失败产物未改。下一顺序仍为正式部署QUERY→独立审阅→另派原ABORT→独立结算审查→准确正常四方法；每个新host还必须执行明确派发的本次最终观察，静态报告或旧观察不自动授权。
