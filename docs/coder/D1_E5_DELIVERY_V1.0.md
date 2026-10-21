# D1 E5 交付 V1.0

2026-10-17。候选 D1-20261017-E5，仅本机 JVM 与离线构建通过；Android/真实 codec/Binder/原 N2 恢复执行均 NOT_RUN。N2 原 FAIL 不回写；D1 未通过、M0 未启动、全部 P0/JNI 与旧 signal FAIL 保持。

## 本批结果与证据边界

需求为 [E5 集中需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E5_CODER_REQUIREMENTS_V1.0.md)。实现生产启动握手修复、有限阶段诊断、失败后原 owner 主动收尾、仅限 N2 身份的查询/合法 abort/fence/实际消费结算入口。真实六帧编码、隔离 CPU EOF/时间线/缩略图验证、Media3 1.9.3 与受限 FFmpeg 8.0.3 均保留。没有用 Fake 生成真实 READY。

已证源码问题：旧 host 用 flags==0 拒绝同步 Binder 的框架附加标志；诊断 CODEC_EVENT 从 codec owner 同步调用 host；host 在 STARTED callback 返回 ACK 前即可置就绪；旧 callback ACK 异常与仍在途混为永久 UNKNOWN；失败有限查询后缺少同原 owner 的主动接续。修复与证据详见架构文档。N2 原记录缺少具体 callback flags、ACK、codec 阶段，所以实际唯一根因仍 UNKNOWN，不宣称本批已治愈设备故障。

## 本机验证

最终 JVM repair-004：原协议/资源/旧代 Core 89 项，新增回调/能力/取消/恢复主路径 48 项，独立 close-unknown 子 JVM 3 项、durability-unknown 子 JVM 2 项，合计 142 断言。后两者各保留 1 个原操作至解释器结束；不把解释器退出计为资源归还，也不将模型 FileLock 认作 Android flock/Binder 验证。初次 main 与 repair-001 的模型失败日志保留，原因是 Windows 强制文件锁阻止重读；repair-002 改为本机模型的范围锁，生产完成凭据补强 repair-003 通过，归档与正常输出准入兼容修复后 repair-004 通过。并未改 Android 原 flock。

构建 main-001 被现有 Gradle 缓存写锁权限阻断；repair-001 得到公共 API O_DIRECTORY 不存在的编译错误；repair-002 改 O_RDONLY|O_NOFOLLOW 并 fstat 验目录后编译通过；repair-003 增补恢复查询原系统证据，repair-004 将恢复前像归档移入预算子目录，避免违反正常输出的纯文件清单，最终完成离线 assembleDebug、assembleDebugAndroidTest、debugRuntimeClasspath。未新增依赖、未下载、未安装/启动 APK。所有尝试原日志与失败输入快照保留。

[最终 JVM 输入与结果](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/local-check-results.json)；[离线构建结果](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/build-results.json)；[最终 build 输入](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/final-build-inputs.json)；[构建输入沿革](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/build-input-lineage.json)；[签名/Manifest/native 审计](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/apk-audit.json)。

## 精确安装包身份

| 角色 | 字节 | SHA-256 | 文件 |
|---|---:|---|---|
| app-debug | 10663736 | `05d382960573399c6cba78302171f9c058ac9df599b63268d59a6ab3f21d00f8` | [安装包](D:/CodexProjects/VideoKit/docs/coder/d1e5/artifacts/D1-20261017-E5/final/app-debug.apk) |
| androidTest | 2753602 | `d93ad2de80ed7b523258cdb7005d97010f8d6950b43a6f9dade9e46f2dddbcc5` | [安装包](D:/CodexProjects/VideoKit/docs/coder/d1e5/artifacts/D1-20261017-E5/final/app-debug-androidTest.apk) |

两包签名证书 SHA-256：`5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，与原 E4A 一致。appId com.videokit.app（test 为 com.videokit.app.test），versionCode 2 / D1-E5，普通独立 CPU :d1_cpu_worker 与同 UID :e4_codec 两个非导出服务。无 INTERNET/companion APK。签名私钥未打包。

## 完整来源与冻结

[完整 E5 源码 ZIP](D:/CodexProjects/VideoKit/docs/coder/d1e5/artifacts/D1-20261017-E5/D1-20261017-E5-source.zip) 包含本候选源码、构建/检查工具、原始日志、小型自有假数据、四文档、基线映射与完整 C14 对应源码容器。排除本机 local.properties、密钥、Gradle/build/classes 缓存和真实媒体。双 APK 作为外部 immutable 项独立封存；ZIP 成员由 source-manifest 精确枚举，不递归解包历史对应源码容器。

[外部冻结清单](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/e5-freeze.json) 绑定源码 ZIP/manifest/每文件/双 APK；最终 ZIP 大小、SHA 与冻结文件 SHA 在集中交接中给出，避免文档包含自身 ZIP 哈希形成循环。只读核验命令：Python -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1e5/tools/e5_package.py verify。该命令只核本地冻结，不执行设备、媒体或构建。

SBOM 35 个 Maven 坐标，E4A→E5 坐标差异 0，七个 native 字节差异 0。保完整 C14 native 对应源码与许可映射。此为精确继承审计，不是漏洞/许可放行。[SBOM](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/sbom.json)；[差异](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/sbom-difference.json)；[C14 复制映射](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/upstream-copy-map.json)；[E4A 衍生关系](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/source-derivation.json)。

E4A 207、T6 54、MPREP 165 个旧 immutable 项只读核验通过，各外部 seal 与原值一致；未改旧候选/报告/fixture/设备缓存/预算/失败产物。[旧冻结只读结果](D:/CodexProjects/VideoKit/docs/coder/d1e5/evidence/external-readonly-verification.json)。本批 coder 设备调用 0，真实媒体 stat/read/hash 0，新 fault 设备执行 0。

一次完整冻结交负责人审阅后才可正式交 tester；下一顺序为原 N2 处置准入→正常 MP4→正常 AVI→能力拒绝→条件取消。没有部分交接或本窗口执行许可。
