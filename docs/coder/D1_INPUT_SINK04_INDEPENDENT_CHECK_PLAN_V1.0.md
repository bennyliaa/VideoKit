# INPUT_SINK04 可直接执行的整包复核入口 V1.0

候选D1-20261021-INPUT-SINK04，coder有限通过，新独立结论PENDING。先核完整seal/ZIP和旧2978项保全，再集中复核；不写冻结候选、不以运行coder绿色检查代替独立断言。D1未过、M0未启。

## 一条完整命令

下列PowerShell命令直接调用冻结工具，输出只能进入本批正确根内的新子目录。`independent-001`必须尚不存在；如已有结果，选该正确根内另一个新子目录，不能覆盖旧结果。

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1input-sink04\tools\review_all.py' --output 'D:\CodexProjects\VideoKit\docs\tester\D1_INPUT_SINK04_REVIEW_EVIDENCE\independent-001'
```

工具在冻结模式先逐项核seal文件字节/hash，再实际调用同一 `local_check.py --review-output` 入口，将源码/helper编译到输出目录的source/classes；随后依次执行源码和production JAR优先路径。保留每个原进程argv、exit、时间、stdout/stderr、JAR SHA、source pins与summary。只用已有JDK及候选固定真实deps，不用SDK/Gradle，不安装APK、不执行宿主真实COMMIT。

仅需核C01入口时可直接运行：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1input-sink04\tools\local_check.py' --review-output 'D:\CodexProjects\VideoKit\docs\tester\D1_INPUT_SINK04_REVIEW_EVIDENCE\independent-entry-001'
```

它实际编译源码和跑原20组；冻结时校验源pins。无需修改/复制脚本或临时去掉旧根断言。根由当前候选目录推导；旧03/02根、候选内部、伪前缀、越界/相对路径、根目录本身均拒绝，新目录不得复用。coder自检已实测两入口正例及同7种负例，失败路径未创建；冻结前自检明确记录unfrozen/CODER_SELF_CHECK。冻结后同入口的只读执行证据由交接消息另提供，不改包内文件。

## 集中复核重点

1. 原B05两输入：宿主原ABORT实际ABORTED，QUERY返回null或Status(READY,"")，默认authority UNKNOWN。应稳定协议首错、ready=false、owner未返，不能原始NPE/空tokenREADY/新RPC。准确同原ABORTED authority出现且原任务归还后可收尾，首错不清。
2. null/错类型/非法值在原消费前校验。WRITE invalid ACK不更新SDK字节下界/position、UNKNOWN一次；Void非null不假成功；reopen/validator既有句柄/长度/摘要/task/bytes/kind约束保持。
3. 统一READY/QUERY/readonly authority及coordinator状态-token判定。有效原token不能被替换，READY/ABORTED不能互相覆盖或倒退WRITING；合法UNKNOWN是缺证明，不能抹掉真实旧终态。坏响应可能已有副作用，不能用“校验失败”推出0B/已回滚或可释放。
4. 同原尾段/晚坏值/authority暂不可用、首次错误和timeoutsticky。COMMIT原ACK与准确业务outcome、writer/全部原任务返回分列；UNKNOWN不重发或退款。
5. 原B01–B04、A01/A02、20/17/23/63/5及19项矩阵；原authority3和私有cause取消6。每次实际gate/同原线程join，不能反射删keeper、退出JVM补绿。实际平台/业务发布NOT_RUN。
6. 结合 [既有返回边界](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK04_RETURN_BOUNDARIES_V1.0.md) 核字段缺失与不适用项：没有返回的task/output/授权/FD字段不能发明协议或冒称验证；token不透明，原端口真实性/持久化/物理FD身份仍需后续真实集成证明。

## 材料与加载身份

[交付报告](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK04_FIX_DELIVERY_V1.0.md)、[差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/evidence/source-differences.json)、[返回值矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/return-value-matrix.json)、[19项](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/independent-regression-map.json)、[原QUERY新安全断言](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/checks/com/videokit/d1input/QueryResultRegression.java)。旧失败原源码/原日志在reference与evidence/input03-reproduction，保留旧FAIL，不是新包PASS。

最终local-005、源码suites-003、production suites-004、严格构建001。生产JAR SHA256 `f241f2f256f261f696f1713b164d17f6ffe68a692e2cf3702acf9eb881ce2e95`；APK `24c6fdbed294771268a103200b19e5a3a8a099002d16dc392fe8d86f8c2d305b`。production classpath必须以该JAR首位，其后外置helper/classes和真实deps；核实际ORIGIN，不能让源码类遮住生产类。JVM URI/errno/WorkerRule为明确平台端口，Media3接口为真实1.9.3；受控4B文件/validator/authority不是实际容器效果。

独立审查应另加自己的故障注入和断言，不能仅采用coder计数。整批一份报告统一回负责人；新候选冻结后不原地补单点，不自动下一批/M0。禁止设备/SDK/ADB/5037/占用/旧handle、并发Gradle/native/外部host构建或真实宿主发布；本交接无执行许可，全部历史P0/UNKNOWN/许可未结项保留。
