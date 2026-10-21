# D1 E5C 完整交付 V1.0

2026-10-17。候选 D1-20261017-E5C，版本5 / D1-E5C。已完成Debug隔离夹具入口、有限本机逻辑检查、集中离线构建及签名/清单/原生库核验。真实Android补验、原QUERY、完整观察和恢复均NOT_RUN。G01待实机证据及独立复审，D1 NOT_PASSED、M0 NOT_STARTED、全P0和历史signal FAIL不变。

## 最终双APK

| 角色 | 字节 | SHA-256 |
|---|---:|---|
| app-debug | 10527871 | `5b7992f1ec01f8782b59dd1508c6a47e3af4f2602ba428e1b65892724f73f464` |
| androidTest | 2743033 | `5101c8efa43fd4ab5944479c8bafa8934ab9c4a1a1318fd9c6eae4c5d3f0e36c` |

最终文件在 `D:/CodexProjects/VideoKit/docs/coder/d1e5c/artifacts/D1-20261017-E5C/final/`。双APK签名证书均 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，与原候选一致。App为com.videokit.app，测试包com.videokit.app.test，单APK产品布局及原两个私有服务保持，7个arm64原生库字节一致。ACCESS_NETWORK_STATE是既有依赖合并权限；无新增权限/INTERNET。

## 实现与验证

新增 `app/src/androidTest/java/com/videokit/spike/e4/E5CGuardFixtureTests.java` 与 E5CFixtureBounds.java。精确方法 isolatedOriginalInodeSymlinks，只使用files/e5c_guard_fixture_20261017_once；健康两锁及owner/lease真文件链接三例。生产类未改，按相对路径直接引用冻结E5B的src/android/C14及原测试源码；main/debug清单复制字节一致。私有方法声明类、private修饰及返回/参数签名精确固定；完整源码hash由最终输入、source-provenance和freeze约束，反射失败即停。

本机10项纯JVM边界/时限用例与9项源码约束PASS，详见evidence/local-check-results.json。它们不能替代Android symlink/flock/FD验证；未重跑旧270/82项历史套件。最终输入SHA `6af5f97db1f2e74ac35627fc3a46bc6b2b74037f495b422d3af522987827bd36`，最后成功构建repair-001绑定此输入。

首轮main-001编译成功，但APK清单审核发现overlay漏带E5B的Debug服务清单，故审核失败。已补入原文件，不修改生产逻辑；一次必要repair-001离线构建通过，最终审核PASS。首轮两APK保存在artifacts/D1-20261017-E5C/pre-debug-manifest-repair，原签名/清单/输入和失败说明在evidence/pre-debug-manifest-repair；两轮构建日志及build-results-before-repair-001.json保留。没有把首轮APK交作最终候选。

来源核验对原E5B seal及1561项不可变文件只读校验PASS。source-provenance同时核直接引用的生产、Android、原测试和C14来源，原main/debug复制与原字节一致。35个Maven坐标、Media3 1.9.3、FFmpeg8.0.3、7个原生库保持，无下载。完整C14对应源容器保留，未复制E5B旧自检树；不是许可证/漏洞放行结论。

## 交付与下一步

另附架构边界、剩余门、设备附录三文档，准确计划tools/device_plan.json。source-manifest逐件绑定完整小overlay、所需E5B源/native/NOTICE/完整C14对应源容器及证据；ZIP按原相对目录装入，解压后配置自身local.properties，可离线重建；不含私钥、缓存或实际媒体。外seal evidence/e5c-freeze.json另绑定ZIP、最终及首轮保留APK，seal自身hash在交接消息/包外只读核验回执中给出。

仅交负责人整包复审；审过再正式派同签名保数据更新→隔离补验→固定原N2只读QUERY。所有执行动作未启动，新计划不是执行许可。原N2预算、R2MiB、pending及旧失败现场保持；任何失败不自动ABORT/观察/产品方法。
