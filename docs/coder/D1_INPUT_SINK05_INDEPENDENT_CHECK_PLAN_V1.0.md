# INPUT_SINK05 集中独立复核入口 V1.0

候选D1-20261021-INPUT-SINK05；coder有限通过，新独立PENDING。先核完整seal/ZIP及旧3683项保全，不写冻结候选。D1未过、M0未启；不是平台/真实发布验收。

## 可直接运行

使用本批正确根内的新子目录；下例independent-001应尚不存在，若已有结果另取同根新名，不覆盖：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1input-sink05\tools\review_all.py' --output 'D:\CodexProjects\VideoKit\docs\tester\D1_INPUT_SINK05_REVIEW_EVIDENCE\independent-001'
```

冻结工具先核全部seal身份，实际调用相同local_check --review-output入口，再跑源码及production JAR优先。仅已有JDK和固定真实deps，无SDK/Gradle/安装/真实COMMIT。argv、时间/exit、stdout/stderr、原source pins、JAR SHA/ORIGIN、summary均外置，50条顶层入口/套件回执（编译/源码20组另有子回执），不能据运行结果自动作独立PASS。

仅测外置入口可运行：

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1input-sink05\tools\local_check.py' --review-output 'D:\CodexProjects\VideoKit\docs\tester\D1_INPUT_SINK05_REVIEW_EVIDENCE\independent-entry-001'
```

根从当前候选推导，旧04/03根、候选内、伪前缀、遍历/相对、根本身及复用目录拒绝。两入口正例与同7类负例已实际运行，无临时复制脚本/去掉断言绕行。冻结前自检明确CODER_SELF_CHECK，冻结后的只读外置执行回执随交接另给，包内不改。coder自检目录与独立tester目录分开。

## 独立重点

1. B06：原READY方法已返、同一原response仍pending；原ABORT/准确QUERY已确认ABORTED后，原READY stage给出形状合法迟到token。须记录raw响应到达/成功而拒绝其采纳，保留ABORTED/首错/冲突UNKNOWN，不ready+aborted并存、不新RPC。缺准确兼容authority继续保管。
2. B07：真实宿主已READY，原ACK尚在同一stage；原QUERY确认同tokenREADY。finish应稳定OUTPUT_ORIGINAL_PENDING或既有pending返回，无内部IllegalStateException；同原正确ACK及真实observer/executor/thread返回后才收敛，不能忽略原回调或cancel补绿。
3. 检查所有首次/晚ACK、等待结果、QUERY、readonly来源的共享不可逆门。已知token不能替换，终态不能互相覆盖/倒退；匹配ACK或派生缓存不能擦另一来源冲突。原响应事实与采用结果分栏，不抹原动作或凭ACK猜回滚。
4. 自选有限关键先后顺序：ACK先于QUERY响应、ABORT ACK延迟、readonly仲裁先、坏authority再到同/异token或失败/取消ACK、原observer/worker/host物理尾段。查看准确stage引用、首错、UNKNOWN、keeper和剩余RPC，不仅引用30/7计数；本批不声称数学全协议证明。
5. 特别独立注入outstanding=0但同一个真实observer/worker仍被gate保留，核稳定pending和最终同一线程join。外部客户端线程可以在observer返回后继续活着；SDK-owned原线程必须终止，拥有host任务尾段的线程须由原authority保留。
6. 原B01–B05/A01A02、19项、20/17/23/63/5、88/33、原QUERY2、authority3/private-cause取消6、tester host8保持。实际gate都要释放并真实join；不反射改SDK、不造authority结果、不以JVM退出算归还。

## 材料与准确路径

[交付](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK05_FIX_DELIVERY_V1.0.md)、[顺序模型](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK05_RESPONSE_ORDER_MODEL_V1.0.md)、[差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/source-differences.json)、[30项/原观察](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/response-order-matrix.json)、[原两项新安全断言](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/checks/com/videokit/d1input/OriginalResponseRegression.java)、[coordinator零计数尾段](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/checks/com/videokit/d1input/CoordinatorOrderCheck.java)。旧原两场景源码/JAR复现在evidence/input04-reproduction；原tester源码/报告/失败在reference，旧FAIL保留。

初版新增测试在gate释放后错误假定worker立即完成，稳定pending落入测试cleanup而exit1，准确初版源码/原日志保留。仅调整测试为有限等待相同原响应和实际join，不改产品门；初版进程退出不当归还证明，最终有效两路径真实清理。请与正式有效结果分栏。

最终local-005、源码suites-004、production suites-005、严格构建001。JAR SHA256 `6fbf307a4f0a06f45606ad9a162fcad95330924c2f220b5f68cec1e851916b0b`；APK `0b5fc8d530c8159c9283d670472255b883d97ad3885e2bae8fd427d25c1148b7`。production classpath首项须此JAR，其后外置helper/classes和真实deps；核ORIGIN避免源码遮住产物。JVM URI/errno/WorkerRule是明确平台端口，Media3接口是真实1.9.3，无假接口。

请另做独立顺序注入/断言，不只运行coder绿色套件。准确host/CompletionStage契约、Status等未定义返回身份、物理FD/密码学token/真实账本仍未证明；不新增协议或扩大发行准入。原三依赖有限离线身份/许可保持。

整批一份集中报告回负责人，不逐点修改冻结包，不自动下一批/M0。SDK/ADB/5037/设备/占用/旧handle、并发Gradle/native/外部host/真实发布禁止；所有历史P0/危险链/UNKNOWN/许可未结项不减，实际FD/fsync/codec/muxer/媒体容器/业务COMMIT仍NOT_RUN。本交接无执行许可。
