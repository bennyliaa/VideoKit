# D1 E5C 设备执行附录 V1.0

2026-10-17。供负责人复审后正式派发；本次coder设备调用0。唯一准确机器计划 `D:/CodexProjects/VideoKit/docs/coder/d1e5c/tools/device_plan.json`，记录最终双APK完整SHA、证书和逐步argv；`argvAfterBoundAdbSerial`仅是待执行参数，需正式派发绑定原平板serial，不能自动选任意设备。禁止Gradle/媒体/设备并发。

## 单批顺序

1. 先独立核外freeze/ZIP/源/最终双APK/原证书和原app身份。用相同签名执行保数据更新app及test包（install -r），不用卸载、clear、降级或新UID。版本5、原UID10221不符即停。
2. 精确选一个方法 `com.videokit.spike.e4.E5CGuardFixtureTests#isolatedOriginalInodeSymlinks`，runner `com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner`。参数e5cCase=isolatedOriginalInodeSymlinks，e5cBatch=D1-E5C-GUARD-LINK-TABLET-20261017，e5cRun=FORMAL_DEBUG_FIXTURE_ONLY。固定root files/e5c_guard_fixture_20261017_once，不接受caller传路径；本方法不执行原QUERY/ABORT。
3. 必须看到健康两锁真实close、owner/lease两份真链接S_IFLNK/readlink/同原inode/长度/SHA、实际ELOOP、原生产role拒绝、无修改/R/S/grant、每个实际FD与原holder CLOSED，最后E5C_LOCK_BOUNDARY_PASS及仪器方法PASS。原生产负例在open前拒绝的FD标NONE_PREOPEN_REJECTION，不能当实际已分配FD close。所有证据需独立复核；方法PASS不等于正式G01审查通过。
4. 同一正式派发整批中，仅在第3步完全PASS且所有原调用返回时，另起instrumentation精确执行 `com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort`，显式e5N2Action=QUERY、e5N2Task=86cafdb3-0fc4-447d-920b-b19c884bf494、e5N2Budget=730a73e1-50e1-4198-a515-047104f00e31、e5RecoveryBatch=D1-E5B-N2-RECOVERY-20261017。保持原恢复batch，无e5aSettlementReceiptSha256参数。只读旧狭义原路径；原QUERY入口源码字节保持。QUERY_ELIGIBLE/originalCloseACK=false/retainedOperations=0及系统证据独立归档，不把fixture合成死亡当原writer证据。

## 预算与停止

夹具最多64节点/256KiB数据/单文件64KiB，日志4MiB（实现64事件各4096字符更紧），原方法时钟60s，3例1次。已有root直接BLOCKED，不扫描既有root、不删、不重命名、不换root重跑。任何FAIL/BLOCKED/PENDING/UNKNOWN/超时/runner或传输不明确均停止，QUERY标NOT_RUN。原线程/实际调用未返回不以外部cancel/kill/force-stop/系统仪器结束冒充close；保留原现场，等待独立判断。日志限额达到也FAIL，不截断拼PASS。

部署、fixture和QUERY分别写结果，夹具PASS仅证明生产观察锁边界；QUERY失败不抹去夹具证据，亦不触发ABORT/observe/正常产品方法。恢复动作必须将本批完整证据交审后再单独派发。原媒体、预置fixture、原budget/R2MiB/pending、原N2身份/epoch/lease、原失败保持，不新建预算替代。

## 审阅入口及本机复核

先读另外三份D1_E5C文档，再核source-provenance/local-check-results/build-results/apk-audit/sbom-difference/external-readonly-verification。包外回执核外seal自身hash，`tools/e5c_package.py verify`只读复核所有immutable和ZIP成员/字节/最终输入；其检查不是设备授权。解压源码ZIP保留docs/coder/d1e5c及所需d1e5b相对布局，配置自己的SDK路径后用既有Gradle/JDK离线构建，不导入任何签名私钥/缓存；若环境无既有依赖，不自动下载。
