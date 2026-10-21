# D1 E6B 独立静态复审报告 V1.0

日期：2026-10-17。Tester。依据 `docs/milestones/D1_E6B_TESTER_REQUIREMENTS_V1.0.md`，审查完整冻结候选 D1-20261017-E6B、四文档及已有证据。

## 结论

**SUPPORTED_FOR_FORMAL_NORMAL_REGRESSION。E6A-F01/P2 在静态及已有直接公开边界证据范围关闭，未发现新增问题。** 原 E6-F01/F03 已支持范围保持，E6-F02 的公开预检剩余缺口已补齐。支持负责人另行正式派发精确 E6B 正常回归，不以本报告自动开始设备测试。

关闭依据是实际公开入口 catch、原 Throwable/cause 保留、准确 TIMELINE/NOT_CREATED/NOT_STARTED 和直接公开入口的有限负例；不是 Android 实机关闭。E5C-REG-F01/P1 仍待新包正常 MP4 完整 READY，原 FAIL、原 N2 无帧原因 UNKNOWN/close ACK=false 不改。D1 NOT_PASSED、M0 NOT_STARTED，全 P0/框架许可及既定未完成项保留。

本轮 Tester ADB/设备/安装 0，原媒体及导出件读取 0 字节，Gradle/native/Java 模型重跑 0；仅执行读取文件的独立身份及证据核验。无在途设备任务，不改 coder 冻结、旧测试报告或账本。

## E6A-F01 修复及直接公开边界审查

实际生产差异只在 `android/com/videokit/spike/c14/E4CpuAdapter.java` 的公开 `validate(Context,...)`：

1. 原 offMain 保持；随后原 PipelineRules.timeline 调用单独 catch(Exception|Error)。捕获变量 failure 原样传入既有 E6AFailure，不重建原异常。
2. 明确 VALIDATOR、mode11、TIMELINE、NOT_CREATED；既有 safe 输出 start=NOT_STARTED，snapshot null/background NOT_COLLECTED、cleanup 空。没有构造 task 或补零 native 数据。
3. catch 位于 TrackedProvider/CpuTaskClient 创建之前；错误立即携出，资源创建不因取 task 而提前。
4. 合法时间线仍沿原创建边界；公开入口其余部分及内部 owned 验证、后置 digest/receipt/content/thumbnail、stop/close、保留未归还 owner 的工作流保持原字节。
5. 既有 session 路由不变：validatorEnter 的 UNKNOWN 收到 E6AFailure 后改为已知未启动状态，source 字段不受影响；实际在途 UNKNOWN 不被猜测为启动成功。

对全部运行 Java 源做独立逐文件比较，唯一变化为该 adapter；对整个 adapter 作精确替换等式及内部 owned 后缀比较，证实只有上述 catch 差异。测试源码、E6ADiagnosticState/E6AFailure/接收器、原首份并发发布、源及验证器成功/失败字段均未改变。

核验 `tools/E6BPublicPreflightSelfCheck.java`、四个工具 shim、输入清单、命令/退出码及 public-compile-001/public-run-001 原日志。记录为 **6 用例、59 断言**：

| 已有直接公开入口用例 | 核验内容 |
|---|---|
| NULL、LENGTH、FIRST_NONZERO、NON_MONOTONIC、OUT_OF_WINDOW 五负例 | 实际调用公开 Context 重载，真实 PipelineRules.timeline 抛错；primary 与 cause 同一对象，原 IOException 类型/code 和首 stack throw-site 保持；scope/mode/phase/task/start 准确、无 snapshot/cleanup；实际路由从 UNKNOWN 改为 NOT_STARTED，source 仍 NOT_STARTED；每例 Binder 创建 tripwire/context/source open/digest 均为 0。 |
| VALID_TIMELINE_REACHES_REAL_CPU_CREATION 校准 | 同公开入口合法预检抵达原 CpuTaskClient 创建点；工具 Binder 构造 tripwire 恰好一次抛预先持有 sentinel，既有 CREATE 包装保留同一 sentinel/cause。证明合法预检没有被提前拒绝，不证明业务验证成功，也不声称合法路径创建 0。 |

没有用内部 ValidationOwner 重载替代公开入口。异常身份由生产 catch 原样传递的源码及原日志内身份/throw-site 断言共同支持，未将另外执行一次规则产生的异常误当同一对象。

这些检查使用 Context/Looper/Log/Binder 平台 shim；Binder 其他方法禁止执行，未模拟真实系统调用成功。坏输入创建 0 是本机 tripwire/计数器与源码顺序的有限证据，不作真实 Android 服务、FD、slot、death 或 owner 归还事实。支持类来自冻结 E6A，变更 adapter 和列明纯规则从 E6B 输入重新编译。Tester 未重跑；原 E6A 20/112 及更旧套件只继承，不累计为本批新通过数量。

## 冻结、最终构建和身份

独立核验脚本 `docs/tester/D1_E6B_EVIDENCE/audit.py`，结果 `identity-and-recorded-static-audit.json`：PASS。仅读取源码、包、元数据和既有日志，无候选代码或模型执行。

| 项目 | 核验结果 |
|---|---|
| 包外 seal | SHA-256 `21ef22f4e92535a0d4e50703d87ff46849c4228f5a20dd6f9721c31c87dddc33` |
| 源码 ZIP | 18,514,431 字节；SHA-256 `53f34d525db0bf14b4ac22eb2fc75d27b231842d9749787d7ea48ad481be81a2`；187 个有序唯一成员逐项大小/hash 一致 |
| 冻结文件 | 191 项大小/hash 全一致；原 E6A 外 seal 和 228 项不可变文件仍一致 |
| 最终构建输入 | SHA-256 `35de0ac79c792f5a6c4f37937a4ee5166557fbcaa001e635110756d0c483fbce`；逐项大小/hash 一致；绑定唯一 main-001、offline/exit0/原 BUILD SUCCESSFUL 日志，无 repair |
| app-debug | 10,544,590 字节；SHA-256 `1930ff1cde30ab48adb184128c1313ac6a0ab6957ce425dfe4974c970a91a987` |
| androidTest | 2,718,669 字节；SHA-256 `ea3c95bc774204651bc8defc5084890694a192e8273e543ea37e040f6a9a9d69`；与 E6A 相同，无测试断言退化 |
| 应用身份 | 原 AppID com.videokit.app、versionCode8/versionName D1-E6B；源码及既有最终 badging 记录相符。只认 artifacts/D1-20261017-E6B/final 双 APK |
| 签名 | 两原签名核验记录均通过，证书 SHA-256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；本轮复核记录，不重跑签名工具 |
| 包内集成 | 最终 app/test DEX 均含 sourceNativeDiagnostic/validatorNativeDiagnostic；E6BPublicPreflightSelfCheck 和创建 tripwire 标记未入包 |

四文档、精确 diff、已有只读 verification 回执、来源/SBOM/NOTICE/原对应源容器与完整源码 ZIP 均已审。原签名、私有服务和接口授权边界保持。源码 ZIP 不以构建缓存、私钥或媒体作为必要来源。

## 继承与严格门

七 native 在 E6B APK、声明来源、原 E6A APK 中逐字节一致；原生源码/header/config 与原来源一致，本批 native 重建 0。35 Maven 坐标锁逐字节相同、native/坐标 delta 空，Media3 1.9.3/FFmpeg 8.0.3 及原白名单保持。原 NOTICE/对应来源保留，未产生新的许可或安全放行结论。

独立解析七 ELF PT_LOAD 对齐和 APK 内未压缩 native 文件偏移，静态 16KiB 条件通过；Android 16KiB/JNI 系统运行仍未测试。

E6Muxer、E4CodecSink、PipelineRules、guard/recovery/final observation/生命周期/预算相关代码及 owned 工作流保持。六源/六输入/六 samples/完整六输出、1000us、完整 EOF、thumbnail/content/mapping、真实资源返回、60s/首 cancel30s、协商12s/STARTED15s 等原门不放宽。原 E6 封装修复的既有回放支持只继承，不重读失败输出/回放媒体，不宣称新包正常编码已通过。

## 正常回归准入与停止边界

**支持正式派发 E6B：保数据部署精确同签名 final 双 APK → normalMp4SixRealFrames → normalAviSixRealFrames → capabilityDenialDoesNotOpenSource → 条件 cancelRejectsWrongEpochOversizeAndLateFrame。** 本报告本身不执行上述步骤。

计划限定 HA1Q6WXR/user0、原 UID10221/test10222、batch D1-E4A-E6B-NORMAL-TABLET-20261017、稳定 budget `730a73e1-50e1-4198-a515-047104f00e31`，原结算报告 SHA `5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962`。每次独立新 host 的 Before 仍实际执行原最终观察，不能仅凭旧 live proof 准入。不先部署 E6/E6A、不新 QUERY/ABORT/独立 OBSERVE、不重跑一次性 G01。

原 N2 已 ABORTED/0 字节并归档、后续失败产物已消费 53,651 字节的账本连续性沿原设备报告保持；本轮不读设备重新证明。不卸载/clear/降级/清账/换预算身份/删产物求通过。原无 pending 是上次设备事实，不冒充本次实时事实。

正常结果必须真实满足全部画面/时序/EOF/READY、独立验证器 mode11/task/phase 与完整 native 字段，以及源/CPU/codec/FD/slot/CONTROL/owner 归还、唯一 R/S/无 pending。mode10 源提取计数不可替代 mode11，native OK 不替代 Java/cleanup/全局成功，缺日志为 NOT_COLLECTED、不补零。

cancel 占位符 `<SHA256_OF_INDEPENDENTLY_REVIEWED_THIS_E6B_TWO_NORMAL_RESULT_REPORT>` 必须替换为本批同设备两个正常完整结果独立审证后的准确新报告 SHA；旧报告、交付及本静态报告 SHA 均不适用。任一 FAIL/BLOCKED/PENDING/UNKNOWN 或实际资源/身份/时限/预算缺证即停止保留，不自动重试、进入依赖后项或 M0。
