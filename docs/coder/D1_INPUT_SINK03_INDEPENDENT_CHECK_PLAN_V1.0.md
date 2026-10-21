# INPUT_SINK03 集中独立复核入口 V1.0

候选 D1-20261021-INPUT-SINK03；coder有限通过，tester独立PENDING；D1未过、M0未启。依据完整新seal/ZIP核身份后复核，不写冻结候选、不改旧FAIL/UNKNOWN，不中途按单个问题交测。

## 集中检查内容

1. B03首次及晚observe的直接CancellationException是否均准确消费一次；对外IOException稳定、无原私有cause/message；重复observe/abort不再抛同一原取消，不重RPC、不重复UNKNOWN。
2. WRITE确实进入、无有效字节ACK时ACK下界/caller position与physical事实分开。重点实际4而ACK下界0/callerPos0/UNKNOWN4，及原A02实际10/ACK3/callerPos3；私有块不被晚caller修改，先前timeout不清零。
3. 九阶段正常ACK、ExecutionException、直接取消、timeout后晚成功/晚失败/晚取消、调用内直接抛取消及原尾段/authority未知。不以63计数代替正确状态，注意不适用字节/COMMIT分支说明。
4. B04已进入ABORT/QUERY超时或失败首错立即sticky，晚ACK/准确ABORTED和实际owner返回不清历史；未进入QUERY的pending不误记失败。查看deadline超时已抛而晚ACK刚完成的判断，不能只看当前future状态。
5. COMMIT未知无ACK时原线程返回仍须保管；准确相同task/token原authority确认后才收敛。原宿主query的ACK早到而同原query尾段未返时不可释放。`commitAcknowledged`与业务`commitOutcome`不能混同；NOT_APPLIED不伪造SDK回滚/ABORTED。默认UNKNOWN accessor不可被用作通过证据。
6. 失败QUERY无终态证明时持有；可选terminal authority只能读取该原task准确事实，不得隐式发新RPC或依据取消推断。验证原ABORT/QUERY调用次数不增，已证明READY/ABORTED不被改写。
7. 保留B01/B02、原20组/17尾段/19项、tester23场景、原读回registry/close任务和输入取消/错误脱敏/释放检查。所有原gate和线程必须清理/join，未知业务资格不得反射删除或靠进程退出补绿。

## 可复用材料及加载方式

[完整交付](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK03_FIX_DELIVERY_V1.0.md)、[异常状态模型](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK03_EXCEPTION_MODEL_V1.0.md)、[阶段矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/phase-exception-matrix.json)、[原23场景对应](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/tester23-regression-map.json)、[原19项](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/independent-regression-map.json)、[差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/source-differences.json)。

`reference`保留旧完整报告、原检查源码及全部顶层原日志/回执；这些是历史复现证据，不代表新包通过。IndependentFixCheck的12项和ReadbackReturnCheck原样复制；原6阶段取消/晚取消/3历史检查的输入保留，新命名Regression类将“复现缺陷”断言替换成安全断言，补明确COMMIT原authority收敛与原线程返回检查。请独立评估测试端口，不仅运行coder自测就关闭问题。

独立输出用 `D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/` 新子目录。候选 `tools/local_check.py --review-output <新目录>` 可在外部新目录编译源码/helper并跑20组；使用已有 `D:/Android/Android Studio/jbr/bin`，无需SDK/Gradle。其余运行计划可只读复用 `tools/run_suites.py`：原17、tester12、读回1、取消6、晚取消1、历史3、输入5、矩阵63。候选run_suites在冻结后拒绝写入；tester需以外部新目录保存独立argv/输出/原进程退出回执。

每类都应执行准确源码和生产JAR优先两条路径。production classpath首项必须是 `artifacts/input-sink03-classes.jar`，随后才是新编译的helper/classes和实际deps；核ORIGIN，避免源码类遮住生产类。生产JAR SHA256 `f053ad930c2f5cdaadc60cfe9157d190212e1f0b2620d0f04631af06382d00ab`；APK SHA256 `aab5754708e29f58ed0c1452db71895bf655eb0e9c363020a985271636bd3a20`。

最终coder源码local-005、源码suites-004、生产suites-005、构建002。构建001已被最终源码的deadline修正取代，保留原日志和superseded身份；不能用001冒充最终构建。依赖/锁/metadata与旧包不变，实际296项/15runtime坐标；旧2349项保持。仅probe编译验签，未安装。

原输入bridge/registry和Android/Media3 ABI真实；仅JVM URI/errno/WorkerRule等平台端口是测试替身，无假Media3接口。平台FD/fsync/codec/muxer/容器/真实业务发布NOT_RUN，受控文件4B不是媒体。禁止SDK/ADB/5037/设备/占用/旧handle查询、并发Gradle、外部host/native构建或真实COMMIT；本交接不含执行许可。

请一次输出B03/B04及同类边界完整集中报告，保留旧INPUT_SINK01/02整包FAIL与本批既往有限通过，不能用依赖准入或正常分支覆盖新失败。所有历史P0/危险链/UNKNOWN/许可未结项不变，不自动下一批或M0。
