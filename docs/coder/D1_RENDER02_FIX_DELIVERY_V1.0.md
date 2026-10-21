# RENDER02 三项集中修复交付

2026-10-20；候选 `D1-20261020-RENDER02`；项目 VideoKit。本批是 RENDER02_FIX，三项一次交付，等待 tester 集中独立复审。**D1 未通过，M0 未启动；Android 真实画面、听音、设备故障场景全部 NOT_RUN。**

依据 [开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_RENDER02_FIX_CODER_REQUIREMENTS_V1.0.md) 和 tester 原报告（SHA256 `c92a0b89b49180fac2db74524dbf7e043cfda6c7ea984074b9b90fe13ba3aed8`）。RENDER01 的 477 个冻结文件及旧 ZIP 已核对未改；旧失败仍保留，不改写成通过。

## 三项结果

| 项目 | 本批完成与验证 | 未关闭的边界 |
|---|---|---|
| P1 META-PROV-01 | 获取官方固定 Guava parent 33.3.1-android 原 POM、HTTP 回执、同源 SHA1/MD5 与 asc；恢复 `verify-metadata=true` 和 strict；记录最终实际校验的 327 个产物（135 binary、38 module、154 POM），含插件 marker 和父/BOM；原 POM 正向通过，篡改副本被准确按 SHA256 拒绝 | 新来源证据不是历史批准；PGP 发布者身份未验证；是否足够准入由独立复审决定，当前 PENDING_TESTER_REVIEW |
| P2 R02 | 原 lockCanvas 晚返后，只有实际 drawBitmap 且原 post 返回才生成画面计数/receipt；清理 post 单列；已绘制后取消仍保留真实旧代回执。受控晚锁取消、绘制后取消、正常六帧、seek 后旧/新代、销毁后新 Surface 五组通过 | JVM 受控 Android 端口，不是 Android 实机效果证明 |
| P2 R03 | 新增同包非导出 Activity 的第五 instrumentation 方法：闲置等待明确 Listen 点击，从初始 audible 意图启动完整三秒生成 PCM；准备 5 秒、点击 15 秒、原归还观察 30 秒。原四入口仍自动静音 | 无人听音，实际听音 NOT_RUN；观察超时不证明原资源归还 |

源码见 [PlatformRenderer](D:/CodexProjects/VideoKit/docs/coder/d1render02/android/com/videokit/d1present/PlatformRenderer.java)、[WorkSession](D:/CodexProjects/VideoKit/docs/coder/d1render02/src/com/videokit/d1present/WorkSession.java)、[Activity](D:/CodexProjects/VideoKit/docs/coder/d1render02/android/com/videokit/d1present/PresentationActivity.java)、[手动窗口策略](D:/CodexProjects/VideoKit/docs/coder/d1render02/src/com/videokit/d1present/ManualListenWindow.java)、[五个测试入口](D:/CodexProjects/VideoKit/docs/coder/d1render02/app/src/androidTest/java/com/videokit/d1present/RenderDeviceTests.java)。

## 元数据来源和实际闭包

新证据来源为 [Maven Central 固定原始 POM](https://repo.maven.apache.org/maven2/com/google/guava/guava-parent/33.3.1-android/guava-parent-33.3.1-android.pom)：20632B，SHA256 `6e11986ea7250b51f847157e2dc937f32a306804dfce0007a5e81ddb9b95c579`。[原始来源回执](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/guava-official-source/source-receipt.json) 包含请求与最终 URL、时间、状态、响应头、原始校验材料及各自 hash。同源 SHA1/MD5 相关性已核，不把同源校验或保存 asc 说成独立发布者身份认证。唯一新增 pin 的 origin 明确写“NEW…independent admission PENDING”。未增加二进制、依赖版本、SDK、模型或媒体下载。

最终仓库仅本候选离线镜像，显式启用 Maven POM / Gradle module 描述，不使用远程 fallback；缓存中只有 module 的 Android plugin 仍可解析。Gradle 的 module 元数据会优先用于部分组件，因此**最终实际消费没有 Guava parent 33.3.1-android POM**；这不是“已经验证旧 parent 来源”的证据。其新 pin 和官方来源另外交审，受控 Maven POM 探针另外验证原 parent 通过、变更 parent 被拒绝。最终实际消费 192 个描述全部符合旧已有 pin；未消费 Foojay。静态审计全部仓库文件的数量不冒充实际消费数量。

[实际消费清单](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/actual-consumption/artifacts.json) 来自最终 strict 构建 005 的 Gradle 自身 Dependency verification operation（原始 progress 名称逐项绑定坐标/文件），不是遍历缓存猜测。附全部实际描述副本、71 条 POM parent/import-BOM 声明；声明边与实际 observed 另列，未解析的属性不虚构为实际依赖。[摘要](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/actual-consumption/summary.json)、[拒绝检查及准确期望/实际 hash](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/metadata-rejection-003/summary.json) 可供复审。

## 自测、构建和复用

旧版生产 renderer/core 在 tester 受控端口下复现 `drawn=1 / bitmapDraw=0 / post=1`；新回归为 `0 / 0 / 1`，原 source/线程/像素真实归还。绘制后取消为 `1 / 1 / 1`，回执 `currentAfterPost=false`，保留真实旧事件。[旧失败复现](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/review-baseline/run.stdout)、[六组新增回归](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/controlled-regression-001/run.stdout)、[九组原核心自测](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/local-001/core.stdout) 均直接绑定源码 hash。

必要构建和失败均保留：[构建记录](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/build-attempts.json)。001 本地 daemon 通信失败；002 默认 POM-only 解析未找到已有 module-only 插件；003 在新 Gradle home 严格离线全量构建通过（67 executed）；004 修正观察器以记录 verification progress 后 strict 重放通过；005 最终明确描述源配置 strict 重放通过（67 up-to-date）。未修改业务代码后反复求绿。独立拒绝探针初两次分别因 variant 选择和不相关缺失 checker-qual 而无效；003 限定原目标描述且关闭无关传递解析后，正向通过、负向明确 checksum mismatch。无效尝试一并保留。

35 个锁定组件与原 E13F/RENDER01 完全一致；其中 30 个有二进制证据、5 个是 metadata/variant alias，实际选择的二进制全部匹配冻结 hash。Guava 缓存证据中的未选择 JRE 变体单列，不冒称该变体被实际消费。[身份核对](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/runtime-35-actual-binary-identity.json)。7 个 native、PCM fixture、对应 C14 源码完全复用，native/fixture/host 均无重建。新 SBOM 修正继承的 CPU JNI 嵌套 E6 标签为实际 C14 身份；旧 SBOM 未改。CPU JNI SHA256 仍为 `ed02feb238b26ea2ac53b6ae2eafca3d3131d74ebfdfd52c39ff3a925648e9a7`，其余六个 native 与 E13F 一致。

## 产物身份

包 `com.videokit.d1present`，versionCode 2 / `D1-RENDER02`，min31/target36，仅 arm64-v8a；是独立空沙箱候选，不是旧 app 的更新或绕过禁用限制。Activity 仍非导出无 launcher，呈现在 `:presentation`，CPU 是普通 isolated `:d1_cpu_worker`，没有新增 INTERNET。

| 产物 | 字节 | SHA256 |
|---|---:|---|
| [app APK](D:/CodexProjects/VideoKit/docs/coder/d1render02/artifacts/app-debug.apk) | 10480388 | `2f6e1cf02d85d8b0bd32ca0c475aea9e182a8b3b55e17a6da066a6ddfc5e2d94` |
| [test APK](D:/CodexProjects/VideoKit/docs/coder/d1render02/artifacts/app-debug-androidTest.apk) | 2695613 | `88241afd1cfe50fee41be95d788d76948bdee24cec14a26329040f69970e63cb` |

同一 Debug 公钥证书 SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；官方已缓存 apksig 库经 JDK 验证两 APK 的 v2 签名，无 SDK 命令或私钥读取。7 native ZIP/ELF 静态 16KiB 对齐通过；不替代设备页大小验证。[产物审计](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/apk-audit/artifact-audit.json)。

## 移交与冻结

[完成矩阵](D:/CodexProjects/VideoKit/docs/coder/d1render02/completion-matrix.json)、[准确后续计划](D:/CodexProjects/VideoKit/docs/coder/D1_RENDER02_FIX_DEVICE_PLAN_V1.0.md)、[技术决定](D:/CodexProjects/VideoKit/docs/coder/D1_RENDER02_FIX_TECHNICAL_DECISIONS_V1.0.md)、[新 SBOM](D:/CodexProjects/VideoKit/docs/coder/d1render02/render02-sbom.cdx.json)、[冻结 seal](D:/CodexProjects/VideoKit/docs/coder/d1render02/evidence/render02-freeze.json)、[源码/证据/产物 ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261020-RENDER02-source.zip)。seal 绑定本报告、源码、全部回归证据、原始来源材料、实际消费描述、APK、ZIP；排除 417MB 离线镜像、构建缓存、工具运行时和私钥，另附完整输入 hash。保留失败日志，冻结后仅只读核对。

仍保持每 session 最多6帧/30秒、64MiB 像素、raw queue2/PCM queue4、PCM 576000B/三秒及原 owner/同代 source 强保管。原 canvas/API 不返、sticky unknown、原 Java 线程未返时不补偿归还、不 kill、不二次 close、不 finish。真实 RSS/BufferQueue/AudioServer、画面方向/截图、实际听音、焦点与完整危险链仍未证明。FFmpeg LGPL 全量对应源码/发布义务、模型与样本权利等原 OPEN/NOT_GRANTED 保持。无 M0、无新执行许可、无设备/SDK/ADB/5037/安装/占用查询或旧 handle 操作；等待负责人收件及 tester 集中复审。
