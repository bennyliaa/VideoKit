# INPUT_SINK02 整包独立复核入口 V1.0

候选 D1-20261021-INPUT-SINK02。请在完整冻结 ZIP/seal 身份核对后检查，不对原冻结目录写入。coder结果仅有限离线自测，不代表独立通过。D1未过、M0未启。

## 优先检查

- B01：ACK到达但同原write线程仍活着时，finishWriter拒绝且flush/close都0、flushPhase=NOT_ADMITTED、firstFailure空；join相同原线程后合法flush1/close1。分别扩展FLUSH/CLOSE的ACK_PENDING、早ACK尾段、失败和UNKNOWN，确认不双调、不退款。
- B02：validator已返回receipt但同原validator线程活着，writer可为true，READY必须0、ownerReturned=false、retained=1。validator可由独立authority持有，不能仅让host总布尔值替它兜底。
- 显式COMMIT早ACK：committed=true与ownerReturned=false同时成立，未返retained=1；join同一原COMMIT线程后才能ownerReturned=true。超时晚ACK同理，firstFailure保留，不能伪回滚。
- REOPEN/READY对应分支：reopen ACK未返时不读回/验证，不二次reopen；READY ACK未返时不能进入COMMIT；准确同原归还后只复用原ACK，不发第二READY。
- ABORT/QUERY：ABORT尾段未返不准入QUERY；ABORT/QUERY已经实际调用后不得靠新调用补绿；query早ACK明确ABORTED也不能提前返owner。
- 同原SinkCoordinator原callback/executor/thread join、reopen原registry/worker返回，以及owner最终keeper0。未来计数完成/线程池terminated若不足以证明实际原线程死亡，不能判通过。
- A01/A02和原20组：A01跨factory/epoch/单源单读；A02实际10、ACK3、callerPos3、UNKNOWN、私有块和首错不回退；原19项逐项判定，S05仍保留NOT_RUN_PLATFORM。

## 可复用材料

[源码根](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/src/com/videokit/d1input/TemporaryOutput.java)、[原始差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/source-differences.json)、[原17场景代码](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/checks/com/videokit/d1input/ReturnBoundaryCheck.java)、[原20组](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/checks/com/videokit/d1input/InputSinkCheck.java)。

旧tester源码 `reference/IndependentBoundaryCheck.java` 原样保留，旧production JAR优先复现日志在 `evidence/old-five-scenarios`。新validator/commit端口显式要求原归还证明，因此原lambda不能原样编译；新 ReturnBoundaryCheck 的前五场景保持同样输入/安全边界，翻转旧“复现缺陷”断言，并把实际受控动作放入其原线程内。请独立查看断言及故障注入，勿仅运行coder测试即作独立结论。

独立输出请放 `D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/` 的新子目录。`tools/local_check.py --review-output <新目录>` 可输出20组编译/运行，避免修改冻结目录。17场景可用该次已编译helper，classpath必须以 `artifacts/input-sink02-classes.jar` 优先，其后checks/classes和实际deps；运行 `com.videokit.d1input.ReturnBoundaryCheck`。务必在独立receipt记录argv、原进程exit、原线程清理、JAR SHA、classpath origin，不能让源码编译classes遮住production JAR。

JDK为 `D:/Android/Android Studio/jbr/bin`；实际deps包含Media3 1.9.3与原Guava，测试仅提供android.net.Uri、errno/WorkerRule等JVM平台端口，无假Media3接口。原受控生成4B文件不是媒体容器。独立测试不得触发 Gradle 并发构建、SDK/ADB/5037/设备/旧handle/占用查询，不安装APK、不调用宿主真实COMMIT。

## 身份和结果边界

生产JAR SHA-256 `a98ec7f34139dcd08db611280256774af4a4897f20f8c3d2fa39beae87248bc0`；APK SHA-256 `25898fe613f845a1ba7dbbd5f5e4d85a7b0875b473099c06ba587eff6df3e08e`。完整ZIP与seal见 [交付报告](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK02_FIX_DELIVERY_V1.0.md)。

新包须给 B01/P2、B02/P1 与同类生命周期分支的集中独立结论，并保留历史INPUT_SINK01 FAIL；不能把旧依赖准入或旧A01/A02通过扩写成整个新包通过。实际AndroidFD/fsync/codec/muxer/媒体格式/真实业务发布均NOT_RUN；D1、M0和全部继承未结项状态不变。本交接不生成、转移或启用任何一次性执行许可。
