# D1 E7 交付 V1.0

2026-10-17。候选 D1-20261017-E7，versionCode9 / D1-E7。E6B-OBS-F01 保持 OPEN；本批交付实际生产死亡门的有界诊断、专用只读设备入口，以及明确停止在设计的持久协议。未声称长期新 host 准入已解决，未安排恢复写入或正常 AVI 重跑。

E6B_NORMAL 已独立审证平板 MP4：真实6源/6输入/6samples/isolated6、READY、PTS无漂移、双EOF、画面/缩略图、全部实际资源归还及唯一 S53567 通过，仅关闭 E5C-REG-F01 原平板 MP4 范围。AVI 新 host 在 Before WRITER_DEATH 阻断；能力与 cancel 未跑。原日志没有历史列表条数、匹配数或 reason，故具体淘汰/PID复用原因 UNKNOWN。

生产 requireRecoveryWriterDead 直接调用 E7WriterDeathGate；仍一次查询 max8，PID/UID/process/时间的匹配先计数，唯一且 reason>0 才查 /proc，只有 ENOENT 视为当前缺席。现在用查询前固定 now 作保守上限。错误码不放宽，观察/guard/fence/账本/文件 force 和实际 close/资源归还仍在原链路。新增报告有返回/匹配/各谓词拒绝数量、唯一匹配的 timestamp/reason/status、查询和 proc 实际状态；未查询/不可用用 NOT_COLLECTED，不补0。没有无关进程的身份/时间/错误正文。

持久死亡事实当前 DISABLED：旧 recovery.owner 只记 PID/UID/process/attempt/墙钟 began，没有 boot epoch 或 kernel process birth generation。已有成功日志无法补回可靠启动代次，也没有可证明的防回滚/篡改信任根；本批不实现持久文件格式、解析器、写入、迁移或 fallback。完整设计与风险矩阵见架构文档。每个新 host 仍必须通过当前原观察；历史成功文件不构成 live proof。

本地生产 gate 27 场景/316 断言通过；仅替换 Android history/proc port，直接调用同一生产谓词，未复制模型。测试不代表 Android API 实测。main-001 离线双 APK 一次构建成功（39秒，无修复/下载），原 guard/owner/观察/准入/资源/预算等10个关键文件逐字节保持。原 E6B 全191项只读复核通过。

- app-debug：`docs/coder/d1e7/artifacts/D1-20261017-E7/final/app-debug.apk`，10544590 B，SHA256 `f709314107a44ab71a6036e4e17c61a4d7ba2f67429c00be35b95775822b805b`。
- androidTest：`docs/coder/d1e7/artifacts/D1-20261017-E7/final/app-debug-androidTest.apk`，2724977 B，SHA256 `50437ade1e7eacf232da015dc88fc86aecd209d4cca68507a7e34540faed7567`。

两个 APK 证书 SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。单 app、2个原非导出服务、无 INTERNET；app/test DEX 分别核新生产 gate 和只读入口。APK zipalign -P16 静态通过，7个 native 与 E6B 完全一致，非16KiB设备实测。35 Maven坐标、FFmpeg8.0.3/Media3 1.9.3、原native对应源/配置/许可材料保持；全部许可P0未关闭。

准确输入快照 `evidence/final-build-inputs.json` SHA256 `e35aadf762b21cd7ce3f77f847ae88e1468c86f2fa696213c28927518feaa62b`，绑定 build-results 最终通过尝试。SBOM/diff/逐文件来源/日志均归档。完整源码 ZIP 及包外 seal 位于 artifacts/D1-20261017-E7 和 evidence/e7-freeze.json；它们的最终 SHA 由独立包外 `docs/coder/D1_E7_READONLY_VERIFICATION_V1.0.json` 给出，避免自指。ZIP 不含私钥/local.properties/classes/cache/真实媒体；包含继承的完整 native 对应源容器。

相对 E6B 的全部构建输入变化：

- `docs/coder/d1e7/android/com/videokit/spike/e4/E5N2RecoveryAndroid.java`
- `docs/coder/d1e7/app/build.gradle.kts`
- `docs/coder/d1e7/app/src/androidTest/java/com/videokit/spike/e4/E7WriterDeathDiagnosticTests.java`
- `docs/coder/d1e7/settings.gradle.kts`
- `docs/coder/d1e7/src/com/videokit/spike/e4/E7WriterDeathGate.java`

原稳定 budget 累计消费107218/reserved0、原N2归档/输出均按最后 tester 实证保留；本批没有设备访问，不能声称刚刚重新测得这些数。E3一次性许可已消耗不再复用。D1未过/M0未启，历史signal门与其余P0保持。本次无ADB/设备/媒体源/导出件/下载/新增恢复写操作。后续仅在独立静态复审及负责人正式派发后，执行附录的单个只读诊断；其结果也不是正常流程准入许可。
